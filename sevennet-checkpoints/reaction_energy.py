#!/usr/bin/env python
"""SevenNet로 흡착 에너지·반응 에너지 계산 (오프라인, 체크포인트 경로 사용).

    dE = sum(coef * E(product)) - sum(coef * E(reactant))

흡착 에너지:   -r slab.vasp mol.xyz      -p slab_mol.vasp
반쪽반응 예:   -r slab_OH.vasp TEMAHf.xyz -p slab_Hf.vasp HNEtMe.xyz
계수:          "2*H2O.xyz" 처럼 coef*file

규칙
- 모든 항은 같은 체크포인트·같은 modal·같은 D3 설정으로 계산합니다(스크립트가 강제).
- 셀이 없는 분자 파일(xyz 등)은 --box 크기 정육면체 상자 가운데에 넣습니다.
- POSCAR의 Selective dynamics(F F F)는 ASE가 FixAtoms로 읽으므로 고정층이 유지됩니다.
"""
import argparse
import csv
import os
import re

import numpy as np
from ase.io import read, write
from ase.optimize import FIRE, BFGS

OPT = {"fire": FIRE, "bfgs": BFGS}


def parse_term(s):
    m = re.match(r"^\s*([0-9.]+)\s*\*\s*(.+)$", s)
    return (float(m.group(1)), m.group(2)) if m else (1.0, s)


def load(path, box):
    atoms = read(path)
    if atoms.cell.rank == 0 or np.allclose(atoms.cell.lengths(), 0):
        atoms.set_cell([box, box, box])
        atoms.center()
    atoms.pbc = True
    return atoms


def make_calc(args, modal):
    common = dict(model=args.ckpt, modal=modal, device=args.device,
                  enable_flash=args.flash, enable_cueq=args.cueq)
    if args.d3:
        from sevenn.calculator import SevenNetD3Calculator
        return SevenNetD3Calculator(damping_type="damp_bj",
                                    functional_name=args.d3_func, **common)
    from sevenn.calculator import SevenNetCalculator
    return SevenNetCalculator(**common)


def energy(path, calc, args, modal, cache):
    if path in cache:
        return cache[path]
    atoms = load(path, args.box)
    atoms.calc = calc
    if args.relax:
        tag = os.path.splitext(os.path.basename(path))[0]
        opt = OPT[args.optimizer](atoms, logfile=None)
        converged = opt.run(fmax=args.fmax, steps=args.steps)
        if not converged:
            print(f"  [경고] {path}: {args.steps} step 안에 fmax {args.fmax} 미수렴")
        os.makedirs(args.outdir, exist_ok=True)
        write(f"{args.outdir}/{tag}__{modal}.vasp", atoms, format="vasp",
              direct=True, sort=False)
    e = atoms.get_potential_energy()
    cache[path] = e
    return e


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ckpt", required=True, help="체크포인트 .pth 경로")
    ap.add_argument("--modal", nargs="+", default=["omat24", "mpa", "oc22"],
                    help="비교할 modal 목록 (기본: omat24 mpa oc22)")
    ap.add_argument("-r", "--reactants", nargs="+", required=True)
    ap.add_argument("-p", "--products", nargs="+", required=True)
    ap.add_argument("--relax", action="store_true", help="각 구조를 먼저 완화")
    ap.add_argument("--optimizer", choices=OPT, default="fire")
    ap.add_argument("--fmax", type=float, default=0.03)
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--box", type=float, default=20.0, help="분자 상자 크기 (Å)")
    ap.add_argument("--d3", action="store_true", help="D3(BJ) 추가 (CUDA 필요)")
    ap.add_argument("--d3-func", default="pbe")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--flash", action="store_true", help="FlashTP 사용 (설치된 경우)")
    ap.add_argument("--cueq", action="store_true", help="cuEquivariance 사용")
    ap.add_argument("--outdir", default="relaxed")
    ap.add_argument("--csv", default="reaction_energy.csv")
    args = ap.parse_args()

    R = [parse_term(s) for s in args.reactants]
    P = [parse_term(s) for s in args.products]
    rows = []
    for modal in args.modal:
        if args.d3 and modal.startswith("omol25"):
            print(f"  [주의] {modal}은 ωB97M-V(VV10 포함)라 D3를 더하면 분산이 이중 계산됩니다.")
        calc = make_calc(args, modal)
        cache = {}
        er = sum(c * energy(f, calc, args, modal, cache) for c, f in R)
        ep = sum(c * energy(f, calc, args, modal, cache) for c, f in P)
        de = ep - er
        print(f"[{modal:>12}] dE = {de:+.4f} eV")
        for f, e in cache.items():
            print(f"{'':16}{e:14.4f}  {f}")
        rows.append({"modal": modal, "dE_eV": f"{de:.5f}", "d3": args.d3,
                     **{os.path.basename(f): f"{e:.5f}" for f, e in cache.items()}})

    with open(args.csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"저장: {args.csv}")


if __name__ == "__main__":
    main()
