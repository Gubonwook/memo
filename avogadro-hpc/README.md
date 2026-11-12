# avogadro-hpc — GPU 없는 HPC에서 구조 보기

GPU, 화면(DISPLAY), OpenGL, FUSE, 관리자 권한이 **하나도 없는** 리눅스(HPC)에서 원자 구조를 보기 위한 패키지입니다.

| 방법 | HPC에 필요한 것 | 용도 |
|---|---|---|
| **① 웹 뷰어 (권장)** | `python3` 하나 (추가 설치 없음) | 구조 확인, supercell, MD 궤적 재생, cube 등치면, 거리/각도 측정, PNG 저장 |
| ② Avogadro GUI (선택) | X 포워딩 + `libGL`/`libX11` | 구조 편집, 분자 빌드 등 Avogadro 고유 기능 |

> **왜 웹 뷰어가 기본인가:** `echo $DISPLAY`가 비어 있으면 HPC에는 창을 그릴 화면이 없습니다. Avogadro는 GUI 프로그램이라 이 상태로는 실행할 수 없습니다.
> 웹 뷰어는 HPC가 **파일만 보내고**, 그림은 데스크톱 브라우저가 그립니다. 그래서 HPC에는 GPU도 화면도 필요 없습니다.

---

## 0. 데스크톱에서 받기

1. 이 저장소 → **Code → Download ZIP** → `avogadro-hpc/` 폴더만 꺼냅니다.
2. (Avogadro GUI도 쓸 경우에만) Avogadro 릴리스 페이지에서 리눅스 AppImage를 받습니다.
   - https://github.com/OpenChemistry/avogadrolibs/releases
   - 파일 이름 예: `Avogadro2-x86_64.AppImage` (HPC가 ARM이면 `aarch64`용)
3. `avogadro-hpc/` 폴더를 통째로 HPC로 옮깁니다 (scp, WinSCP, 사내 전송 도구 등). AppImage는 `avogadro-hpc/avogadro/` 안에 넣습니다.

```bash
# 예: 데스크톱 터미널에서
scp -r avogadro-hpc user@hpc:~/
```

---

## 1. HPC 환경 점검

```bash
cd ~/avogadro-hpc
bash check_env.sh
```

읽기만 하고 아무것도 바꾸지 않습니다. 맨 아래 **판정**에 무엇을 쓸 수 있는지 나옵니다.

---

## 2. 웹 뷰어 사용 (권장)

### 2-1. HPC에서 서버 켜기

```bash
bash ~/avogadro-hpc/start_viewer.sh ~/calc/HfO2      # 구조 파일이 있는 폴더
```

하위 폴더까지 구조 파일을 자동으로 찾아 목록을 만듭니다. 끌 때는 `Ctrl+C`를 누릅니다.
포트(기본 8765)가 사용 중이면 자동으로 다음 번호를 씁니다. 실제 번호는 화면에 출력됩니다.

### 2-2. 데스크톱에서 접속

**새 터미널**을 열고 SSH 터널을 겁니다. Windows 10 이상은 PowerShell에 `ssh`가 기본으로 있습니다.

```bash
ssh -L 8765:localhost:8765 user@hpc
```

브라우저(Chrome/Edge)에서 **http://localhost:8765** 를 엽니다.

- **계산 노드에서 서버를 띄운 경우**: 서버를 `--host 0.0.0.0`으로 켜고 로그인 노드를 경유해 터널을 겁니다.
  ```bash
  # HPC (계산 노드)
  python3 ~/avogadro-hpc/viewer/serve.py ~/calc --host 0.0.0.0
  # 데스크톱
  ssh -L 8765:<계산노드이름>:8765 user@login-node
  ```
  `0.0.0.0`은 같은 네트워크의 다른 사용자도 접속할 수 있다는 뜻입니다. 민감한 데이터라면 로그인 노드에서 기본값(127.0.0.1)으로 쓰세요.
- **MobaXterm**: Tunneling 메뉴에서 Local port forwarding을 설정합니다(8765 → localhost:8765).

### 2-3. HPC 없이 데스크톱에서만 보기

`viewer/index.html`을 브라우저로 직접 열고 파일을 드래그하면 됩니다. 서버가 없어도 동작합니다.

### 지원 형식

| 형식 | 파일 이름 예 | ASE 필요 |
|---|---|---|
| VASP 구조 | `POSCAR`, `CONTCAR`, `*.vasp`, `xxx.POSCAR` (Selective dynamics, VASP4 형식 포함) | 아니오 |
| VASP 궤적 | `XDATCAR` (고정 셀 / 가변 셀) | 아니오 |
| xyz / extended xyz | `*.xyz`, `*.extxyz` (`Lattice="..."` 있으면 셀 표시, 다중 프레임 재생) | 아니오 |
| CIF, PDB | `*.cif`, `*.pdb` | 아니오 |
| Gaussian cube | `*.cube` (±등치면) | 아니오 |
| 기타 | `*.mol2`, `*.sdf`, `*.mol`, `*.gro`, `*.pqr` | 아니오 |
| OUTCAR, vasprun.xml, `*.traj`, `*.xsf`, LAMMPS data 등 | | **예** (`pip install --user ase`) |

### 기능

- 표시 스타일: Ball & stick / Stick / Space filling / Line(큰 시스템용)
- 단위 셀 표시, a·b·c축 방향으로 보기
- Supercell (최대 6×6×6)
- MD 궤적 프레임 슬라이더와 재생
- cube 등치면 값과 투명도 조절
- 원자를 클릭해 거리(2개), 각도(3개) 측정
- 원소 라벨, 어두운 배경, PNG 저장
- 정보 패널: 원자 수, 조성, 격자 상수, 부피

---

## 3. Avogadro GUI (선택)

**조건:** ① X 서버가 있는 터미널(MobaXterm 등)로 `ssh -Y` 접속, ② HPC에 `libGL.so.1`과 `libX11.so.6` 존재. `check_env.sh`로 확인할 수 있습니다.

```bash
cd ~/avogadro-hpc/avogadro
bash extract_appimage.sh ./Avogadro2-x86_64.AppImage   # FUSE 없이 풀기 (1회)
bash ../check_env.sh                                    # 누락 라이브러리 재점검
bash run_avogadro.sh                                    # 실행
bash run_avogadro.sh ~/calc/CONTCAR                     # 파일 지정
```

`run_avogadro.sh`는 GPU 대신 CPU로 OpenGL을 그리도록 설정합니다(`LIBGL_ALWAYS_SOFTWARE=1`, Mesa llvmpipe). 렌더링 스레드는 `LP_NUM_THREADS=4`가 기본이고, `LP_NUM_THREADS=8 bash run_avogadro.sh`처럼 바꿀 수 있습니다.

**현실적인 한계**
- `libGL.so.1`이 없는 최소 설치 HPC에서는 실행되지 않습니다. 관리자에게 `mesa-libGL`(RHEL 계열) 또는 `libgl1 libglx-mesa0`(Ubuntu 계열) 설치를 요청해야 합니다.
- X 포워딩 화면 전송은 느립니다. 회전할 때 끊기는 건 정상이고, 단순히 보는 용도라면 웹 뷰어가 훨씬 빠릅니다.

---

## 문제 해결

| 증상 | 해결 |
|---|---|
| 브라우저에서 접속이 안 됨 | SSH 터널 터미널이 열려 있는지, 서버가 출력한 포트 번호와 같은지 확인 |
| 목록이 비어 있음 | 서버를 켤 때 지정한 폴더 확인. 하위 6단계까지만 탐색 |
| 파일이 회색("ASE 필요") | HPC에서 `pip install --user ase` 후 서버 재시작 |
| 화면이 하얗기만 함 | 브라우저 하드웨어 가속(WebGL) 켜기. `chrome://gpu`에서 WebGL 확인 |
| 큰 궤적이 느림 | 스타일을 Line으로 바꾸기. ASE 경유 궤적은 2000프레임으로 자동 축소 |
| `extract_appimage.sh` 실패 | 홈 폴더가 noexec 마운트인지 확인 (`mount \| grep $HOME`). 다른 폴더(예: scratch)에서 실행 |
| Avogadro 창이 안 뜸 | `bash run_avogadro.sh --debug` 출력의 `cannot open`, `not found` 줄 확인 |

---

## 파일 구성

```
avogadro-hpc/
├── README.md
├── check_env.sh            # 환경 점검 (읽기 전용)
├── start_viewer.sh         # 웹 뷰어 실행 바로가기
├── viewer/
│   ├── serve.py            # 파이썬 표준 라이브러리 서버 (3.6+)
│   ├── index.html          # 뷰어 화면
│   └── lib/3Dmol-min.js    # 3Dmol.js 2.5.5 (오프라인 번들, BSD-3)
├── avogadro/
│   ├── extract_appimage.sh # AppImage를 FUSE 없이 풀기
│   └── run_avogadro.sh     # 소프트웨어 OpenGL로 실행
└── samples/                # 테스트용 합성 구조 (실제 계산 결과 아님)
```

라이선스: 3Dmol.js는 BSD-3-Clause입니다(`viewer/lib/3Dmol-LICENSE.txt`). Avogadro는 BSD 라이선스이며 이 저장소에는 포함되어 있지 않습니다.
