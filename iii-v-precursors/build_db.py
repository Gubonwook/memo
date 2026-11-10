# -*- coding: utf-8 -*-
"""InGaAs ALD/ALE precursor database builder (In / Ga precursors, As reactants)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from openpyxl.worksheet.table import Table, TableStyleInfo

FONT = "Arial"
EL = ["C", "H", "N", "O", "F", "Cl", "Br", "I", "Si", "Sn", "In", "Ga", "As", "P"]
AW = {"C": 12.011, "H": 1.008, "N": 14.007, "O": 15.999, "F": 18.998, "Cl": 35.45, "Br": 79.904,
      "I": 126.904, "Si": 28.085, "Sn": 118.71, "In": 114.818, "Ga": 69.723, "As": 74.922, "P": 30.974}
PREC_EL = ["C", "H", "N", "O", "Cl", "Br", "I", "Si", "In", "Ga"]   # columns shown on precursor sheets

def F(s):
    """parse simple formula dict string like 'C3H9In'"""
    import re
    d = {}
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", s):
        if el:
            d[el] = d.get(el, 0) + (int(n) if n else 1)
    return d

# ---------------------------------------------------------------- precursors
# keys: id, nota (AtomicLimits), abbr, name, metal, nM, ox, f (formula str or None),
# lig_class, lig, bonds, donor, betaH, state, mp, bp, vpA, vpB, vp_note, thermal, pyro, cas,
# cert (formula certainty), src, oxygen(bool)
P = []
def add(**k):
    P.append(k)

# ---------- Indium
add(id="In-01", nota="InMe3", abbr="TMIn", name="Trimethylindium", metal="In", nM=1, ox="+3",
    f="C3H9In", lig_class="Alkyl", lig="Me ×3", bonds="In–C ×3", donor="없음", betaH="없음 (Me)",
    state="고체 (승화성)", mp="88 (88.0–88.8)", bp="134 (101 °C 이상 분해)", vpA=3204, vpB=10.98,
    vp_note="log P(Torr)=10.98−3204/T, 30–100 °C 유효; 고체라 사용량에 따라 실효 증기압 변동",
    thermal="101 °C 이상에서 분해 보고; 상압 OMVPE에서 400 °C 미만에선 느리게 분해 (저온용으로는 너무 안정)",
    pyro="자연발화 (H250, H260)", cas="3385-78-2", cert="확정", src="S2; S16", oxygen=False)
add(id="In-02", nota="InEt3", abbr="TEIn", name="Triethylindium", metal="In", nM=1, ox="+3",
    f="C6H15In", lig_class="Alkyl", lig="Et ×3", bonds="In–C ×3", donor="없음", betaH="있음 (Et)",
    state="액체", mp="−32", bp="144 (상압) / 92 @10 mmHg", vpA=None, vpB=None,
    vp_note="30 °C에서 TMIn보다 증기압 낮음 (특허 서술); 식 미확인",
    thermal="40 °C부터 분해 시작, H2 존재 시 더 낮음 (특허 서술 — 1차 문헌 확인 필요); 기상 기생반응 문제 보고",
    pyro="자연발화 (H250), 물과 격렬 반응", cas="923-34-2", cert="확정", src="S3; S16; S17; S61", oxygen=False)
add(id="In-03", nota="InMe2(PrNMe2)", abbr="DADI", name="[3-(Dimethylamino)propyl]dimethylindium", metal="In", nM=1, ox="+3",
    f="C7H18InN", lig_class="Alkyl + 분자내 아민 donor (chelate)", lig="Me ×2, (CH2)3NMe2", bonds="In–C ×3, In←N ×1 (분자내)",
    donor="분자내 N donor", betaH="propyl 사슬 (분자내 배위로 안정화)", state="액체", mp="", bp="", vpA=None, vpB=None,
    vp_note="", thermal="H2O로 275 °C에서 ALD (0.6 Å/cycle)", pyro="", cas="", cert="확정 (약어·구조 문헌 확인)",
    src="S18; S22; S23; S26", oxygen=False)
add(id="In-04", nota="InMe3(NMe2Bu)", abbr="DATI", name="(N,N-Dimethylbutylamine)trimethylindium", metal="In", nM=1, ox="+3",
    f="C9H24InN", lig_class="Alkyl + 아민 adduct", lig="Me ×3 · NMe2Bu", bonds="In–C ×3, In←N ×1 (adduct)",
    donor="외부 아민 adduct", betaH="없음 (Me)", state="액체", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="DADI 대비 입체장애 작음 (DFT), PEALD GPC 높음", pyro="", cas="", cert="확정", src="S18; S26", oxygen=False)
add(id="In-05", nota="InEt2(N(SiMe3)2)", abbr="Et2InN(TMS)2", name="Diethyl[bis(trimethylsilyl)amido]indium", metal="In", nM=1, ox="+3",
    f="C10H28InNSi2", lig_class="Alkyl + 실릴아미드", lig="Et ×2, N(SiMe3)2", bonds="In–C ×2, In–N ×1",
    donor="없음", betaH="있음 (Et)", state="액체", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O와 GPC ~0.7 Å (TMIn ~0.39 Å보다 높음); 200 °C 미만에서 C 잔류", pyro="", cas="",
    cert="확정", src="S18; S23; S24", oxygen=False)
add(id="In-06", nota="InMe2(tBuAMD)", abbr="DBDMI", name="(N,N'-Di-tert-butylacetimidamido)dimethylindium", metal="In", nM=1, ox="+3",
    f="C12H27InN2", lig_class="Alkyl + amidinate (heteroleptic)", lig="Me ×2, (tBuN)2CMe", bonds="In–C ×2, In–N ×2",
    donor="κ2-N,N chelate", betaH="없음 (Me)", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="고온 ALD용 전구체로 설계 (O3, 200–350 °C 공정 보고)", pyro="", cas="", cert="확정 (약어 문헌 기준)",
    src="S27", oxygen=False)
add(id="In-07", nota="In(iPrAMD)3", abbr="In(amd)3", name="Tris(N,N'-diisopropylacetamidinato)indium", metal="In", nM=1, ox="+3",
    f="C24H51InN6", lig_class="Amidinate (homoleptic)", lig="(iPrN)2CMe ×3", bonds="In–N ×6",
    donor="κ2-N,N chelate ×3", betaH="해당 없음 (M–C 없음)", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O ALD 창 225–300 °C; 150 °C 승화, 320 °C까지 녹지 않고 분해; H2S와 In2S3 ALD (190 °C 공급)", pyro="", cas="", cert="확정", src="S18; S24; S64", oxygen=False)
add(id="In-08", nota="In(iPrFMD)3", abbr="In(famd)3", name="Tris(N,N'-diisopropylformamidinato)indium", metal="In", nM=1, ox="+3",
    f="C21H45InN6", lig_class="Formamidinate (homoleptic)", lig="(iPrN)2CH ×3", bonds="In–N ×6",
    donor="κ2-N,N chelate ×3", betaH="해당 없음", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O ALD 창 150–275 °C (H2O 기반 In2O3 중 가장 낮은 onset, 가장 넓은 창); C-free 막; 증발에 ~127 °C 가열 필요", pyro="자연발화 아님 (저자 서술)",
    cas="", cert="확정", src="S18; S24", oxygen=False)
add(id="In-09", nota="In(dpguan)3", abbr="In(guan)3", name="Tris(N,N-dimethyl-N',N''-diisopropylguanidinato)indium", metal="In", nM=1, ox="+3",
    f="C27H60InN9", lig_class="Guanidinate (homoleptic)", lig="(iPrN)2C–NMe2 ×3", bonds="In–N ×6",
    donor="κ2-N,N chelate ×3", betaH="해당 없음", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O ALD 창 230–300 °C; 110 °C 이상에서 상당한 분해 (특허 서술)", pyro="", cas="",
    cert="추정 — 'dpguan' 표기를 Mpofu 2022 Table 1의 In(guan)3로 대응시킴; 원문 확인 필요", src="S18", oxygen=False)
add(id="In-10", nota="In(triaz)3", abbr="In(triaz)3", name="Tris(1,3-diisopropyltriazenide)indium(III)", metal="In", nM=1, ox="+3",
    f="C18H42InN9", lig_class="Triazenide (homoleptic)", lig="iPrN=N–NiPr ×3", bonds="In–N ×6",
    donor="κ2-N,N chelate ×3", betaH="해당 없음", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O ALD 창 ~270–385 °C, ~1.0 Å/cycle, 저불순물", pyro="", cas="",
    cert="추정 — 치환기(iPr)는 동 그룹 Ga 유사체 표기 기준; 원문 확인 필요", src="S18", oxygen=False)
add(id="In-11", nota="InCp", abbr="InCp", name="Cyclopentadienylindium(I)", metal="In", nM=1, ox="+1",
    f="C5H5In", lig_class="Cyclopentadienyl", lig="C5H5 ×1", bonds="In–Cp (η5)", donor="없음", betaH="해당 없음",
    state="고체", mp="", bp="", vpA=None, vpB=None, vp_note="0.01 mmHg에서 ~50 °C 승화 (판매처); ALD 버블러 40 °C, 배관 200 °C 유지",
    thermal="O3와 200–450 °C ALD; 500 °C에선 대부분 분해 (CVD화); Cp 부산물로 C 불순물 증가 우려", pyro="", cas="", cert="확정", src="S19; S20; S21; S62", oxygen=False)
add(id="In-12", nota="In(EtCp)", abbr="InEtCp", name="Ethylcyclopentadienylindium(I)", metal="In", nM=1, ox="+1",
    f="C7H9In", lig_class="Cyclopentadienyl", lig="C5H4Et ×1", bonds="In–Cp (η5)", donor="없음", betaH="해당 없음",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="", pyro="", cas="", cert="확정 (표기 기준)",
    src="S1", oxygen=False)
add(id="In-13", nota="InCl3", abbr="InCl3", name="Indium(III) chloride", metal="In", nM=1, ox="+3",
    f="InCl3", lig_class="Halide", lig="Cl ×3", bonds="In–Cl ×3", donor="없음", betaH="해당 없음",
    state="고체", mp="", bp="", vpA=None, vpB=None, vp_note="증기압 매우 낮음 — 평면 기판 포화에도 소스 285 °C 필요",
    thermal="H2O/H2O2와 300–500 °C, GPC 0.25–0.40 Å; HCl 부산물이 장비·막 식각", pyro="불연", cas="",
    cert="확정", src="S18; S19; S58", oxygen=False)
add(id="In-14", nota="InCl", abbr="InCl", name="Indium(I) chloride (반응기 내 생성)", metal="In", nM=1, ox="+1",
    f="InCl", lig_class="Halide (Ga/In 금속 + HCl 현장 생성)", lig="Cl ×1", bonds="In–Cl", donor="없음", betaH="해당 없음",
    state="기상 (in situ)", mp="", bp="", vpA=None, vpB=None, vp_note="외부 공급원이 아니라 hydride/chloride VPE 반응기 안에서 생성",
    thermal="Chloride ALE (InAs) — Koukitu, Ahopelto", pyro="", cas="", cert="확정", src="S1", oxygen=False)
add(id="In-15", nota="InClMe2", abbr="DMInCl", name="Dimethylindium chloride", metal="In", nM=1, ox="+3",
    f="C2H6ClIn", lig_class="Alkyl + halide", lig="Me ×2, Cl", bonds="In–C ×2, In–Cl ×1", donor="없음", betaH="없음 (Me)",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="InAs ALE (Mori) — DEGaCl과 같은 개념의 할라이드-알킬 혼합형",
    pyro="", cas="", cert="확정", src="S1", oxygen=False)
# O-containing In
add(id="In-16", nota="In(acac)3", abbr="In(acac)3", name="Indium(III) acetylacetonate", metal="In", nM=1, ox="+3",
    f="C15H21InO6", lig_class="β-Diketonate", lig="acac ×3", bonds="In–O ×6", donor="κ2-O,O chelate ×3", betaH="해당 없음",
    state="고체", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="H2O 165–220 °C / O3 160–225 °C", pyro="",
    cas="", cert="확정", src="S18", oxygen=True)
add(id="In-17", nota="In(thd)3", abbr="In(tmhd)3", name="Tris(2,2,6,6-tetramethyl-3,5-heptanedionato)indium", metal="In", nM=1, ox="+3",
    f="C33H57InO6", lig_class="β-Diketonate", lig="thd ×3", bonds="In–O ×6", donor="κ2-O,O chelate ×3", betaH="해당 없음",
    state="고체", mp="175", bp="", vpA=None, vpB=None, vp_note="In(acac)3보다 휘발성 낮음; MOCVD 버블러 ~200 °C", thermal="O2 plasma 100–400 °C, GPC 매우 낮음 (0.014 nm/cycle)",
    pyro="", cas="", cert="확정", src="S18; S25; S63", oxygen=True)
add(id="In-18", nota="In(dmamp)3", abbr="In(dmamp)3", name="Tris(1-dimethylamino-2-methyl-2-propoxy)indium", metal="In", nM=1, ox="+3",
    f="C18H42InN3O3", lig_class="Aminoalkoxide", lig="OCMe2CH2NMe2 ×3", bonds="In–O ×3, In←N ×3", donor="κ2-O,N chelate ×3",
    betaH="해당 없음", state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="O3 100–300 °C", pyro="", cas="",
    cert="확정", src="S18", oxygen=True)
add(id="In-19", nota="In(dmamp)2(OiPr)", abbr="", name="Bis(dmamp)(isopropoxy)indium", metal="In", nM=1, ox="+3",
    f="C15H35InN2O3", lig_class="Aminoalkoxide + alkoxide", lig="dmamp ×2, OiPr", bonds="In–O ×3, In←N ×2", donor="κ2-O,N chelate ×2",
    betaH="해당 없음", state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="O3 공정 (Han et al.)", pyro="", cas="",
    cert="확정 (표기 기준)", src="S1", oxygen=True)
add(id="In-20", nota="InMe2(edpa)", abbr="Me2In(EDPA)", name="Dimethyl(N-ethoxy-2,2-dimethylpropanamido)indium", metal="In", nM=1, ox="+3",
    f="C9H20InNO2", lig_class="Alkyl + amidate (N-alkoxy)", lig="Me ×2, tBuC(O)N(OEt)", bonds="In–C ×2, In–N/O (chelate)",
    donor="κ2 chelate", betaH="없음 (Me)", state="액체", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="O2 plasma 70–250 °C (Mpofu 표) / 90–180 °C, 0.053 nm/cycle (원 논문)", pyro="", cas="", cert="확정",
    src="S18; S25", oxygen=True)
add(id="In-21", nota="InMe3(MeO(CH2)2NHtBu)", abbr="", name="Trimethylindium · N-(2-methoxyethyl)-tert-butylamine adduct", metal="In", nM=1, ox="+3",
    f="C10H26InNO", lig_class="Alkyl + 아민/에테르 adduct", lig="Me ×3 · MeOCH2CH2NHtBu", bonds="In–C ×3, In←N/O (adduct)",
    donor="외부 adduct (N,O)", betaH="없음 (Me)", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O 150–200 °C", pyro="", cas="", cert="확정 (표기 기준)", src="S18", oxygen=True)
add(id="In-22", nota="InMe2(NtBu(CH2)2(CH3)2OMe)", abbr="", name="Dimethylindium 아미도-에테르 착물 (Choi et al.)", metal="In", nM=1, ox="+3",
    f=None, lig_class="Alkyl + 아미도-에테르 chelate", lig="Me ×2, N(tBu)–…–OMe", bonds="In–C ×2, In–N, In←O",
    donor="κ2-N,O chelate", betaH="없음 (Me)", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="O2 plasma 공정", pyro="", cas="",
    cert="표기 모호 — DB 표기만으로 리간드 골격을 확정할 수 없어 분자식 계산 보류", src="S1", oxygen=True)

# ---------- Gallium
add(id="Ga-01", nota="GaMe3", abbr="TMGa", name="Trimethylgallium", metal="Ga", nM=1, ox="+3",
    f="C3H9Ga", lig_class="Alkyl", lig="Me ×3", bonds="Ga–C ×3", donor="없음", betaH="없음 (Me)",
    state="액체", mp="−15.8 (삼중점 257.45 K)", bp="55.7", vpA=None, vpB=None,
    vp_note="NIST: 20.45 kPa (290 K), 32.48 kPa (300 K) → 20 °C ≈ 180 Torr; 버블러는 보통 0 °C 등으로 냉각",
    thermal="기상 균일분해 380–460 °C; 300 °C 이상 GaAs 표면에서 메틸 전부 이탈", pyro="자연발화", cas="1445-79-0",
    cert="확정", src="S4; S5; S15; S60", oxygen=False)
add(id="Ga-02", nota="GaEt3", abbr="TEGa", name="Triethylgallium", metal="Ga", nM=1, ox="+3",
    f="C6H15Ga", lig_class="Alkyl", lig="Et ×3", bonds="Ga–C ×3", donor="없음", betaH="있음 (Et, β-H 제거 경로)",
    state="액체", mp="−82.3", bp="143", vpA=2162, vpB=8.083,
    vp_note="log P(Torr)=8.083−2162/T; 10 °C 2.80 Torr, 20 °C 5.10 Torr", thermal="TMGa보다 분해 온도 낮음 → 저온 공정용, C 혼입 적음; GaAs ALE는 좁은 조건에서만",
    pyro="자연발화, 물과 격렬 반응", cas="1115-99-7", cert="확정", src="S6; S7; S39; S40", oxygen=False)
add(id="Ga-03", nota="GaEt2Me", abbr="", name="Diethylmethylgallium", metal="Ga", nM=1, ox="+3",
    f="C5H13Ga", lig_class="Alkyl (혼합)", lig="Et ×2, Me", bonds="Ga–C ×3", donor="없음", betaH="있음 (Et)",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="GaAs ALE (Sakuma)", pyro="", cas="", cert="확정",
    src="S1", oxygen=False)
add(id="Ga-04", nota="GaiBu3", abbr="TIBGa", name="Triisobutylgallium", metal="Ga", nM=1, ox="+3",
    f="C12H27Ga", lig_class="Alkyl", lig="iBu ×3", bonds="Ga–C ×3", donor="없음", betaH="있음 (iBu)",
    state="액체", mp="", bp="73 @5.25 mmHg", vpA=None, vpB=None, vp_note="", thermal="GaAs ALE (Ozeki); MOMBE에서 저온 효율이 TEGa보다 좋고 C 적음", pyro="자연발화 (H250)", cas="", cert="확정",
    src="S1; S65", oxygen=False)
add(id="Ga-05", nota="GaNp3", abbr="TNGa", name="Trineopentylgallium", metal="Ga", nM=1, ox="+3",
    f="C15H33Ga", lig_class="Alkyl", lig="CH2CMe3 ×3", bonds="Ga–C ×3", donor="없음", betaH="없음 (neopentyl)",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="β-H 제거 없이 TMGa처럼 homolysis 분해; GaAs ALE 430–500 °C, TMGa처럼 뚜렷한 self-limiting, C 감소는 크지 않음", pyro="", cas="",
    cert="확정", src="S1; S66", oxygen=False)
add(id="Ga-06", nota="GaEt2Cl", abbr="DEGaCl", name="Diethylgallium chloride", metal="Ga", nM=1, ox="+3",
    f="C4H10ClGa", lig_class="Alkyl + halide", lig="Et ×2, Cl", bonds="Ga–C ×2, Ga–Cl ×1", donor="없음 (기상 이량체 우세)",
    betaH="있음 (Et)", state="액체 (수분과 매우 빠르게 반응)", mp="", bp="60–62 (판매처 값)", vpA=3080, vpB=8.943,
    vp_note="log P(Torr)=8.943−3080/T, 5–60 °C 측정; 기상은 이량체 우세", thermal="분해 생성물 GaCl이 self-limiting 담당; 고온일수록 C 감소, 600 °C에서 고이동도; hot-wall MOVPE 350–700 °C (0.1–10 Torr)",
    pyro="", cas="", cert="확정", src="S10; S40; S41; S67", oxygen=False)
add(id="Ga-07", nota="GaCl3", abbr="GaCl3", name="Gallium(III) chloride", metal="Ga", nM=1, ox="+3",
    f="GaCl3", lig_class="Halide", lig="Cl ×3", bonds="Ga–Cl ×3 (고체/기상 Ga2Cl6 이량체)", donor="없음", betaH="해당 없음",
    state="고체 (조해성)", mp="77.9", bp="201", vpA=None, vpB=None, vp_note="48 °C에서 1 Torr",
    thermal="탄소 없음; AsH3와 200–500 °C ALE 보고, 단 300 °C 이상에서 1→2 ML/cycle로 증가; (Et3Si)3As와 GaAs ALD 창 175–200 °C; NH3와 GaN은 400 °C 이상에서 Cl 잔류", pyro="불연, 부식성 (H314)",
    cas="13450-90-3", cert="확정", src="S8; S9; S42; S43; S69", oxygen=False)
add(id="Ga-08", nota="GaCl", abbr="GaCl", name="Gallium(I) chloride (반응기 내 생성)", metal="Ga", nM=1, ox="+1",
    f="GaCl", lig_class="Halide (in situ)", lig="Cl ×1", bonds="Ga–Cl", donor="없음", betaH="해당 없음",
    state="기상 (in situ)", mp="", bp="", vpA=None, vpB=None, vp_note="Ga 금속 + HCl 현장 생성",
    thermal="Chloride ALE: 흡착 GaCl이 H와 반응해 HCl로 Cl 이탈", pyro="", cas="", cert="확정", src="S1; S40", oxygen=False)
add(id="Ga-09", nota="GaBr", abbr="GaBr", name="Gallium(I) bromide (in situ)", metal="Ga", nM=1, ox="+1",
    f="GaBr", lig_class="Halide (in situ)", lig="Br ×1", bonds="Ga–Br", donor="없음", betaH="해당 없음",
    state="기상 (in situ)", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="GaAs ALE (Taki)", pyro="", cas="",
    cert="확정", src="S1", oxygen=False)
add(id="Ga-10", nota="GaI", abbr="GaI", name="Gallium(I) iodide (in situ)", metal="Ga", nM=1, ox="+1",
    f="GaI", lig_class="Halide (in situ)", lig="I ×1", bonds="Ga–I", donor="없음", betaH="해당 없음",
    state="기상 (in situ)", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="GaAs ALE (Taki)", pyro="", cas="",
    cert="확정", src="S1", oxygen=False)
add(id="Ga-11", nota="GaI3", abbr="GaI3", name="Gallium(III) iodide", metal="Ga", nM=1, ox="+3",
    f="GaI3", lig_class="Halide", lig="I ×3", bonds="Ga–I ×3", donor="없음", betaH="해당 없음",
    state="고체", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="O3와 Ga2O3 (Aarik)", pyro="", cas="", cert="확정",
    src="S1", oxygen=False)
add(id="Ga-12", nota="Ga2(NMe2)6", abbr="[Ga(NMe2)3]2", name="Hexakis(dimethylamido)digallium", metal="Ga", nM=2, ox="+3",
    f="C12H36Ga2N6", lig_class="Dialkylamide", lig="NMe2 ×6 (μ-NMe2 가교 이량체)", bonds="Ga–N ×8 (말단 4 + 가교 4)",
    donor="이량체", betaH="해당 없음", state="고체 (이량체), 수분 민감", mp="101–104", bp="", vpA=None, vpB=None, vp_note="",
    thermal="H2O 170–250 °C (좁은 창); O2 plasma 60–160 °C, 1.5 Å/cycle, C·N <2 at.%; NH3 plasma GaN 130–250 °C, 1.4 Å/cycle", pyro="", cas="", cert="확정",
    src="S28; S29; S68", oxygen=False)
add(id="Ga-13", nota="(GaMe2NH2)3", abbr="[Me2GaNH2]3", name="Dimethylgallium amide trimer", metal="Ga", nM=3, ox="+3",
    f="C6H24Ga3N3", lig_class="Alkyl + amide (삼량체)", lig="Me ×6, μ-NH2 ×3", bonds="Ga–C ×6, Ga–N ×6 (가교)",
    donor="삼량체", betaH="없음 (Me)", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="O2 plasma 공정, 200 °C 부근으로 제한", pyro="", cas="", cert="확정", src="S29", oxygen=False)
add(id="Ga-14", nota="GaMe2NH2", abbr="", name="Dimethylgallium amide (DB 별도 표기)", metal="Ga", nM=1, ox="+3",
    f="C2H8GaN", lig_class="Alkyl + amide", lig="Me ×2, NH2", bonds="Ga–C ×2, Ga–N", donor="실제로는 올리고머 가능", betaH="없음 (Me)",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="O2 plasma (Seong) — Ga-13과 같은 물질일 가능성",
    pyro="", cas="", cert="확정 (단량체 표기)", src="S1", oxygen=False)
add(id="Ga-15", nota="Ga(iPr-triaz)3", abbr="Ga(triaz)3", name="Tris(1,3-diisopropyltriazenide)gallium", metal="Ga", nM=1, ox="+3",
    f="C18H42GaN9", lig_class="Triazenide (homoleptic)", lig="iPrN=N–NiPr ×3", bonds="Ga–N ×6", donor="κ2-N,N chelate ×3",
    betaH="해당 없음", state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="H2O와 Ga2O3 (Mushore)", pyro="", cas="",
    cert="확정 (표기 기준)", src="S1", oxygen=False)
add(id="Ga-16", nota="Ga(CpMe5)", abbr="GaCp*", name="Pentamethylcyclopentadienylgallium(I)", metal="Ga", nM=1, ox="+1",
    f="C10H15Ga", lig_class="Cyclopentadienyl", lig="C5Me5 ×1", bonds="Ga–Cp* (η5)", donor="없음", betaH="해당 없음",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="H2O+O2 plasma (Mizutani) — InEtCp와 같은 그룹 공정",
    pyro="", cas="", cert="확정", src="S1", oxygen=False)
# O-containing Ga
add(id="Ga-17", nota="Ga(acac)3", abbr="Ga(acac)3", name="Gallium(III) acetylacetonate", metal="Ga", nM=1, ox="+3",
    f="C15H21GaO6", lig_class="β-Diketonate", lig="acac ×3", bonds="Ga–O ×6", donor="κ2-O,O chelate ×3", betaH="해당 없음",
    state="고체", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="고온(~370 °C) 필요, O3에서만 조성 양호 (2차 인용)",
    pyro="", cas="", cert="확정", src="S29", oxygen=True)
add(id="Ga-18", nota="Ga(thd)3", abbr="Ga(TMHD)3", name="Tris(2,2,6,6-tetramethyl-3,5-heptanedionato)gallium", metal="Ga", nM=1, ox="+3",
    f="C33H57GaO6", lig_class="β-Diketonate", lig="thd ×3", bonds="Ga–O ×6", donor="κ2-O,O chelate ×3", betaH="해당 없음",
    state="고체", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="O2 plasma 100–400 °C, 0.1 Å/cycle; H2O·O3로는 300 °C에서 거의 성장 없음",
    pyro="", cas="", cert="확정", src="S29", oxygen=True)
add(id="Ga-19", nota="Ga(OiPr)3", abbr="GTIP", name="Gallium triisopropoxide", metal="Ga", nM=1, ox="+3",
    f="C9H21GaO3", lig_class="Alkoxide", lig="OiPr ×3", bonds="Ga–O ×3 (실제 올리고머 가능)", donor="", betaH="해당 없음",
    state="", mp="", bp="", vpA=None, vpB=None, vp_note="", thermal="H2O 150–250 °C (2차 인용)", pyro="", cas="", cert="확정",
    src="S29; S33", oxygen=True)
add(id="Ga-20", nota="GaMe2(OiPr)", abbr="DMGIP", name="Dimethylgallium isopropoxide", metal="Ga", nM=1, ox="+3",
    f="C5H13GaO", lig_class="Alkyl + alkoxide", lig="Me ×2, OiPr", bonds="Ga–C ×2, Ga–O ×1", donor="μ-O 가교 가능", betaH="없음 (Me)",
    state="액체", mp="", bp="", vpA=None, vpB=None, vp_note="상온 약 3 Torr",
    thermal="H2O ALD 창 280–300 °C, ~0.3 Å/cycle; MOCVD 450–625 °C", pyro="자연발화 아님", cas="", cert="확정",
    src="S30", oxygen=True)
add(id="Ga-21", nota="GaMe3(CH3OCH2CH2NHtBu)", abbr="", name="Trimethylgallium · N-(2-methoxyethyl)-tert-butylamine adduct", metal="Ga", nM=1, ox="+3",
    f="C10H26GaNO", lig_class="Alkyl + 아민/에테르 adduct", lig="Me ×3 · MeOCH2CH2NHtBu", bonds="Ga–C ×3, Ga←N/O",
    donor="외부 adduct (N,O)", betaH="없음 (Me)", state="", mp="", bp="", vpA=None, vpB=None, vp_note="",
    thermal="O2 plasma (Hong)", pyro="", cas="", cert="확정 (표기 기준)", src="S1", oxygen=True)

# ---------------------------------------------------------------- group-V reactants
# DB = AtomicLimits 목록에 있음 / "미수록" = 다른 문헌에서만 확인
A = [
 dict(id="As-01", nota="AsH3", abbr="Arsine", name="Arsine", f="AsH3", cls="Hydride", bonds="As–H ×3", VH=3, inDB="예",
      state="기체 (고압 실린더)", mp="−111.2 (−116 보고도 있음)", bp="−62.5", vp="14.9 atm (≈11,000 mmHg, 20 °C)",
      decomp="석영 반응관에서 475–600 °C 균일분해(석영이 촉매), GaAs 존재 시 가속. 다른 자료는 230–240 °C부터 분해 시작으로 기술 — 측정 조건이 다름",
      tox="ACGIH TLV-TWA 0.005 ppm, OSHA PEL 0.05 ppm, IDLH 3 ppm, 폭발범위 5.1–78%", carbon="C 원천 없음",
      note="ALE 표준 As 원; 저온에서 열분해 느림 → 저온 공정에선 As 공급 효율이 문제. GaAs CVD 700–900 °C, InAs OMVPE 600→275 °C", cas="7784-42-1",
      src="S13; S14; S15; S73"),
 dict(id="As-02", nota="tBuAsH2", abbr="TBAs", name="tert-Butylarsine", f="C4H11As", cls="Monoalkyl arsine", bonds="As–C ×1, As–H ×2", VH=2, inDB="예",
      state="액체", mp="−1", bp="65–68", vp="96 Torr (10 °C)",
      decomp="분해 개시 ~350 °C, GaAs 표면에서 최대 200 °C 낮아짐; AsH3보다 저온에서 빨리 분해 → V/III ≈ 1에서도 GaAs 형태 양호",
      tox="H250 (자연발화), H330 (흡입 시 치명) — 고압가스인 AsH3보다 취급 안전; 상온 저장 중 소량 AsH3로 분해 보고",
      carbon="추가 C 혼입 없음 보고", note="TMGa/TBAs vacuum ALE: 1 ML/cycle, 창 폭 70 °C; MOVPE: GaAs(TEGa) 350–700 °C, InAs(TMIn) 480–540 °C, (Ga,In)As/InP 570–650 °C",
      cas="4262-43-5", src="S11; S12; S44; S53; S54; S70"),
 dict(id="As-03", nota="EtAsH2", abbr="EtAs", name="Ethylarsine", f="C2H7As", cls="Monoalkyl arsine", bonds="As–C ×1, As–H ×2", VH=2, inDB="예",
      state="", mp="", bp="", vp="", decomp="", tox="", carbon="모노·디알킬 아르신은 트리알킬보다 C 혼입 적음 (계열 일반론)",
      note="TMGa와 GaAs ALE (Maa)", cas="", src="S1; S53"),
 dict(id="As-04", nota="As(NMe2)3", abbr="TDMAAs", name="Tris(dimethylamino)arsenic", f="C6H18AsN3", cls="Amino arsine", bonds="As–N ×3", VH=0, inDB="예",
      state="액체 (수분 민감)", mp="−53", bp="55 @10 mmHg", vp="",
      decomp="사전 크래킹 불필요; 아민 종이 Ga·As 표면에 흡착해 self-limiting 기여 → TEGa ALE 온도 범위 크게 확장",
      tox="AsH3 대비 안전한 대체원 (As–H 없음)", carbon="C 혼입 적음 보고",
      note="TMGa와 500 °C ALE (GaAs/GaMnAs); TEGa+TDMAAs CBE 470 °C에서 선택성 확보(AsH3·As4는 600 °C); 480 °C에서 GaAs 자연산화막 제거(열 탈착보다 110 °C 낮음); InAs/GaAs ALE·초격자",
      cas="", src="S45; S46; S47; S52; S71; S72"),
 dict(id="As-05", nota="(Et3Si)3As", abbr="", name="Tris(triethylsilyl)arsine", f="C18H45AsSi3", cls="Silyl arsine", bonds="As–Si ×3", VH=0, inDB="예",
      state="", mp="", bp="", vp="As 소스 50–70 °C로 사용", decomp="할라이드(GaCl3)와 dehalosilylation 반응 → Et3SiCl 부산물",
      tox="", carbon="Si·C 혼입 확인 필요", note="GaCl3와 GaAs ALD 창 175–200 °C, 비정질·화학량론 막; 특허 예 100·120 °C에서 0.5–0.7 Å/cycle (Ga0.58As0.42)",
      cas="", src="S1; S69"),
 dict(id="As-06", nota="As", abbr="As (원소)", name="Elemental arsenic (As4/As2 증기)", f="As", cls="원소", bonds="—", VH=0, inDB="예",
      state="고체 (승화)", mp="", bp="1기압에서 610 °C 승화", vp="", decomp="크래커로 As2 생성 가능",
      tox="As 화합물 독성", carbon="C·H 없음", note="GaCl3·GaEt2Cl과 GaAs ALE (Kobayashi, Sasaoka)", cas="", src="S1; S55"),
 dict(id="As-07", nota="(Me3Si)3As (DB 미수록)", abbr="", name="Tris(trimethylsilyl)arsine", f="C9H27AsSi3", cls="Silyl arsine", bonds="As–Si ×3", VH=0, inDB="미수록",
      state="", mp="", bp="82–84 @4 Torr", vp="", decomp="MX3와 반응해 MAs + 3 Me3SiX", tox="공기·수분 민감", carbon="",
      note="GaCl3/GaMe3와 상압 CVD GaAs (기판 온도 미확인)", cas="", src="S74"),
 dict(id="As-08", nota="AsMe3 (DB 미수록)", abbr="TMAs", name="Trimethylarsine", f="C3H9As", cls="Trialkyl arsine", bonds="As–C ×3", VH=0, inDB="미수록",
      state="액체", mp="−87.3", bp="56", vp="", decomp="", tox="인화점 −25 °C", carbon="C 오염 심함 (트리알킬 공통)",
      note="GaAs MOVPE 550–800 °C, InAsP 700 °C — ALE용 아님 (참고)", cas="", src="S53; S75"),
 dict(id="As-09", nota="AsEt3 (DB 미수록)", abbr="TEAs", name="Triethylarsine", f="C6H15As", cls="Trialkyl arsine", bonds="As–C ×3", VH=0, inDB="미수록",
      state="액체", mp="", bp="140 (판매처 값)", vp="", decomp="", tox="", carbon="C 오염된 GaAs",
      note="GaAs 상압 OMCVD 560–590 °C (참고)", cas="", src="S53; S76"),
 dict(id="As-10", nota="Et2AsH (DB 미수록)", abbr="DEAs", name="Diethylarsine", f="C4H11As", cls="Dialkyl arsine", bonds="As–C ×2, As–H ×1", VH=1, inDB="미수록",
      state="액체", mp="", bp="105", vp="", decomp="", tox="", carbon="As–H 1개 있어 고품질 GaAs 가능 (리뷰)",
      note="GaAs MOVPE 550–800 °C (참고)", cas="", src="S54; S77"),
 dict(id="As-11", nota="As(CF3)3 (DB 미수록)", abbr="", name="Tris(trifluoromethyl)arsine", f="C3F9As", cls="Perfluoroalkyl arsine", bonds="As–C ×3", VH=0, inDB="미수록",
      state="", mp="", bp="~33", vp="", decomp="", tox="", carbon="",
      note="대부분 조건에서 GaAs를 식각; 낮은 V/III·250 Torr 이상에서만 성장 (참고)", cas="", src="S78"),
]

PX = [
 dict(id="P-01", nota="PH3", abbr="Phosphine", name="Phosphine", f="PH3", cls="Hydride", bonds="P–H ×3", VH=3, inDB="문헌",
      state="기체 (액화 압축가스)", mp="−132.8 (−133.8)", bp="−87.7", vp="41.3 atm (20 °C)",
      decomp="~375 °C부터 분해, ~593 °C에서 완전 분해 (판매처 자료); 열분해는 1차 반응이며 주로 표면(불균일) 반응. CH3로 덮인 In 표면에서는 PH3 분해가 느려 InP ALE가 1 ML/cycle 미만이 됨",
      tox="OSHA PEL 0.3 ppm, ACGIH TLV-TWA 0.05 ppm·STEL 0.15 ppm (2017), IDLH 50 ppm; 자연발화온도 38 °C (P2H4 불순물 있으면 상온 발화), 폭발범위 1.79–98%",
      carbon="C 원천 없음", note="InP·GaP ALE/PE-ALD 표준 P 원. PE-ALD에서는 챔버 벽에 쌓인 과잉 P가 문제 → H2 plasma 식각 단계 추가",
      cas="7803-51-2", src="S79; S80; S81; S82; S90"),
 dict(id="P-02", nota="tBuPH2", abbr="TBP", name="tert-Butylphosphine", f="C4H11P", cls="Monoalkyl phosphine", bonds="P–C ×1, P–H ×2", VH=2, inDB="문헌",
      state="액체 (공기 민감)", mp="−85 (판매처 값)", bp="54", vp="",
      decomp="PH3보다 저온에서 분해; SiO2 표면 영향 없는 균일 반응, 1차 반응이 아님(농도 높을수록 빠름). H2 중 단독 분해는 >500 °C 시작·>700 °C 완료(FTIR), TMIn이 있으면 상온에서 반응(adduct)하고 300 °C부터 분해",
      tox="H250 (자연발화), H314, H330 — 리뷰에서는 독성이 매우 낮다고 기술 (판매처 GHS와 상충, 확인 필요)",
      carbon="TBP 기인 C 오염 없음 보고; GaAsP에서 As/P 비 제어가 PH3보다 쉬움", note="InP OMVPE에서 PH3보다 낮은 V/III로 고품질; TEIn/TBP UHV 분자층 에피 320–340 °C",
      cas="2501-94-2", src="S54; S83; S84; S85; S86; S87"),
 dict(id="P-03", nota="P(NMe2)3", abbr="TDMAP", name="Tris(dimethylamino)phosphine", f="C6H18N3P", cls="Amino phosphine", bonds="P–N ×3", VH=0, inDB="문헌",
      state="액체", mp="", bp="", vp="", decomp="", tox="P–H 없음", carbon="",
      note="TMGa와 GaP ALD 보고 (320 °C 초과 필요); AlPO4 ALD P 원; GaP/GaAs pulse-jet ALE (Haraguchi)", cas="", src="S52; S88; S89"),
 dict(id="P-04", nota="P(SiMe3)3", abbr="TMS3P", name="Tris(trimethylsilyl)phosphine", f="C9H27PSi3", cls="Silyl phosphine", bonds="P–Si ×3", VH=0, inDB="문헌",
      state="액체", mp="", bp="", vp="상압에서도 증류 가능할 만큼 휘발성 (저자 서술)", decomp="InX3 (X=Cl, Br, I)와 반응해 InP 생성 (Me3SiX 이탈)",
      tox="공기·수분 민감", carbon="Si 혼입 확인 필요",
      note="InP 양자점 표준 P 원; Co2P ALD 보고; InP/GaP ALD는 2022년 시점 미보고 (저자 서술)", cas="", src="S89; S90; S91"),
 dict(id="P-05", nota="P(tBu)3", abbr="tri-TBP", name="Tri-tert-butylphosphine", f="C12H27P", cls="Trialkyl phosphine", bonds="P–C ×3", VH=0, inDB="문헌",
      state="", mp="", bp="", vp="", decomp="", tox="", carbon="P-rich GaP 막",
      note="TEGa + tri-TBP + 원자 H로 GaP PE-ALD (2.7 Å/cycle); 원자 H+tri-TBP로 Si 표면 기능화가 핵생성 핵심", cas="", src="S92"),
 dict(id="P-06", nota="tBuP(NMe2)2", abbr="TBBDMAP", name="tert-Butylbis(dimethylamino)phosphine", f="C8H21N2P", cls="Alkyl amino phosphine", bonds="P–C ×1, P–N ×2", VH=0, inDB="문헌",
      state="", mp="", bp="", vp="", decomp="TBP보다 낮은 열분해 온도를 목표로 개발 (특허)", tox="", carbon="",
      note="OMVPE/CBE용 (특허) — ALD 보고 미확인", cas="", src="S93"),
 dict(id="P-07", nota="P (원소, 원격 플라스마)", abbr="P4 / PHx", name="Elemental phosphorus vapor", f="P", cls="원소", bonds="—", VH=0, inDB="문헌",
      state="고체", mp="", bp="", vp="", decomp="원격 RF H2 플라스마로 원자 H·PHx 생성", tox="", carbon="C 없음",
      note="원격 플라스마 CVD로 GaP 에피 590 °C 이상 (ALD 아님, 참고)", cas="", src="S94"),
 dict(id="P-08", nota="P(SnMe3)3", abbr="TMT3P", name="Tris(trimethyltin)phosphide", f="C9H27PSn3", cls="Stannyl phosphine", bonds="P–Sn ×3", VH=0, inDB="문헌",
      state="", mp="", bp="", vp="", decomp="", tox="", carbon="Sn 혼입 우려",
      note="TiCl4와 TiP ALD 창 175–225 °C (InP/GaP에는 미적용, 참고)", cas="", src="S95"),
]

# ---------------------------------------------------------------- processes
PR = []
def pr(film, pre, b, c, typ, tmin="", tmax="", gpc="", note="", refs="", src="", **k):
    PR.append(dict(film=film, pre=pre, b=b, c=c, typ=typ, tmin=tmin, tmax=tmax, gpc=gpc, note=note,
                   refs=refs, src=src, sub=k.get("sub", ""), reactor=k.get("reactor", ""),
                   srcT=k.get("srcT", ""), seq=k.get("seq", ""), cryst=k.get("cryst", ""),
                   comp=k.get("comp", ""), props=k.get("props", "")))

# In2O3
pr("In2O3","InCl3","H2O","", "Thermal ALD",300,500,"0.25–0.40 Å/cycle","HCl 부산물이 장비·막 식각","Asikainen et al. 외","S18; S19; S58",
   srcT="InCl3 285 °C", reactor="ALE 반응기 (400·500 °C 성장 보고)")
pr("In2O3","InCl3","H2O2","", "Thermal ALD",300,500,"","","Ritala et al.","S18")
pr("In2O3","InMe3","H2O","", "Thermal ALD",200,250,"~0.39 Å/cycle","200 °C 이상에서만 성장","Ott, Lee, Niu 외","S18; S24")
pr("In2O3","InMe3","O3","", "Thermal ALD",100,200,"","","Salami, Shan, Zhu 외","S18")
pr("In2O3","InMe3","O2 plasma","", "PEALD","","","","","Lim, Mahmoodinezhad, Shi 외","")
pr("In2O3","InCp","O3","", "Thermal ALD",200,450,"1.2–1.4 Å/cycle (창 내); 사이클 수에 따라 1.3→2.0","200 °C 미만 급감(O3 분해 임계), 500 °C 전구체 분해","Elam, Martinson","S19",
   srcT="InCp 버블러 40 °C, 배관 200 °C", reactor="점성류 ALD, N2 60 sccm", seq="InCp 2 s – 퍼지 4 s – O3 2 s – 퍼지 2 s; O3 ~10% (O2 400 sccm)",
   cryst="입방정 나노결정 In2O3", props="투명 전도성")
pr("In2O3","InCp","H2O","O2", "Thermal ALD",100,350,"","H2O·O2 단독으로는 성장 거의 없음, 둘 다 필요","Libera, Keller","S18; S21",
   seq="동시 노출/H2O→O2/O2→H2O 세 모드 비교 (100–250 °C)")
pr("In2O3","InCp","H2O2","", "Thermal ALD",160,200,"~1.46 Å/cycle","","Ma et al.","S20",
   sub="Si; TFT는 Al2O3/p+Si", comp="200 °C: In:O = 1:1.36, C 미검출", props="Eg 3.42→3.75 eV (150→200 °C); TFT 이동도 7.8 cm²/V·s (300 °C 공기 열처리 후)")
pr("In2O3","InCp","O2 plasma","", "PEALD",225,275,"","","Zhao, Zhang","S18")
pr("In2O3","In(EtCp)","H2O","O2 plasma", "PEALD","","","","","Mizutani et al.","")
pr("In2O3","In(EtCp)","H2O","O2", "Thermal ALD","","","","","Mizutani et al.","")
pr("In2O3","In(EtCp)","O2 plasma","", "PEALD","","","","","Mizutani et al.","")
pr("In2O3","In(EtCp)","H2O","O3", "Thermal ALD","","","","","Kobayashi et al.","")
pr("In2O3","In(acac)3","H2O","", "Thermal ALD",165,220,"","","Nilsen et al.","S18")
pr("In2O3","In(acac)3","O3","", "Thermal ALD",160,225,"","","Nilsen et al.","S18")
pr("In2O3","In(thd)3","O3","", "Thermal ALD","","","","","Brahim et al.","")
pr("In2O3","In(thd)3","O2 plasma","", "PEALD",100,400,"0.014 nm/cycle","","Ramachandran et al.","S18; S25")
pr("In2O3","In(dmamp)3","O3","", "Thermal ALD",100,300,"","","Han et al.","S18")
pr("In2O3","In(dmamp)2(OiPr)","O3","", "Thermal ALD","","","","","Han et al.","")
pr("In2O3","In(dpguan)3","H2O","", "Thermal ALD",230,300,"0.45–0.55 Å/cycle (amd·famd·guan 공통)","'dpguan'=guan 대응은 추정","Gebhard et al.","S18")
pr("In2O3","In(iPrAMD)3","H2O","", "Thermal ALD",225,300,"0.45–0.55 Å/cycle","","Kim et al.","S18; S24")
pr("In2O3","In(iPrFMD)3","H2O","", "Thermal ALD",150,275,"0.45–0.55 Å/cycle","H2O 공정 중 최저 onset·최대 창","Kim et al.","S18; S24",
   srcT="~127 °C", comp="C-free")
pr("In2O3","In(triaz)3","H2O","", "Thermal ALD",270,385,"~1.0 Å/cycle","","Mpofu et al.","S18",
   comp="저불순물", props="0.2 mΩ·cm, 높은 투과율")
pr("In2O3","InEt2(N(SiMe3)2)","H2O","", "Thermal ALD",175,250,"~0.7 Å/cycle","200 °C 미만 C 잔류","Maeng et al.","S18; S24")
pr("In2O3","InEt2(N(SiMe3)2)","O3","", "Thermal ALD",100,200,"","","Maeng et al.","S18; S23",
   props="150 °C 이상 비저항 <10⁻³ Ω·cm")
pr("In2O3","InEt2(N(SiMe3)2)","O2 plasma","", "PEALD","","","","","Yeom et al.","")
pr("In2O3","InEt2(N(SiMe3)2)","H2O2","", "Thermal ALD","","","","","Nguyen et al.","")
pr("In2O3","InEt3","O3","", "Thermal ALD",100,200,"0.009→0.088 nm/cycle (115→250 °C, 계속 증가)","뚜렷한 창 없음 (S59)","Maeng et al.","S18; S23; S59",
   reactor="Ar 캐리어 50 sccm, 작업 압력 300 mTorr", cryst="≥200 °C 다결정 입방정", comp="≥200 °C C 거의 없음",
   props="100 °C 미만에서 액체 전구체 중 최저 비저항 2×10⁻³ Ω·cm; 거칠기 <1.6 nm")
pr("In2O3","InEt3","O2 plasma","", "PEALD","","","","","Kawato et al.","")
pr("In2O3","InMe2(PrNMe2)","H2O","", "Thermal ALD",275,275,"0.6 Å/cycle","보고 온도 275 °C (창 양 끝 아님)","Maeng et al.","S22",
   props="비저항 9.2×10⁻⁵ Ω·cm, 420–700 nm 투과율 >80%")
pr("In2O3","InMe2(PrNMe2)","O3","", "Thermal ALD",100,200,"","","Maeng et al.","S18; S23")
pr("In2O3","InMe2(PrNMe2)","O2 plasma","", "PEALD","","","DATI보다 낮음","","Hong et al.","S26")
pr("In2O3","InMe2(tBuAMD)","O3","", "Thermal ALD",200,350,"0.06–0.1 nm/cycle","200·300·350 °C 보고값 (창 정의 아님)","Lee et al.","S27",
   cryst="200 °C 비정질, 300·350 °C 결정질", comp="OH 관련 ~1% (고온)", props="TFT 이동도 온도에 따라 증가, Vth 변화 작음")
pr("In2O3","InMe2(edpa)","O2 plasma","", "PEALD",70,250,"0.053 nm/cycle","원 논문은 90–180 °C","Kim et al.","S18; S25",
   props="고이동도 TFT")
pr("In2O3","InMe2(edpa)","H2O","", "Thermal ALD","","","","","Agbenyeke et al.","")
pr("In2O3","InMe2(NtBu(CH2)2(CH3)2OMe)","O2 plasma","", "PEALD","","","","","Choi et al.","")
pr("In2O3","InMe3(MeO(CH2)2NHtBu)","H2O","", "Thermal ALD",150,200,"","","Lee et al.","S18")
pr("In2O3","InMe3(NMe2Bu)","O2 plasma","", "PEALD",100,200,"DADI보다 높음","","Choi, Kim","S18; S26",
   cryst="DADI보다 결정성 우수, 결함 적음", props="FET 이동도 115.8 cm²/V·s, Vth −0.12 V, SS <70 mV/dec")
pr("In2S3","In(acac)3","H2S","", "Thermal ALD","","","","붙여주신 목록이 여기서 잘림","Yousfi 외","")
pr("In2S3","In(acac)3","H2S plasma","", "PEALD","","","","","Van den Hoek et al.","")
pr("In2S3","In(iPrAMD)3 (DB 표기 외)","H2S","", "Thermal ALD","","","","특허; 전구체 190 °C 공급","—","S64", srcT="150 °C 승화, 190 °C 공급")
# Ga2O3
pr("Ga2O3","(GaMe2NH2)3","O2 plasma","", "PEALD",200,200,"","200 °C 부근으로 제한","Shan, Seong, Liu","S29")
pr("Ga2O3","GaMe2NH2","O2 plasma","", "PEALD","","","","","Seong et al.","")
pr("Ga2O3","Ga(acac)3","O3","", "Thermal ALD",370,370,"","고온(~370 °C) 필요, 2차 인용","Nieminen, Utriainen 외","S29")
pr("Ga2O3","Ga(acac)3","H2O","", "Thermal ALD","","","","","Nieminen et al.","")
pr("Ga2O3","Ga(CpMe5)","H2O","O2 plasma", "PEALD","","","","","Mizutani et al.","")
pr("Ga2O3","Ga(CpMe5)","O2 plasma","", "PEALD","","","","","Mizutani et al.","")
pr("Ga2O3","Ga(iPr-triaz)3","H2O","", "Thermal ALD","","","","","Mushore et al.","")
pr("Ga2O3","Ga(OiPr)3","H2O","", "Thermal ALD",150,250,"","2차 인용","Choi et al.","S29; S33")
pr("Ga2O3","Ga(thd)3","O2 plasma","", "PEALD",100,400,"0.1 Å/cycle","H2O·O3로는 300 °C에서 거의 성장 없음","Ramachandran, Wei","S29",
   sub="SiO2/Si", seq="전구체 5 s – O2 plasma 5 s (퍼지 가스 없음), 300 W", cryst="비정질", comp="화학량론, C 미검출")
pr("Ga2O3","Ga2(NMe2)6","H2O","", "Thermal ALD",170,250,"","좁은 창","Dezelah et al.","S29")
pr("Ga2O3","Ga2(NMe2)6","O2 plasma","", "PEALD",60,160,"1.5 Å/cycle","초기 기판 억제 있음","O'Donoghue et al.","S28",
   sub="Si(100)", cryst="비정질 (1000 °C 열처리 시 β-Ga2O3)", comp="거의 화학량론, C·N <2 at.%", props="Eg 4.9 eV, 투과율 >80%")
pr("Ga2O3","GaCl3","H2O","", "Thermal ALD","","","","","Qi et al.","")
pr("Ga2O3","GaEt3","O2 plasma","", "PEALD",250,350,"","250–350 °C에서 α-Ga2O3 우세 (상 기준, 창 아님); >350 °C α+ε 혼합","Shih, Roberts 외","S34",
   sub="사파이어", reactor="Ar 캐리어·퍼지 100 sccm", seq="TEGa 0.1 s – 퍼지 5 s – O2 plasma 5 s – 퍼지 5 s; 최적 300 W, O2 20 sccm", cryst="α-Ga2O3")
pr("Ga2O3","GaEt3","Ar+O2 plasma","", "PEALD",150,240,"0.69–1.31 Å/cycle","연구 범위","Ilhom et al.","S32",
   sub="Si, 사파이어, 유리", reactor="hollow-cathode 플라스마, 30–300 W", seq="매 사이클 후 in situ Ar plasma 20 s (50–300 W)",
   cryst="Ar plasma 없으면 비정질, 250 W Ar plasma로 β-Ga2O3", comp="O/Ga ~1.44, C ~5 at.%")
pr("Ga2O3","GaEt3","O3","", "Thermal ALD","","","","","Wang, Li, Zhang 외","")
pr("Ga2O3","GaI3","O3","", "Thermal ALD","","","","","Aarik et al.","")
pr("Ga2O3","GaMe2(OiPr)","H2O","", "Thermal ALD",280,300,"~0.3 Å/cycle","","Lee et al.","S30",
   sub="Si(001)", srcT="상온 (~3 Torr)", cryst="비정질", comp="화학량론")
pr("Ga2O3","GaMe3","O3","", "Thermal ALD",250,300,"0.4 (250 °C), 0.5 Å/cycle (300 °C)","보고 온도 (창 정의 아님)","Comstock, Allen, Hiller 외","S33")
pr("Ga2O3","GaMe3","O2 plasma","", "PEALD",100,400,"~0.53 Å/cycle","","Donmez, Allen, Ma 외","S31")
pr("Ga2O3","GaMe3","O2 plasma","", "PEALD",80,250,"~0.6 Å/cycle","같은 공정, 다른 그룹 (2500 W)","—","S33",
   sub="Si, 사파이어", srcT="TMGa 0 °C", seq="TMGa 0.2 s – N2 퍼지 4 s – O2 plasma 28 s – N2 퍼지 4 s", reactor="2500 W 플라스마")
pr("Ga2O3","GaMe3","O2 plasma","", "PEALD",200,200,"0.65–0.70 Å/cycle","O2 plasma 3–30 s 비교","—","S96",
   sub="Si(100)", cryst="비정질", comp="계면 SiOx 재성장 0.27 nm로 제한 (첫 3사이클)", props="플라스마 노출 길수록 누설전류 5자릿수 감소, εr ~14.2")
pr("Ga2O3","GaMe3","H2O","", "Thermal ALD","","","","","Hou, Yang","")
pr("Ga2O3","GaMe3","N2O plasma","", "PEALD","","","","","Uvarov et al.","")
pr("Ga2O3","GaMe3(CH3OCH2CH2NHtBu)","O2 plasma","", "PEALD","","","","","Hong et al.","")
pr("GaN","[Ga(NMe2)3]2","NH3 plasma","", "PEALD",130,250,"1.4 Å/cycle","붙여주신 목록이 여기서 잘림","Rouf et al.","S68",
   sub="Si(100), 4H-SiC", cryst="Si 위 결정질; 4H-SiC 위 AlN 버퍼 없이 에피", comp="Ga/N 거의 화학량론, C·O 낮음", props="Eg ~3.42 eV, 비의도적 n형")
pr("GaN","GaCl3","NH3","", "Thermal ALD",400,"","","400 °C 이상, Cl 불순물","—","S69")
# GaAs
pr("GaAs","GaMe3","AsH3","", "ALE (MOVPE형)",445,485,"1 ML/cycle","표준 반응기 기준","Nishizawa, Bedair, Tischler 외 (62편)","S35",
   reactor="MOCVD형 반응기", props="ALE 활성층으로 고품질 양자우물·저문턱 QW 레이저 (AlGaAs/GaAs)")
pr("GaAs","GaMe3","AsH3","", "ALE (특수 반응기)",450,700,"1 ML/cycle","노출 시간 단축으로 기상 분해 억제","Reid, Urdianyk, Bedair","S36",
   reactor="기체 가열 최소화, 짧은 노출, 급차단 가능한 ALE 반응기", comp="노출 시간·온도로 C 도핑 10¹⁵–10²⁰ cm⁻³ 조절")
pr("GaAs","GaMe3","AsH3","", "ALE",400,400,"1 ML/cycle","TMGa 10 s 노출로 400 °C 포화","—","S38", seq="TMGa 10 s")
pr("GaAs","GaMe3","(AsH3 없이 흡착만)","", "UHV 흡착 연구",440,530,"Ga 1 ML 포화","320 °C에서는 반응 매우 느림","Maa & Dapkus","S37",
   sub="As 안정화 GaAs(001)", reactor="UHV, TMGa 10⁻⁷–5×10⁻⁶ Torr, 5–15 s", comp="XPS로 C 미검출", cryst="2×4 → 4×1/4×2 Ga 안정화")
pr("GaAs","GaMe3","tBuAsH2","", "Vacuum ALE","","","1 ML/cycle","창 폭 70 °C (양 끝 온도 미확인)","Maa, Chen 외","S44",
   reactor="진공 ALE", props="모두 p형, 운반자 농도는 노출 조건에 의존")
pr("GaAs","GaMe3","EtAsH2","", "ALE","","","","","Maa et al.","")
pr("GaAs","GaMe3","(Me2N)3As","", "ALE (pulse-jet)",500,500,"","보고 온도 (GaAs/GaMnAs)","—","S71")
pr("GaAs","GaEt3","AsH3","", "ALE (상압 MOVPE)","","","","좁은 온도·공급량 범위에서만 ALE; 일부 연구는 ALE 안 됨","Mochizuki, Meguro, Ohno 외","S39; S40",
   reactor="상압 MOVPE")
pr("GaAs","GaEt3","(Me2N)3As","", "ALE","","","","AsH3 대비 ALE 온도 범위 크게 확장 (값 미확인)","Fujii, Suemune","S45")
pr("GaAs","GaEt3","(Me2N)3As","", "CBE (선택 성장)",470,470,"","AsH3·As4는 같은 선택성에 600 °C 필요","—","S46", reactor="CBE (UHV)")
pr("GaAs","GaEt3","tBuAsH2","", "ALE","","","","","Aït-Lhouss, Arès","")
pr("GaAs","GaEt2Cl","AsH3","", "ALE (저압 MOCVD)","","","1 ML/cycle","넓은 조건에서 ML 성장","Mori, Yu","S41",
   sub="3인치 GaAs 웨이퍼 (균일)", reactor="수평형 저압 MOCVD", props="600 °C에서 n형, 77 K 이동도 22,400 cm²/V·s")
pr("GaAs","GaEt2Cl","AsH3","", "Hot-wall MOVPE",350,700,"","0.1–10 Torr","—","S67", props="450 °C에서 운반자 <2.5×10¹⁴ cm⁻³")
pr("GaAs","GaEt2Cl","As","", "ALE","","","","","Sasaoka et al.","")
pr("GaAs","GaEt2Me","AsH3","", "ALE","","","","완벽한 self-limiting은 TMGa에서만 관찰 (TMGa·EtMe2Ga·TEGa 비교)","Sakuma et al.","S97")
pr("GaAs","GaiBu3","AsH3","", "ALE","","","","","Ozeki et al.","")
pr("GaAs","GaNp3","tBuAsH2","", "ALE",430,500,"","TMGa처럼 뚜렷한 self-limiting, C 감소 크지 않음","Yeo, Arès","S66")
pr("GaAs","GaCl3","AsH3","", "ALE (할라이드 수송)",200,500,"300 °C 1 ML → 450 °C ~2 ML/cycle","300 °C 미만 다결정·SiO2 마스크에도 증착","Jin, Kobayashi, Ishikawa 외","S42; S43",
   sub="GaAs (SiO2 마스크)", reactor="H2 캐리어 (GaCl3/H2, AsH3/H2)", srcT="GaCl3를 반응기 밖에서 공급", cryst="300 °C 이상 단결정 (Raman)", comp="C 원천 없음")
pr("GaAs","GaCl3","As","", "ALE","","","","","Kobayashi et al.","")
pr("GaAs","GaCl3","(Et3Si)3As","", "ALD (dehalosilylation)",175,200,"0.5–0.7 Å/cycle (특허 100·120 °C)","특허 예는 100·120 °C","Sarnet et al.","S69",
   srcT="As 소스 50–70 °C", cryst="비정질", comp="화학량론 (특허 예 Ga0.58As0.42)")
pr("GaAs","GaCl","AsH3","", "Chloride ALE","","","","흡착 GaCl + H → HCl 이탈","Usui, Koukitu 외 (16편)","S40")
pr("GaAs","GaBr","AsH3","", "ALE","","","","","Taki et al.","")
pr("GaAs","GaI","AsH3","", "ALE","","","","","Taki et al.","")
pr("GaAs","TEGa·DEA adduct (TEGDEA, DB 미수록)","AsH3","", "ALE",400,"","1 ML/cycle","400 °C를 넘는 온도에서 self-limiting (특허)","—","S98",
   sub="GaAs(100)", seq="TEGDEA 6 s – H2 0.5 s – AsH3 10 s (100 sccm) – H2 0.5 s", props="(GaAs)1(InAs)1 초격자 InGaAs 활성층에 사용")
# InAs
pr("InAs","InMe3","AsH3","", "ALE",340,340,"1 ML/cycle","TMIn 3 s 노출로 340 °C 포화","Dapkus, Jeong, Jung 외","S38", seq="TMIn 3 s")
pr("InAs","InMe3","AsH3","", "ALE",350,400,"1 ML/cycle","AsH3 뒤 퍼지를 짧게(365 °C <0.5 s, 400 °C <0.1 s) 해야 이상적 ALE","—","S48",
   sub="InAs(001)", reactor="H2 또는 N2 퍼지", comp="AsH3 후 퍼지가 길면 최외각 As 탈착으로 성장률 감소; In 종단면은 안정")
pr("InAs","InMe3","AsH3","", "ALE (pulse-jet)","","","1 ML/cycle (0.303 nm)","360 °C에서는 TMIn 시간 늘려도 포화가 깨짐","Haraguchi, Ozeki","S52",
   sub="InAs(001)", seq="AsH3 8.0 s 고정", reactor="pulse-jet epitaxy, H2 퍼지, vent-and-run")
pr("InAs","InMe3","AsH3","", "ALE (회전 기판)",480,480,"self-limited","","—","S49", reactor="회전 기판·전용 서셉터로 잔류물·경계층 기계적 제거")
pr("InAs","InMe3","tBuAsH2","", "ALE","","","","HRXRD로 self-limiting 확인 (InAs/InP)","Tran et al.","S99")
pr("InAs","InMe3","tBuAsH2","", "MOVPE",480,540,"","경면 InAs 범위 (MOVPE)","—","S70")
pr("InAs","InEt3","AsH3","", "ALE","","","","","Tischler, McDermott","S51")
pr("InAs","InClMe2","AsH3","", "ALE","","","","","Mori et al.","")
pr("InAs","InCl","AsH3","", "Chloride ALE","","","","","Koukitu, Ahopelto","")
pr("InAs","InMe3·NMe2Et (TMIDMEA, DB 미수록)","AsH3","", "ALE",350,500,"1 ML/cycle","높은 열안정성으로 창 확장","—","S50",
   sub="GaAs(100)", props="(InAs)1(GaAs)1 초격자 12주기를 460 °C 단일 온도로 성장, 상온 PL 1.3 µm")
# ternary arsenides
pr("InGaAs","InMe3 + GaMe3","AsH3","", "ALE","","","","","Huang et al.","")
pr("Ga-As-In-As","GaMe3 + InEt3","AsH3","", "ALE","","","","TMGa→AsH3→TEIn→AsH3 순차; 두께가 사이클 수와 일치","Bedair et al.","S51", sub="InP")
pr("(InAs)m(GaAs)n","InMe3 + GaMe3","(Me2N)3As / AsH3","", "Pulsed-jet ALE","","","","격자 불일치와 원자 단위 표면 형상이 self-limiting에 크게 영향; 초격자로 유효 In 조성 높은 InGaAs","Haraguchi, Ozeki","S52",
   sub="GaAs(001), InP(001)")
pr("(Ga,In)As","TEGa/TMIn","tBuAsH2","", "MOVPE",570,650,"","InP 위 (Ga,In)As","—","S70", sub="InP")
# phosphides (AtomicLimits P 페이지는 미제공 → 문헌에서만)
pr("InP","InMe3","PH3","", "ALE",350,350,"self-limited","저온 350 °C에서 ALE 모드 성장","Sakuma et al. (JJAP 1988)","S100")
pr("InP","InMe3","PH3","", "ALE (특수 장치)",320,440,"1 분자층/cycle","기존 장치는 ~450 °C 이상에서 두께 증가; 20 Torr","—","S101", reactor="20 Torr, 기판에 원료를 분사하는 특수 장치 (특허)")
pr("InP","InMe3","PH3","", "교대 공급 MOCVD",340,340,"1 ML/cycle","에피 하한 330 °C; 420–580 °C 물질전달 율속, 400 °C 미만 반응 율속","P. L. Liu","S102",
   reactor="MOCVD")
pr("InP","InMe3","PH3","", "ALE (SPA 관찰)",350,350,"<1 ML/cycle","P 안정화면에 TMIn 공급 시 350 °C에서 self-limitation; CH3 종단 In 위에서 PH3 분해 느림. H2 퍼지로 CH3 탈착 후 PH3를 주면 1 ML/cycle에 근접","NTT","S103",
   sub="InP(001)", reactor="H2 퍼지")
pr("InP","InMe3","PH3","", "ALE (LP-MOCVD)","","","<1 ML/cycle","CH3 종단 In 표면에서 PH3 불완전 분해가 원인 (SPA)","서울대·경희대","S104", reactor="LP-MOCVD")
pr("InP","InEt3","tBuPH2","", "분자층 에피 (UHV)",320,340,"~0.7 ML/cycle","경면 표면은 320–340 °C에서만; SiNx 위 다결정 증착 없음(선택 성장)","Otsuka, Nishizawa 외","S87",
   sub="InP(001) (부분 SiNx 마스크)", reactor="UHV, 사전 크래킹 없음")
pr("InP","InMe3","PH3","", "PE-ALD",250,350,"안정 GPC (380 °C에서 증가)","380 °C에서 비이상 성장 시작","Uvarov et al. (2025)","S105",
   sub="n형 Si(100) (양면 연마, 5–10 Ω·cm)", reactor="Plasmalab 100, 13.56 MHz CCP 직접 플라스마; TMIn·PH3 모두 H2 희석",
   cryst="온도↑ 결정성↑ (Raman LO 강화)", props="PL 1.36–1.39 eV, 고온에서 청색편이·선폭 감소")
pr("InP","InMe3","tBuPH2","", "OMVPE","","","","V/III 15, TBP 분압 0.5 Torr, TBP 유량 램프 버퍼","—","S86")
pr("InP","InX3 (X=Cl, Br, I)","P(SiMe3)3","", "용액/고상 합성 (참고)","","","","Me3SiX 이탈로 InP 생성 — ALD 화학의 근거","Harvard","S91")
pr("GaP","GaMe3","PH3","", "ALE (LP-MOVPE)","","","self-limiting","최초 GaP ALE; 표면 P가 TMG를 선택 흡착하는 기구 (표면 Ga에 CH3 없음, XPS)","Sakuma, Kodama, Ozeki","S106",
   reactor="저압 MOVPE")
pr("GaP","GaMe3","PH3","H2 plasma", "PE-ALD",250,380,"","20 W에서 비정질, 100 W에서 미결정(RMS 6 nm); P 단계 후 H2 plasma로 과잉 P 제거해야 ALD형 성장","Gudovskikh et al.","S107",
   sub="Si", reactor="연속 H2 plasma, 시간 변조", cryst="저전력 비정질 (380 °C에서 3–5 nm 나노결정 일부)", props="RMS 0.9→0.2 nm (250→380 °C, 비정질)")
pr("GaP","GaMe3","PH3","H2 plasma", "PE-ALD",350,350,"","","Morozov et al.","S108",
   sub="Si", cryst="균일 비정질, GaP/Si 계면 날카로움", props="MBE GaP/Si보다 패시베이션 우수")
pr("GaP:Si","GaMe3","PH3","SiH4 (0.1% in H2)", "PE-ALD",380,380,"","Si 도핑 단계 별도","Gudovskikh et al.","S109",
   sub="p형 Si", reactor="연속 H2 플라스마", cryst="비정질·미결정", props="n-GaP/p-Si 이종접합, 광전 효과")
pr("GaP","GaEt3","P(tBu)3","원자 H", "PE-ALD","","","2.7 Å/cycle","Si 표면을 원자 H + tri-TBP로 기능화해야 핵생성","—","S92",
   sub="Si(100), 6° 미스컷 Si", cryst="다결정 (미스컷 Si에서 국부 에피)", comp="P/Ga 비 높음 (P-rich)")
pr("GaP","GaMe3","P(NMe2)3","", "Thermal ALD","","","","320 °C 초과 필요","—","S88")
pr("GaP / GaAs","GaMe3","P(NMe2)3 / PH3","", "Pulse-jet ALE","","","","GaP/GaP(001), GaP/GaAs(001) — 격자 불일치가 self-limiting에 영향","Haraguchi, Ozeki","S52",
   sub="GaP(001), GaAs(001)")
pr("GaAs-GaP SLS","GaMe3","AsH3 / PH3","", "ALE","","","","GaAs–GaP 변형층 초격자","Ozeki et al.","S110")
pr("InGaP","InMe3 + GaMe3","PH3","", "Pulse-jet ALE","","","","3원계 PJE 성장 (학위논문)","Sakuma","S111")
pr("GaP","GaMe3","P (원격 H2 plasma)","", "Remote PECVD (참고)",590,"","","ALD 아님; GaP·Si 위 에피","Choi et al.","S94", sub="GaP, Si")
# other As
pr("AlAs","AlMe3","AsH3","", "ALE (참고)","","","","As 반응물 참고용","Bedair, Ozeki 외","")
pr("AlAs","Me3N:AlH3","As(NMe2)3","", "ALE (참고)","","","","","Fujii, Suemune","")
pr("As2S3","As(NMe2)3","H2S","", "Thermal ALD (참고)","","","","TDMAAs가 금속 전구체 역할","Färm et al.","")
pr("MnAs","Mn(CpMe)2","As(NMe2)3","", "ALE (참고)","","","","","Ozeki et al.","")
pr("TiP (참고)","TiCl4","P(SnMe3)3","", "Thermal ALD",175,225,"","P-rich TiP, 조성이 온도·기판에 의존","—","S95")

SRC = [
("S1","AtomicLimits ALD Database (사용자가 붙여준 In/Ga/As 페이지), DOI 10.6100/alddatabase","https://www.atomiclimits.com/alddatabase/"),
("S2","Wikipedia – Trimethylindium (Shenai-Khatkhate 2008 증기압식 인용)","https://en.wikipedia.org/wiki/Trimethylindium"),
("S3","Wikipedia – Triethylindium","https://en.wikipedia.org/wiki/Triethylindium"),
("S4","Wikipedia – Trimethylgallium","https://en.wikipedia.org/wiki/Trimethylgallium"),
("S5","NIST SRD 134 – Trimethyl Gallium","https://www.nist.gov/node/431836"),
("S6","Nouryon TEGa SSG Product Data Sheet","https://www.nouryon.com/globalassets/inriver/resources/pds-tega-ssg-electronics-glo-en.pdf"),
("S7","Wikipedia – Triethylgallium","https://en.wikipedia.org/wiki/Triethylgallium"),
("S8","Indium Corp. GaCl3 Product Data Sheet","https://documents.indium.com/qdynamo/download.php?docid=3072"),
("S9","Wikipedia – Gallium(III) chloride","https://en.wikipedia.org/wiki/Gallium(III)_chloride"),
("S10","IBM Research – Vapor pressure of DEGaCl and DEAlCl","https://research.ibm.com/publications/vapor-pressure-and-vapor-composition-of-diethylgallium-chloride-and-diethylaluminum-chloride"),
("S11","Use of tertiarybutylarsine for GaAs growth, APL 50, 218 (1987)","https://doi.org/10.1063/1.97666"),
("S12","American Elements – Tertiarybutylarsine","https://www.americanelements.com/tertiarybutylarsine-4262-43-5"),
("S13","Wikipedia – Arsine","https://en.wikipedia.org/wiki/Arsine"),
("S14","NRT Arsine Quick Reference Guide (2017)","https://nrt.org/sites/2/files/Arsine%20SA%20QRG%20FINAL%202017%2004%2025.pdf"),
("S15","Dapkus et al., ONR Annual Report – Atomic Layer Epitaxy (1986), DTIC ADA171723","https://apps.dtic.mil/sti/pdfs/ADA171723.pdf"),
("S16","DTIC ADA250666 – TIPIn/TMIn OMVPE report","https://apps.dtic.mil/sti/pdfs/ADA250666.pdf"),
("S17","US Patent 4,734,514 (TEIn 열안정성 서술)","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4734514"),
("S18","Mpofu et al., Dalton Trans. 51, 4712 (2022) – In triazenide + Table 1 (In2O3 공정 정리)","https://pubs.rsc.org/en/content/articlehtml/2022/dt/d1dt03748j"),
("S19","Elam et al., InCp/O3 In2O3 ALD (Chem. Mater. 2006 원고)","https://corpora.tika.apache.org/base/docs/govdocs1/263/263968.pdf"),
("S20","Ma et al., Nanoscale Res. Lett. 13, 4 (2018) – InCp/H2O2","https://link.springer.com/doi/10.1186/s11671-017-2414-0"),
("S21","Libera, Hryn, Elam, Chem. Mater. (2011)","https://doi.org/10.1021/cm103637t"),
("S22","Maeng et al., Ceram. Int. 41, 10782 (2015) – DADI/H2O","https://scholarworks.bwise.kr/hanyang/handle/2021.sw.hanyang/155986"),
("S23","Maeng et al., J. Alloys Compd. (2015) – 액체 In 전구체/O3","https://dspace.kaist.ac.kr/handle/10203/205209"),
("S24","Kim et al. (Gordon group), Chem. Eur. J. (2018) – In amidinate/formamidinate","https://gordon.faculty.chemistry.harvard.edu/resource/kimchemistryeurojnl249525-95292018pdf"),
("S25","Me2In(EDPA) PEALD In2O3 (KAIST)","https://ssmd.kaist.ac.kr/_files/ugd/964b65_4b910d971e81472689340e32a12b189e.pdf"),
("S26","DADI vs DATI PEALD In2O3 비교 연구","https://biomed.reviewer.ly/app/publication/5057a97d-6b4f-4203-85cf-7b0bb4f12945"),
("S27","KIST – DBDMI In2O3 ALD (Nanotechnology)","https://pubs.kist.re.kr/handle/201004/150209"),
("S28","O'Donoghue et al., Dalton Trans. 46, 16551 (2017) – [Ga(NMe2)3]2/O2 plasma","https://pubs.rsc.org/en/content/articlelanding/2017/dt/c7dt03427j"),
("S29","Ramachandran et al., J. Mater. Chem. A 2, 19232 (2014) – Ga(TMHD)3 PEALD + Ga 공정 정리","https://pubs.rsc.org/en/content/getauthorversionpdf/c4ta05007j"),
("S30","Lee et al. – DMGIP ALD/MOCVD Ga2O3 (Korea Univ.)","https://scholar.korea.ac.kr/handle/2021.sw.korea/111674"),
("S31","Donmez et al., JVST A 31 (2013) – TMGa/O2 plasma","https://repository.bilkent.edu.tr/items/39f3f358-0db8-44a1-ab30-75ebaaeec3d3"),
("S32","Ilhom et al. – TEG + Ar/O2 plasma Ga2O3","https://figshare.com/articles/journal_contribution/Low-Temperature_As-Grown_Crystalline_Ga_sub_2_sub_O_sub_3_sub_Films_via_Plasma-Enhanced_Atomic_Layer_Deposition/13863999"),
("S33","Nanomaterials 12, 1510 (2022) – PEALD Ga2O3","https://mdpi.com/2079-4991/12/9/1510"),
("S34","Roberts et al., arXiv:1908.06914 – TEGa/O2 plasma α-Ga2O3","https://arxiv.org/abs/1908.06914"),
("S35","DenBaars et al., MRS Proc. (1988) – GaAs ALE TMGa/AsH3 445–485 °C","https://www.cambridge.org/core/journals/mrs-online-proceedings-library-archive/article/abs/growth-of-aigaasgaas-heterostructures-by-atomic-layer-epitaxy/A44FB5FDCB35205424E9CDE725A758C5"),
("S36","Reid, Urdianyk, Bedair, APL 59, 2397 (1991)","https://doi.org/10.1063/1.106027"),
("S37","Maa & Dapkus, J. Electron. Mater. 19, 289 (1990)","https://link.springer.com/article/10.1007/BF02651286"),
("S38","Atomic Layer Epitaxy of GaAs and InAs (MRS Proc.)","https://core-cms.cambridgecore.org/core/journals/mrs-online-proceedings-library-archive/article/atomic-layer-epitaxy-of-gaas-and-inas/DA095A7D96AB8B5DF85C3AEBAFD8D920"),
("S39","Ohno et al., APL 54, 2000 (1989) – TEGa/AsH3 ALE","https://doi.org/10.1063/1.101195"),
("S40","Yu et al., MRS Proc. (1991) – Surface chemistry of GaAs ALE","https://www.cambridge.org/core/journals/mrs-online-proceedings-library-archive/article/abs/surface-chemistry-and-mechanism-of-atomic-layer-growth-of-gaas/03E6DD8024666B29C114B82E7F6D3E23"),
("S41","Mori et al., APL 52, 27 (1988) – DEGaCl ALE","https://katalog.lib.cas.cz/KNAV/EdsRecord/edb,9825486"),
("S42","Atomic Layer Epitaxy of GaAs Using GaCl3 and AsH3","https://scilit.com/publications/a399c6619ba4ab6be168a164371058f5"),
("S43","Ishikawa et al., JJAP 31, 1716 (1992) – GaCl3/AsH3 1–2 ML/cycle","https://doi.org/10.1143/JJAP.31.1716"),
("S44","Jow et al., J. Electron. Mater. 24, 25 (1995) – TMGa/TBAs vacuum ALE","https://link.springer.com/article/10.1007/BF02659722"),
("S45","Fujii, Suemune, Yamanishi, APL (1992) – amino-As ALE","https://doi.org/10.1063/1.108132"),
("S46","Li & Tu, MRS Proc. (1996) – TDMAAs selective-area CBE","https://www.cambridge.org/core/product/60D1740EF149FB6A027C311B53C736DE"),
("S47","Ortion et al., JJAP 35, 5964 (1996) – TDMAAs in situ cleaning","https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/3109275"),
("S48","Fujitsu – InAs ALE, As 탈착 억제 (J. Cryst. Growth)","https://data.zhenzhi.com/details/1/991810063"),
("S49","J. Mater. Res. (1994) – Self-limited growth of InAs at 480 °C","https://resolve.cambridge.org/core/journals/journal-of-materials-research/article/selflimited-growth-of-inas-at-480-c/E130258426460BFBDBFDBD09C5C66C23"),
("S50","Ohtsuka et al., MRS Proc. – TMIDMEA InAs ALE","https://resolve.cambridge.org/core/journals/mrs-online-proceedings-library-archive/article/growth-of-inas-and-inas1gaasl-superlattice-quantum-well-structures-on-gaas-by-atomic-layer-epitaxy-using-trimethylindiumdimethylethylamine-adduct/E428EBA14D45887ED2D896CD02536D5E"),
("S51","Bedair et al., APL 51, 1830 (1987) – Ga-As-In-As superalloy ALE","https://doi.org/10.1063/1.98484"),
("S52","Haraguchi, Ozeki, Takeuchi – InAs/GaAs·GaP/GaAs ALE 성장 기구 (宮崎大学 紀要)","https://miyazaki-u.repo.nii.ac.jp/records/2389"),
("S53","Lum & Klingert (Bell Labs, 1989) – Low vapor pressure organoarsenic compounds","https://www.nokia.com/bell-labs/publications-and-media/publications/low-vapor-pressure-organoarsenic-compounds-as-alternatives-to-arsine-in-gaas-movpe"),
("S54","MRS Proc. review – Group V sources for OMVPE","https://core-cms.cambridgecore.org/core/journals/mrs-online-proceedings-library-archive/volume/A396D5C4794BE615B796B016BAA493F1?pageNum=2"),
("S55","US Patent 4,368,098 (As 승화점 서술)","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4368098"),
("S56","US Patent 5,270,247 (Fujitsu, InAs 350 °C / GaAs 500 °C ALE 온도 불일치)","https://patents.justia.com/patent/5270247"),
("S58","Asikainen, Ritala, Leskelä (1994) – InCl3/H2O 400·500 °C","https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_osti_scitechconnect_6734636"),
("S59","Nanomaterials 11, 2047 (2021) – Et3In/O3 ALD 115–250 °C","https://pmc.ncbi.nlm.nih.gov/articles/PMC8399107"),
("S60","Yu, APL 55, 1011 (1989) – TMGa chemisorption on GaAs(100)","https://doi.org/10.1063/1.101719"),
("S61","American Elements – Triethylindium (이전 세션 확인)","https://americanelements.com/triethylindium-923-34-2"),
("S62","ChemicalBook – InCp 34822-89-4 (이전 세션 확인)","https://chemicalbook.com/price-india/34822-89-4.htm"),
("S63","Berkala Fisika (Undip) – In(tmhd)3 (이전 세션 확인)","https://ejournal.undip.ac.id/index.php/berkala_fisika/article/view/2455"),
("S64","US Patent 9,382,618 – In amidinate/guanidinate (이전 세션 확인)","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9382618"),
("S65","American Elements – Triisobutylgallium (이전 세션 확인)","https://americanelements.com/triisobutylgallium-17150-84-4"),
("S66","Trineopentylgallium GaAs ALE (이전 세션 확인)","https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/10385455"),
("S67","ChemicalBook DEGaCl + hot-wall MOVPE (이전 세션 확인)","https://chemicalbook.com/ProductChemicalPropertiesCB0366335_EN.htm"),
("S68","Rouf et al., J. Mater. Chem. C 8, 8457 (2020) – Ga(NMe2)3/NH3 plasma GaN","https://pubs.rsc.org/en/content/articlehtml/2020/tc/d0tc02085k"),
("S69","J. Mater. Chem. C (2016) GaCl3/(Et3Si)3As GaAs ALD + US Patent 10,208,379 (이전 세션 확인)","https://pubs.rsc.org/en/Content/ArticleLanding/2016/TC/C5TC03079J"),
("S70","TBAs 분해·MOVPE 온도 (J. Soc. Mater. Sci. Japan 56, 880 등, 이전 세션 확인)","https://www.jstage.jst.go.jp/article/jsms/56/9/56_9_880/_article/-char/en"),
("S71","Miyazaki Univ. repository – TDMAAs/TMGa ALE 500 °C (이전 세션 확인)","https://miyazaki-u.repo.nii.ac.jp/records/2510"),
("S72","ChemicalBook – TDMAAs (이전 세션 확인)","https://m.chemicalbook.com/ChemicalProductProperty_EN_CB9686003.htm"),
("S73","ChemicalBook – Arsine (분해 개시 230–240 °C 서술)","https://chemicalbook.com/ChemicalProductProperty_EN_CB4375809.htm"),
("S74","DTIC ADA200887 – (Me3Si)3As (이전 세션 확인)","https://apps.dtic.mil/sti/tr/pdf/ADA200887.pdf"),
("S75","Wikipedia – Trimethylarsine (이전 세션 확인)","https://en.wikipedia.org/wiki/Trimethylarsine"),
("S76","MRS Proc. – Atmospheric-pressure OMCVD of GaAs using triethylarsenic (이전 세션 확인)","https://resolve.cambridge.org/core/journals/mrs-online-proceedings-library-archive/article/abs/atmospheric-pressure-omcvd-growth-of-gaas-using-triethylarsenic-and-alkylgallium-organometallic-precursors/A2678E781DF6597EF2E06EDFCCD0DA01"),
("S77","US Patent 4,900,855 – Diethylarsine (이전 세션 확인)","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/4900855"),
("S78","MRS Proc. – Gas phase and surface reactions of organometallic arsenic sources (이전 세션 확인)","https://www.cambridge.org/core/journals/mrs-online-proceedings-library-archive/article/gas-phase-and-surface-reactions-of-organometallic-arsenic-sources/E7A40484A3618FBCB711E5CA461EEE53"),
("S79","OSHA Occupational Chemical Database – Phosphine","https://www.osha.gov/chemicaldata/667"),
("S80","OSHA Method 1003 – Phosphine","https://osha.gov/sites/default/files/methods/osha-1003.pdf"),
("S81","ChemicalBook – Phosphine (분해 온도 서술)","https://chemicalbook.com/ChemicalProductProperty_IN_CB8716837.htm"),
("S82","Wikipedia – Phosphine (Kiwix 사본)","https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Phosphine"),
("S83","Li, Larsen, Buchan, Stringfellow, J. Electron. Mater. 18, 457 (1989) – Pyrolysis of TBP","https://springerlink.bibliotecabuap.elogim.com/content/pdf/10.1007/BF02657995.pdf"),
("S84","ChemicalBook – tert-Butylphosphine 2501-94-2","https://m.chemicalbook.com/ChemicalProductProperty_EN_CB4184281.htm"),
("S85","UCC – Gas phase monitoring under InP MOVPE (TBP/TMIn FTIR)","https://research.ucc.ie/en/publications/gas-phase-monitoring-of-reactions-under-inp-movpe-growth-conditio/"),
("S86","J. Electron. Mater. 18, 355 (1989) – InP OMVPE with TMIn/TBP","https://link.springer.com/article/10.1007/BF02657983"),
("S87","Otsuka, Nishizawa 외 – InP self-limiting growth, TEIn/TBP UHV","https://www.taylorfrancis.com/chapters/edit/10.1201/9781003063100-86/self-limiting-submonolayer-growth-inp-alternative-triethylindium-tertiarybutylphosphine-supply-ultra-high-vacuum-nobuyuki-otsuka-jun-ichi-nishizawab-hideyuki-kikuchib-yutaka-oyamac"),
("S88","Nanoscale (2025) d5nr00457h 서론 – P 전구체 정리 (TBP·TDMAP >320 °C)","https://pubs.rsc.org/en/content/articlepdf/2025/nr/d5nr00457h"),
("S89","Charvot et al. (2022) – tris(trialkylsilyl)phosphides in ALD (발표 초록)","https://fcht.upce.cz/en/publikace-detail/39887505"),
("S90","Univ. Pardubice – 금속 인화물 P 전구체 서술 (TMS3P Co2P)","https://fcht.upce.cz/publikace-detail/39891577"),
("S91","Harvard, MRS Proc. – InP from indium halides and P(SiMe3)3","https://www.cambridge.org/core/journals/mrs-online-proceedings-library-archive/article/abs/synthesis-of-inp-drom-indium-halides-and-tristrimethylsilylphosphine/5CDD6E03407A55EF4684595CC40DCE03"),
("S92","Appl. Surf. Sci. 619, 156727 (2023) – GaP PE-ALD TEG/tri-TBP/atomic H","https://doi.org/10.1016/j.apsusc.2023.156727"),
("S93","US Patent 6,020,253 – tertiarybutylbis(dimethylamino)phosphine","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6020253"),
("S94","Choi et al., JVST A 11, 626 (1993) – GaP remote PECVD","https://acnpsearch.tweb-dev.unibo.it/singlejournalindex/1719015"),
("S95","Nanoscale (2025) – TiP ALD with TMT3P/TiCl4","https://fcht.upce.cz/publikace-detail/39891860"),
("S96","JVST A (2022) – O2 plasma exposure time in Ga2O3 PEALD (TMGa)","https://bvbvf1.bib-bvb.de/vufind/PrimoRecord/cdi_scitation_primary_10_1116_6_0001207"),
("S97","Sakuma et al., J. Appl. Phys. 68, 5660 (1990) – TMGa/EtMe2Ga/TEGa ALE 비교","https://katalog.lib.cas.cz/KNAV/EdsRecord/edb,7644199"),
("S98","US Patent 5,438,952 – TEGDEA/TMIDMEA ALE (Fujitsu)","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5438952"),
("S99","Tran et al., APL 62, 2375 (1993) – HRXRD self-limiting InP·InAs/InP ALE","https://publications.polymtl.ca/70714/"),
("S100","Sakuma et al., JJAP 27, L2189 (1988) – InP self-limited growth","https://doi.org/10.1143/jjap.27.l2189"),
("S101","US Patent 5,166,092 – ALE apparatus (InP 320–440 °C)","https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5166092"),
("S102","P. L. Liu – InP by alternate supply MOCVD (초록)","https://www.sciencegate.app/document/10.1557/proc-449-85"),
("S103","NTT – SPA study of TMIn/PH3 pyrolysis on InP(001)","https://data.zhenzhi.com/details/1/1004327906"),
("S104","J. Korean Phys. Soc. 34 (1999) – InP ALE SPA","https://inis.iaea.org/records/1d699-bdm91"),
("S105","Uvarov et al., St. Petersburg Polytech. Univ. J. Phys. Math. 18 (2025) – InP PE-ALD","https://physmath.spbstu.ru/en/article/2025.82.49"),
("S106","Sakuma, Kodama, Ozeki, APL 56, 827 (1990) – ALE of GaP","https://doi.org/10.1063/1.102675"),
("S107","Gudovskikh et al., JVST A 36 (2018) – Low-T PE deposition of GaP on Si","https://hal-centralesupelec.archives-ouvertes.fr/hal-01777504"),
("S108","Morozov et al., J. Phys. Conf. Ser. 741 (2016) – Thin film GaP","https://hal-centralesupelec.archives-ouvertes.fr/hal-02404610"),
("S109","Gudovskikh et al., J. Renew. Sustain. Energy 10 (2018) – Si-doped GaP PE-ALD","https://hal.archives-ouvertes.fr/hal-01738008"),
("S110","Ozeki et al., JVST B 8, 741 (1990) – GaAs-GaP SLS by ALE","https://data.zhenzhi.com/details/1/1008049075"),
("S111","Sakuma, PhD thesis, Osaka Univ. (1997) – ALE of III-V (InGaAs·InGaP PJE)","https://ir.library.osaka-u.ac.jp/repo/ouka/all/2668/13490_Dissertation.pdf"),
]

# ---------------------------------------------------------------- styles
thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HFILL = PatternFill("solid", start_color="1F3864")
HFONT = Font(name=FONT, bold=True, color="FFFFFF", size=10)
BFONT = Font(name=FONT, size=10)
CALC = PatternFill("solid", start_color="EAF1DD")
INPUT = PatternFill("solid", start_color="FFFF00")
WARN = PatternFill("solid", start_color="FCE4D6")
WRAP = Alignment(wrap_text=True, vertical="top")

def style_sheet(ws, headers, calc_cols=()):
    calc_idx = {headers.index(c) + 1 for c in calc_cols if c in headers}
    for c in ws[1]:
        c.font = HFONT; c.fill = HFILL; c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[1].height = 42
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = BFONT; c.border = BORDER; c.alignment = WRAP
            if c.column in calc_idx and c.fill.start_color.rgb in (None, "00000000"):
                c.fill = CALC
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    for i in range(1, len(headers) + 1):
        if ws.column_dimensions[get_column_letter(i)].width in (None, 13.0):
            ws.column_dimensions[get_column_letter(i)].width = 13

wb = Workbook()

# ---------------- README
ws = wb.active; ws.title = "README"
readme = [
 ("InGaAs(P) 공정 설계용 In·Ga 전구체 / As·P 반응물 데이터베이스 v2", True),
 ("작성 2026-11-10 · 기반: AtomicLimits ALD Database(붙여주신 In/Ga/As 페이지) + 문헌 확인 + 이전 세션(2026-11-09) 확인 데이터", False),
 ("", False),
 ("■ 시트 구성", True),
 ("In_O-free / In_O함유 / Ga_O-free / Ga_O함유 : 전구체 1개 = 1행. 분자식·계산 특성·물성·안정성·공정 요약", False),
 ("As_반응물 (11종) / P_반응물 (8종) : 분자식·As(P) 함량·V–H 결합 수·물성·열분해·독성·C 혼입·공정 메모", False),
 ("공정기록 : 공정 1건 = 1행. 온도 창·GPC + 기판·반응기/압력·소스 온도·펄스 순서·결정성·조성/불순물·막 물성 (확인 못 한 값은 빈칸)", False),
 ("슈퍼사이클_매칭 : 이원계 공정 조합별 온도 창 겹침 계산 (InAs/GaAs, InAs/InP, InP/GaP)", False),
 ("상수 / 출처 : 원자량, 출처 목록(S번호)", False),
 ("", False),
 ("■ O 분류 기준", True),
 ("전구체 분자 안에 O 원자가 있으면 'O함유'. 반응물(H2O/O3/O2 plasma)의 O는 분류 기준이 아님 — 산화물 공정은 전구체 열안정 상한·반응성 근거로 함께 실음.", False),
 ("", False),
 ("■ 색 범례", True),
 ("연녹색 열 = 수식 계산값 (원소 수를 고치면 자동 갱신) · 노란 셀 = 입력값 · 살구색 셀 = 추정·모호 항목", False),
 ("", False),
 ("■ 주의", True),
 ("1) AtomicLimits 원본은 JavaScript 앱이라 직접 수집 불가 → 붙여주신 목록 사용. In·Ga 페이지는 In2S3·GaN에서 잘림. As 페이지는 완전. P 페이지는 제공되지 않아 P 반응물·인화물 공정은 문헌에서만 수집 (AtomicLimits 문헌 열이 '—').", False),
 ("2) 물성(mp, bp, 증기압, CAS)은 확인된 값만 입력. 판매처 값·2차 인용은 셀 안에 표기.", False),
 ("3) 공정 온도 '창'과 '보고 온도'는 비고에 구분. 단일 온도 보고는 Tmin=Tmax.", False),
 ("4) III-V ALE 문헌 대부분은 1980–90년대 MOVPE형 반응기(H2 캐리어) 기준 — 일반 ALD 장비로 옮길 때 퍼지·노출 재검증 필요.", False),
 ("5) 'In(dpguan)3', 'In(triaz)3' 리간드 대응은 추정, 'InMe2(NtBu(CH2)2(CH3)2OMe)'는 분자식 계산 보류.", False),
 ("6) 이천 팹 규제 관련 메모는 같은 폴더의 README.md 'Regulatory basis' 절 참고 (이전 세션 정리).", False),
]
for i, (t, b) in enumerate(readme, 1):
    c = ws.cell(row=i, column=1, value=t)
    c.font = Font(name=FONT, size=12 if i == 1 else 10, bold=b)
    c.alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 140
r = len(readme) + 2
ws.cell(row=r, column=1, value="증기압 계산 온도 (°C)").font = Font(name=FONT, bold=True, size=10)
ws.cell(row=r, column=2, value=20).fill = INPUT
ws.cell(row=r, column=2).font = Font(name=FONT, color="0000FF", size=10)
ws.column_dimensions["B"].width = 12
VPT = f"README!$B${r}"
ws.cell(row=r, column=3, value="← 전구체 시트의 '증기압 @ 설정온도' 열이 이 값을 사용").font = BFONT

# ---------------- constants
wc = wb.create_sheet("상수")
wc.append(["원소", "원자량 (g/mol)", "출처"])
for e in EL:
    wc.append([e, AW[e], "IUPAC 표준 원자량 (관용값)"])
for row in wc.iter_rows():
    for c in row:
        c.font = BFONT; c.border = BORDER
for c in wc[1]:
    c.font = HFONT; c.fill = HFILL
wc.column_dimensions["A"].width = 8; wc.column_dimensions["B"].width = 16; wc.column_dimensions["C"].width = 30
AWREF = {e: f"상수!$B${i+2}" for i, e in enumerate(EL)}

# ---------------- precursor sheets
PH = ["ID", "AtomicLimits 표기", "약어", "정식명", "금속", "금속 산화수", "분자당 금속 수",
      "분자식 (계산용)"] + [f"n({e})" for e in PREC_EL] + [
      "분자량 (g/mol)", "금속 함량 (wt%)", "C/금속 비", "H/금속 비", "C+N+O+Si (리간드 중원자 수)",
      "헤테로원자 플래그", "리간드 계열", "리간드 구성", "결합 (M–X)", "Donor/킬레이트", "β-H 보유 알킬",
      "상온 상태", "녹는점 (°C)", "끓는점 (°C)", "증기압식 A (log P[Torr]=B−A/T)", "증기압식 B",
      "증기압 @ 설정온도 (Torr)", "증기압·공급 메모", "열안정성·분해·공정 메모", "자연발화/반응성", "CAS",
      "분자식 확실도", "출처"]
COL = {h: i + 1 for i, h in enumerate(PH)}
def L(h):
    return get_column_letter(COL[h])

def write_prec(title, rows):
    ws = wb.create_sheet(title)
    ws.append(PH)
    for p in rows:
        r = ws.max_row + 1
        cnt = F(p["f"]) if p["f"] else None
        vals = [p["id"], p["nota"], p["abbr"], p["name"], p["metal"], p["ox"], p["nM"], p["f"] or "계산 보류"]
        vals += [None if cnt is None else cnt.get(e, 0) for e in PREC_EL]
        ws.append(vals + [None] * (len(PH) - len(vals)))
        if cnt is not None:
            ws.cell(row=r, column=COL["분자량 (g/mol)"],
                    value="=" + "+".join(f"{L('n(' + e + ')')}{r}*{AWREF[e]}" for e in PREC_EL))
            ws.cell(row=r, column=COL["금속 함량 (wt%)"],
                    value=f"={L('n('+p['metal']+')')}{r}*{AWREF[p['metal']]}/{L('분자량 (g/mol)')}{r}")
            ws.cell(row=r, column=COL["C/금속 비"], value=f"={L('n(C)')}{r}/{L('분자당 금속 수')}{r}")
            ws.cell(row=r, column=COL["H/금속 비"], value=f"={L('n(H)')}{r}/{L('분자당 금속 수')}{r}")
            ws.cell(row=r, column=COL["C+N+O+Si (리간드 중원자 수)"],
                    value=f"={L('n(C)')}{r}+{L('n(N)')}{r}+{L('n(O)')}{r}+{L('n(Si)')}{r}")
            o, n, cl, br, i_, si = (f"{L('n('+x+')')}{r}" for x in ["O", "N", "Cl", "Br", "I", "Si"])
            ws.cell(row=r, column=COL["헤테로원자 플래그"],
                    value=(f'=IF({o}>0,"O ","")&IF({n}>0,"N ","")&IF({cl}+{br}+{i_}>0,"Hal ","")'
                           f'&IF({si}>0,"Si ","")&IF({o}+{n}+{cl}+{br}+{i_}+{si}=0,"C,H만","")'))
        else:
            for h in ["분자량 (g/mol)", "금속 함량 (wt%)", "C/금속 비", "H/금속 비", "C+N+O+Si (리간드 중원자 수)", "헤테로원자 플래그"]:
                ws.cell(row=r, column=COL[h], value="—")
        txt = {"리간드 계열": p["lig_class"], "리간드 구성": p["lig"], "결합 (M–X)": p["bonds"],
               "Donor/킬레이트": p["donor"], "β-H 보유 알킬": p["betaH"], "상온 상태": p["state"],
               "녹는점 (°C)": p["mp"], "끓는점 (°C)": p["bp"], "증기압·공급 메모": p["vp_note"],
               "열안정성·분해·공정 메모": p["thermal"], "자연발화/반응성": p["pyro"], "CAS": p["cas"],
               "분자식 확실도": p["cert"], "출처": p["src"]}
        for h, v in txt.items():
            ws.cell(row=r, column=COL[h], value=v if v != "" else None)
        if p["vpA"] is not None:
            ws.cell(row=r, column=COL["증기압식 A (log P[Torr]=B−A/T)"], value=p["vpA"])
            ws.cell(row=r, column=COL["증기압식 B"], value=p["vpB"])
            ws.cell(row=r, column=COL["증기압 @ 설정온도 (Torr)"],
                    value=f"=10^({L('증기압식 B')}{r}-{L('증기압식 A (log P[Torr]=B−A/T)')}{r}/({VPT}+273.15))")
        if not p["cert"].startswith("확정"):
            ws.cell(row=r, column=COL["분자식 확실도"]).fill = WARN
            ws.cell(row=r, column=COL["분자식 (계산용)"]).fill = WARN
    style_sheet(ws, PH, calc_cols=["분자량 (g/mol)", "금속 함량 (wt%)", "C/금속 비", "H/금속 비",
                                   "C+N+O+Si (리간드 중원자 수)", "헤테로원자 플래그", "증기압 @ 설정온도 (Torr)"])
    for rr in range(2, ws.max_row + 1):
        ws.cell(row=rr, column=COL["분자량 (g/mol)"]).number_format = "0.00"
        ws.cell(row=rr, column=COL["금속 함량 (wt%)"]).number_format = "0.0%"
        ws.cell(row=rr, column=COL["C/금속 비"]).number_format = "0.0"
        ws.cell(row=rr, column=COL["H/금속 비"]).number_format = "0.0"
        ws.cell(row=rr, column=COL["증기압 @ 설정온도 (Torr)"]).number_format = "0.000"
    widths = {"ID": 8, "AtomicLimits 표기": 24, "약어": 13, "정식명": 34, "분자식 (계산용)": 15,
              "리간드 계열": 22, "리간드 구성": 22, "결합 (M–X)": 22, "Donor/킬레이트": 16, "β-H 보유 알킬": 16,
              "증기압·공급 메모": 38, "열안정성·분해·공정 메모": 50, "분자식 확실도": 30, "출처": 16,
              "헤테로원자 플래그": 14, "녹는점 (°C)": 14, "끓는점 (°C)": 18, "자연발화/반응성": 20, "CAS": 12}
    for h, w in widths.items():
        ws.column_dimensions[L(h)].width = w
    for e in PREC_EL:
        ws.column_dimensions[L("n(" + e + ")")].width = 6

inP = [p for p in P if p["metal"] == "In"]; gaP = [p for p in P if p["metal"] == "Ga"]
write_prec("In_O-free", [p for p in inP if not p["oxygen"]])
write_prec("In_O함유", [p for p in inP if p["oxygen"]])
write_prec("Ga_O-free", [p for p in gaP if not p["oxygen"]])
write_prec("Ga_O함유", [p for p in gaP if p["oxygen"]])

# ---------------- group-V reactant sheets
def write_v(title, rows, V):
    els = ["C", "H", "N", "F", "Si", "Sn", V]
    AH = ["ID", "표기", "약어", "정식명", "분자식", "AtomicLimits 수록"] + [f"n({e})" for e in els] + [
          "분자량 (g/mol)", f"{V} 함량 (wt%)", f"{V}–H 결합 수", "계열", "결합", "상온 상태", "녹는점 (°C)", "끓는점 (°C)",
          "증기압", "열분해 특성", "독성·안전", "C/Si 혼입", "공정 메모", "CAS", "출처"]
    ws = wb.create_sheet(title)
    ws.append(AH)
    ac = {h: i + 1 for i, h in enumerate(AH)}
    for a in rows:
        r = ws.max_row + 1
        cnt = F(a["f"])
        ws.append([a["id"], a["nota"], a["abbr"], a["name"], a["f"], a["inDB"]] + [cnt.get(e, 0) for e in els]
                  + [None, None, a["VH"], a["cls"], a["bonds"], a["state"] or None, a["mp"] or None, a["bp"] or None,
                     a["vp"] or None, a["decomp"] or None, a["tox"] or None, a["carbon"] or None, a["note"] or None,
                     a["cas"] or None, a["src"]])
        cols = {e: get_column_letter(ac["n(" + e + ")"]) for e in els}
        ws.cell(row=r, column=ac["분자량 (g/mol)"], value="=" + "+".join(f"{cols[e]}{r}*{AWREF[e]}" for e in els))
        ws.cell(row=r, column=ac[f"{V} 함량 (wt%)"],
                value=f"={cols[V]}{r}*{AWREF[V]}/{get_column_letter(ac['분자량 (g/mol)'])}{r}")
        if a["inDB"] == "미수록":
            ws.cell(row=r, column=ac["AtomicLimits 수록"]).fill = WARN
    style_sheet(ws, AH, calc_cols=["분자량 (g/mol)", f"{V} 함량 (wt%)"])
    for rr in range(2, ws.max_row + 1):
        ws.cell(row=rr, column=ac["분자량 (g/mol)"]).number_format = "0.00"
        ws.cell(row=rr, column=ac[f"{V} 함량 (wt%)"]).number_format = "0.0%"
    for h, w in {"표기": 22, "정식명": 30, "열분해 특성": 46, "독성·안전": 40, "공정 메모": 50, "C/Si 혼입": 28, "증기압": 24,
                 "결합": 18, "계열": 18, "출처": 22, "상온 상태": 16, "녹는점 (°C)": 14, "끓는점 (°C)": 16}.items():
        ws.column_dimensions[get_column_letter(ac[h])].width = w
    for e in els:
        ws.column_dimensions[get_column_letter(ac["n(" + e + ")"])].width = 6

write_v("As_반응물", A, "As")
write_v("P_반응물", PX, "P")

# ---------------- process records
oxy = {p["nota"]: p["oxygen"] for p in P}
oxy.update({"InMe3 + GaMe3": False, "GaMe3 + InEt3": False, "[Ga(NMe2)3]2": False, "TEGa/TMIn": False,
            "InMe3·NMe2Et (TMIDMEA, DB 미수록)": False, "TEGa·DEA adduct (TEGDEA, DB 미수록)": False,
            "In(iPrAMD)3 (DB 표기 외)": False, "InX3 (X=Cl, Br, I)": False})
RH = ["막", "금속(또는 주) 전구체", "반응물 B", "반응물 C", "전구체 O 함유", "반응물에 O 포함", "V족 원소",
      "공정 유형", "Tmin (°C)", "Tmax (°C)", "창 폭 (°C)", "GPC / 성장률",
      "기판", "반응기·압력·캐리어", "소스 온도", "펄스·퍼지 순서", "결정성·상", "조성·불순물", "막 물성",
      "비고", "AtomicLimits 문헌", "출처"]
wp = wb.create_sheet("공정기록")
wp.append(RH)
def vgroup(film, b):
    t = film + " " + b
    if "As" in film: return "As"
    if "P" in film.replace("Pulse", "") and "TiP" not in film: return "P"
    return "—"
for d in PR:
    r = wp.max_row + 1
    po = oxy.get(d["pre"])
    reacO = any(k in (d["b"] + " " + d["c"]) for k in ["H2O", "O3", "O2", "N2O"])
    wp.append([d["film"], d["pre"], d["b"], d["c"] or None, ("예" if po else "아니오") if po is not None else "—",
               "예" if reacO else "아니오", vgroup(d["film"], d["b"]), d["typ"],
               d["tmin"] if d["tmin"] != "" else None, d["tmax"] if d["tmax"] != "" else None, None,
               d["gpc"] or None, d["sub"] or None, d["reactor"] or None, d["srcT"] or None, d["seq"] or None,
               d["cryst"] or None, d["comp"] or None, d["props"] or None, d["note"] or None,
               d["refs"] or None, d["src"] or "미확인 (AtomicLimits 목록만)"])
    wp.cell(row=r, column=11, value=f'=IF(AND(ISNUMBER(I{r}),ISNUMBER(J{r})),J{r}-I{r},"")')
style_sheet(wp, RH, calc_cols=["창 폭 (°C)"])
for h, w in {"막": 14, "금속(또는 주) 전구체": 26, "반응물 B": 16, "공정 유형": 18, "GPC / 성장률": 24,
             "기판": 22, "반응기·압력·캐리어": 30, "소스 온도": 18, "펄스·퍼지 순서": 32, "결정성·상": 26,
             "조성·불순물": 26, "막 물성": 30, "비고": 46, "AtomicLimits 문헌": 24, "출처": 16}.items():
    wp.column_dimensions[get_column_letter(RH.index(h) + 1)].width = w

# ---------------- supercycle matching
wm = wb.create_sheet("슈퍼사이클_매칭")
MH = ["조합", "목표 막", "공정 A", "A Tmin", "A Tmax", "공정 B", "B Tmin", "B Tmax",
      "겹침 하한 (°C)", "겹침 상한 (°C)", "겹침 폭 (°C)", "판정", "근거·주의"]
wm.append(MH)
combos = [
 ("C1", "InGaAs", "InAs: InMe3 / AsH3 (표준)", 340, 400, "GaAs: GaMe3 / AsH3 (표준)", 445, 485,
  "표준 조건에선 단일 온도 불가. Fujitsu 특허도 InAs 350 °C / GaAs 500 °C 불일치를 문제로 기술", "S38; S48; S35; S56"),
 ("C2", "InGaAs", "InAs: InMe3 / AsH3 (표준)", 340, 400, "GaAs: GaMe3 / AsH3 (TMGa 10 s 장노출)", 400, 400,
  "400 °C 한 점에서만 접함. InAs 쪽은 400 °C에서 AsH3 후 퍼지 <0.1 s 요구 → 공정 마진 거의 없음", "S38; S48"),
 ("C3", "InGaAs", "InAs: InMe3·NMe2Et (TMIDMEA) / AsH3", 350, 500, "GaAs: GaMe3 / AsH3 (표준)", 445, 485,
  "(InAs)1(GaAs)1을 460 °C 단일 온도에서 실증. TMIDMEA는 DB의 DATI(InMe3·NMe2Bu)와 다른 adduct", "S50; S35"),
 ("C4", "InGaAs", "InAs: InMe3 / AsH3 (회전 기판)", 480, 480, "GaAs: GaMe3 / AsH3 (표준)", 445, 485,
  "InAs 480 °C self-limiting은 회전 기판·전용 서셉터 조건", "S49; S35"),
 ("C5", "InGaAs", "InAs: InMe3 / AsH3 (표준)", 340, 400, "GaAs: GaCl3 / AsH3", 200, 500,
  "온도는 겹치지만 GaCl3는 300 °C 이상에서 1→2 ML/cycle → Ga 쪽 self-limiting 깨질 수 있음. Cl 부산물 관리", "S38; S48; S42; S43"),
 ("C6", "InGaAs", "InAs: InMe3 / AsH3 (표준)", 340, 400, "GaAs: GaMe3 / AsH3 (특수 반응기)", 450, 700,
  "GaAs 창이 넓어도 InAs 상한(400 °C)과 겹치지 않음", "S38; S48; S36"),
 ("C7", "InGaAs", "InAs: InMe3 / AsH3 (표준)", 340, 400, "GaAs: GaNp3 / tBuAsH2", 430, 500,
  "겹치지 않음 (As 원이 다른 점도 유의)", "S38; S48; S66"),
 ("C8", "InAsP", "InAs: InMe3 / AsH3 (표준)", 340, 400, "InP: InMe3 / PH3 (특수 장치)", 320, 440,
  "겹침 있음. 같은 TMIn이라 In 단계 공유 가능. 단 InP 320–440 °C는 특수 분사 장치 조건, 일반 장치는 InP ALE 350 °C·<1 ML/cycle 보고", "S38; S48; S101; S103"),
 ("C9", "InAsP", "InAs: InMe3 / AsH3 (표준)", 340, 400, "InP: InEt3 / tBuPH2 (UHV)", 320, 340,
  "340 °C 한 점에서만 접함; In 전구체가 서로 다름 (TMIn vs TEIn)", "S38; S48; S87"),
 ("C10", "InGaP", "InP: InMe3 / PH3 (PE-ALD)", 250, 350, "GaP: GaMe3 / PH3 + H2 plasma (PE-ALD)", 250, 380,
  "같은 그룹·같은 장비 계열(Si 기판). GaP는 저전력에서 비정질, 과잉 P 제거용 H2 plasma 단계 필요", "S105; S107"),
]
for (cid, tgt, ina, a1, a2, gaa, b1, b2, note, src) in combos:
    r = wm.max_row + 1
    wm.append([cid, tgt, ina, a1, a2, gaa, b1, b2, None, None, None, None, f"{note} [{src}]"])
    wm.cell(row=r, column=9, value=f"=MAX(D{r},G{r})")
    wm.cell(row=r, column=10, value=f"=MIN(E{r},H{r})")
    wm.cell(row=r, column=11, value=f"=J{r}-I{r}")
    wm.cell(row=r, column=12, value=f'=IF(K{r}>0,"겹침 있음",IF(K{r}=0,"한 점에서만 접함","겹침 없음"))')
style_sheet(wm, MH, calc_cols=["겹침 하한 (°C)", "겹침 상한 (°C)", "겹침 폭 (°C)", "판정"])
for col in (4, 5, 7, 8):
    for rr in range(2, wm.max_row + 1):
        wm.cell(row=rr, column=col).font = Font(name=FONT, color="0000FF", size=10)
for h, w in {"조합": 6, "목표 막": 10, "공정 A": 30, "공정 B": 34, "판정": 16, "근거·주의": 80}.items():
    wm.column_dimensions[get_column_letter(MH.index(h) + 1)].width = w
n = wm.max_row + 2
notes = [
 "■ 읽는 법: 파란 숫자는 문헌 온도(입력값) — 새 공정 조합을 행으로 추가하면 겹침이 자동 계산됨.",
 "■ TEGa/AsH3는 ALE 조건이 좁아 정량 창이 확인되지 않아 제외. TEGa+TDMAAs는 ALE 범위가 크게 확장된다는 보고(S45)가 있으나 수치 미확인.",
 "■ TMGa/TBAs vacuum ALE는 창 폭 70 °C만 확인(S44), GaP ALE(TMGa/PH3, S106)는 온도 미확인 → 원문 확인 시 행 추가 권장.",
 "■ 이원계 각각이 한 온도에서 포화해도 이종 계면(격자 불일치·표면 형상)에서 self-limiting이 달라질 수 있음 (S52).",
]
for i, t in enumerate(notes):
    c = wm.cell(row=n + i, column=1, value=t); c.font = BFONT
    wm.merge_cells(start_row=n + i, start_column=1, end_row=n + i, end_column=13)
    c.alignment = Alignment(wrap_text=True, vertical="top"); wm.row_dimensions[n + i].height = 30

# ---------------- sources
wsrc = wb.create_sheet("출처")
wsrc.append(["ID", "출처", "URL"])
for s in SRC:
    wsrc.append(list(s))
style_sheet(wsrc, ["ID", "출처", "URL"])
wsrc.column_dimensions["A"].width = 7; wsrc.column_dimensions["B"].width = 80; wsrc.column_dimensions["C"].width = 90
for rr in range(2, wsrc.max_row + 1):
    c = wsrc.cell(row=rr, column=3); c.hyperlink = c.value
    c.font = Font(name=FONT, size=10, color="0563C1", underline="single")

# sanity: every cited S-id exists
import re as _re
ids = {s[0] for s in SRC}
cited = set()
for blob in [p["src"] for p in P] + [a["src"] for a in A + PX] + [d["src"] for d in PR] + [c[-1] for c in combos]:
    cited |= set(_re.findall(r"S\d+", blob))
missing = cited - ids
assert not missing, f"missing sources: {missing}"

import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "InGaAsP_precursor_DB.xlsx")
wb.save(out)
print("saved", out, len(P), "precursors", len(A), "As", len(PX), "P", len(PR), "processes", len(SRC), "sources")
