#!/usr/bin/env python
"""SevenNet + ASE NEB 예시 (sevenn 0.13.0 CPU에서 동작 확인: H fcc→hcp / Pt(111)).

    python neb_example.py --ckpt ckpt/checkpoint_sevennet_omni.pth --modal oc22 \
        --initial IS.vasp --final FS.vasp --nimages 7

- IS/FS는 같은 원자 순서여야 합니다(VASP CONTCAR 그대로 쓰면 됨).
- 계산기 하나를 모든 image가 공유합니다(allow_shared_calculator=True) → GPU 메모리 절약.
- 끝점은 먼저 같은 modal로 완화합니다. 그래야 장벽 기준이 맞습니다.
"""
import argparse

from ase.io import read, write
from ase.mep import NEB
from ase.optimize import FIRE

from sevenn.calculator import SevenNetCalculator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--modal", required=True)
    ap.add_argument("--initial", required=True)
    ap.add_argument("--final", required=True)
    ap.add_argument("--nimages", type=int, default=7, help="중간 image 수")
    ap.add_argument("--fmax", type=float, default=0.05)
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--no-relax-ends", action="store_true")
    args = ap.parse_args()

    calc = SevenNetCalculator(args.ckpt, modal=args.modal, device=args.device)

    ends = []
    for f in (args.initial, args.final):
        a = read(f)
        a.calc = calc
        if not args.no_relax_ends:
            FIRE(a, logfile=None).run(fmax=args.fmax, steps=args.steps)
        ends.append(a)

    images = [ends[0]] + [ends[0].copy() for _ in range(args.nimages)] + [ends[1]]
    neb = NEB(images, climb=True, allow_shared_calculator=True)
    neb.interpolate(method="idpp")
    for im in images[1:-1]:
        im.calc = calc
    FIRE(neb, trajectory="neb.traj").run(fmax=args.fmax, steps=args.steps)

    E = [im.get_potential_energy() for im in images]
    e0 = E[0]
    for i, e in enumerate(E):
        print(f"image {i:2d}: {e - e0:+.4f} eV")
    print(f"Ea(forward) = {max(E) - e0:.3f} eV, dE = {E[-1] - e0:+.3f} eV")
    write("neb_final.extxyz", images)


if __name__ == "__main__":
    main()
