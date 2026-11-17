#!/usr/bin/env python
"""격리 서버에서 체크포인트가 제대로 반입됐는지 확인 (인터넷 불필요).

0) ckpt/*.partNN 조각을 .pth로 합침   1) SHA256SUMS와 해시 비교   2) 체크포인트 로드
3) H2O/Pt(111) 흡착 에너지를 modal별로 계산해 숫자가 나오는지 확인

    python verify_offline.py --dir ckpt
    python verify_offline.py --dir ckpt --install   # 키워드 경로에도 복사
"""
import argparse
import hashlib
import os
import shutil

from ase.build import add_adsorbate, fcc111, molecule

KEYWORD_DIR = {
    "checkpoint_sevennet_omni.pth": "SevenNet_omni",
    "checkpoint_sevennet_omni_i8.pth": "SevenNet_omni_i8",
    "checkpoint_sevennet_mf_ompa.pth": "SevenNet_MF_ompa",
}
TEST_MODALS = {
    "checkpoint_sevennet_omni.pth": ["omat24", "mpa", "oc20", "oc22"],
    "checkpoint_sevennet_omni_i8.pth": ["omat24", "oc22"],
    "checkpoint_sevennet_mf_ompa.pth": ["omat24", "mpa"],
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help=".pth와 SHA256SUMS가 있는 폴더")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--install", action="store_true",
                    help="sevenn/pretrained_potentials/ 아래에 복사해 '7net-omni' 키워드로도 쓰게 함")
    args = ap.parse_args()

    sums = {}
    with open(os.path.join(args.dir, "SHA256SUMS")) as f:
        for line in f:
            h, name = line.split()
            sums[name] = h

    # GitHub 100 MB 제한 때문에 나눠 둔 .partNN 조각을 합침
    import glob
    for name in sums:
        path = os.path.join(args.dir, name)
        parts = sorted(glob.glob(path + ".part*"))
        if parts and not os.path.exists(path):
            with open(path, "wb") as out:
                for p in parts:
                    with open(p, "rb") as f:
                        shutil.copyfileobj(f, out)
            print(f"[합침] {name} ← {len(parts)}개 조각")

    from sevenn.calculator import SevenNetCalculator
    import sevenn

    for name, ref in sums.items():
        path = os.path.join(args.dir, name)
        if not os.path.exists(path):
            print(f"[없음] {name}")
            continue
        ok = sha256(path) == ref
        print(f"[{'OK' if ok else '해시 불일치'}] {name}")
        if not ok:
            continue

        slab = fcc111("Pt", size=(3, 3, 3), vacuum=10.0)
        mol = molecule("H2O")
        mol.set_cell([20, 20, 20]); mol.center(); mol.pbc = True
        ads = slab.copy()
        h2o = molecule("H2O"); h2o.rotate(180, "x")  # H가 위를 향하게 (O-down)
        add_adsorbate(ads, h2o, 2.3, "ontop")
        for modal in TEST_MODALS[name]:
            calc = SevenNetCalculator(model=path, modal=modal, device=args.device)
            e = {}
            for k, a in (("slab", slab), ("mol", mol), ("ads", ads)):
                a = a.copy(); a.calc = calc
                e[k] = a.get_potential_energy()
            print(f"    {modal:>8}: E_ads(H2O/Pt, 고정 구조) = "
                  f"{e['ads'] - e['slab'] - e['mol']:+.3f} eV")

        if args.install:
            dst = os.path.join(os.path.dirname(sevenn.__file__),
                               "pretrained_potentials", KEYWORD_DIR[name], name)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(path, dst)
            print(f"    키워드 경로에 복사: {dst}")


if __name__ == "__main__":
    main()
