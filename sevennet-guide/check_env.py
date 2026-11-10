"""SevenNet 환경 검증 스크립트 (RTX PRO 6000 Blackwell 등).

실행:  python check_env.py [--model 7net-omni] [--modal mpa] [--natoms 2000]

확인 항목
  1. PyTorch가 sm_120 커널을 포함하는지, GPU가 인식되는지
  2. SevenNet + 각 가속기(cuEquivariance / FlashTP / OpenEquivariance / LunaTP) 사용 가능 여부
  3. 가속기를 켰을 때 에너지·힘이 e3nn 기본 경로와 일치하는지 (Blackwell 커널 오류 탐지)
  4. D3 (CUDA JIT 컴파일) 동작
  5. 큰 셀에서 1-step 시간과 GPU 최대 메모리
"""
import argparse
import time

import numpy as np


def hr(title):
    print(f"\n{'=' * 8} {title} {'=' * (60 - len(title))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="7net-omni")
    ap.add_argument("--modal", default="mpa", help="multi-task 모델이 아니면 'none'")
    ap.add_argument("--natoms", type=int, default=2000, help="속도·메모리 측정용 대략적 원자 수")
    args = ap.parse_args()
    modal = None if args.modal.lower() == "none" else args.modal

    # ------------------------------------------------------------ 1. torch
    hr("1. PyTorch / GPU")
    import torch

    print("torch", torch.__version__, "| CUDA runtime", torch.version.cuda)
    assert torch.cuda.is_available(), "CUDA 사용 불가"
    archs = torch.cuda.get_arch_list()
    cap = torch.cuda.get_device_capability(0)
    print("GPU:", torch.cuda.get_device_name(0), "| capability", cap)
    print("compiled archs:", archs)
    print("memory: %.1f GB" % (torch.cuda.get_device_properties(0).total_memory / 1e9))
    if cap == (12, 0) and "sm_120" not in archs:
        raise SystemExit("PyTorch에 sm_120 커널이 없습니다 → cu128 이상 휠로 재설치하세요.")

    # ------------------------------------------------------------ 2. accelerators
    hr("2. SevenNet / 가속기")
    import sevenn

    print("sevenn", getattr(sevenn, "__version__", "?"))
    avail = {}
    for name, mod, fn in [
        ("cueq", "sevenn.nn.cue_helper", "is_cue_available"),
        ("flash", "sevenn.nn.flash_helper", "is_flash_available"),
        ("oeq", "sevenn.nn.oeq_helper", "is_oeq_available"),
        ("lunatp", "sevenn.nn.lunatp_helper", "is_lunatp_available"),
    ]:
        try:
            m = __import__(mod, fromlist=[fn])
            avail[name] = bool(getattr(m, fn)())
        except Exception as e:  # noqa: BLE001
            avail[name] = False
            print(f"  {name}: import 실패 ({type(e).__name__}: {e})")
    for k, v in avail.items():
        print(f"  {k:7s}: {'사용 가능' if v else '-'}")

    # ------------------------------------------------------------ 3. consistency
    hr("3. 가속기 결과 일치 검사 (작은 HfO2 셀)")
    from ase.build import bulk
    from sevenn.calculator import SevenNetCalculator

    small = bulk("HfO2", "fluorite", a=5.1, cubic=True).repeat((2, 2, 2))
    small.rattle(0.05, seed=0)

    def evaluate(atoms, **kw):
        calc = SevenNetCalculator(model=args.model, modal=modal, **kw)
        a = atoms.copy()
        a.calc = calc
        return a.get_potential_energy(), a.get_forces()

    e_ref, f_ref = evaluate(small)
    print(f"  e3nn (기준)  E = {e_ref:.6f} eV")
    for k in ("cueq", "flash", "oeq", "lunatp"):
        if not avail[k]:
            continue
        try:
            e, f = evaluate(small, **{f"enable_{k}": True})
            de = abs(e - e_ref) / len(small) * 1000
            df = np.abs(f - f_ref).max() * 1000
            ok = de < 1.0 and df < 10.0
            print(f"  {k:7s} ΔE = {de:.3f} meV/atom, max|ΔF| = {df:.2f} meV/Å  -> {'OK' if ok else '확인 필요'}")
        except Exception as e:  # noqa: BLE001
            print(f"  {k:7s} 실패: {type(e).__name__}: {e}")

    # ------------------------------------------------------------ 4. D3
    hr("4. D3 (CUDA JIT)")
    try:
        from sevenn.calculator import D3Calculator

        a = small.copy()
        a.calc = D3Calculator(functional_name="pbe", damping_type="damp_bj")
        print(f"  D3 energy = {a.get_potential_energy():.6f} eV  -> OK")
    except Exception as e:  # noqa: BLE001
        print(f"  D3 실패: {type(e).__name__}: {e}")
        print("  → nvcc 12.8+ / CUDA_HOME / TORCH_CUDA_ARCH_LIST='12.0' 확인")

    # ------------------------------------------------------------ 5. speed / memory
    hr(f"5. 속도·메모리 (~{args.natoms} atoms)")
    n_rep = max(1, round((args.natoms / 12) ** (1 / 3)))
    big = bulk("HfO2", "fluorite", a=5.1, cubic=True).repeat((n_rep,) * 3)
    big.rattle(0.05, seed=1)
    best = next((k for k in ("cueq", "flash", "oeq") if avail[k]), None)
    configs = [("e3nn", {})] + ([(best, {f"enable_{best}": True})] if best else [])
    for label, kw in configs:
        try:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            calc = SevenNetCalculator(model=args.model, modal=modal, **kw)
            a = big.copy()
            a.calc = calc
            a.get_forces()  # warm-up (컴파일 포함)
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            for _ in range(3):
                a.positions += 1e-4
                a.get_forces()
            torch.cuda.synchronize()
            dt = (time.perf_counter() - t0) / 3
            mem = torch.cuda.max_memory_allocated() / 1e9
            print(f"  {label:6s} {len(a)} atoms: {dt * 1000:.1f} ms/step, peak {mem:.1f} GB")
        except Exception as e:  # noqa: BLE001
            print(f"  {label:6s} 실패: {type(e).__name__}: {e}")

    print("\n완료.")


if __name__ == "__main__":
    main()
