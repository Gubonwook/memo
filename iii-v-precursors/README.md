# In/Ga precursors and As reactants for InAs/GaAs deposition (ALD/CVD/ALE)

Only compounds with documented deposition use are listed. Property values come from the linked sources
(some are vendor values and differ between suppliers). Compiled 2026-11-09.

- `ga_precursors.csv` - Ga precursors
- `in_precursors.csv` - In precursors
- `as_reactants.csv` - As reactants

Not included (deposition use found, but physical properties not verified): GaNp3 is listed with growth temperature only; GaEt2Me, GaCl, GaBr, GaI, InClMe2, InCl, EtAsH2, PhAsH2 have no verified data.
No verified self-limiting ALD of InAs found; GaAs ALD is reported only for GaCl3 + (Et3Si)3As.

Growth temperatures: `growth_temp_C` is the headline range per material/process; `growth_temp_basis` gives the system
(ALD/ALE/MOVPE, co-reactant). Values depend strongly on reactor and co-reactant, so use them as starting points.
"not verified" means no number was found in the sources checked.

Icheon fab usability (`fab_usability_icheon`, As table only): rough judgment from general hazard properties
(toxicity, pyrophoricity/flammability, vapor pressure, by-products, supply). It is NOT an official approval;
actual use requires internal EHS / process-integration review.

## Regulatory basis for Icheon (As reactants) - checked 2026-11-09
Found in sources (secondary sources noted):
- Arsine: listed as 유독물질 / 사고대비물질 (ChemicalBook KR, secondary source; official 화관법 table not opened). 사고대비물질 handling facilities need a 화학사고예방관리계획서 (Shin&Kim newsletter 1475).
- 산업안전보건법: 비소 및 그 무기화합물 TWA 0.01 mg/m3 (KOSHA GUIDE H-120-2020 context; ChemicalBook MSDS); arsine TLV-TWA 0.05 ppm (ACGIH/OSHA).
- 수질: 비소 배출허용기준 0.05 mg/L (strictest column) to 0.25 mg/L (law.go.kr 별표, 2020 기준; which column applies to Icheon not confirmed).
- 수도권정비계획법: Icheon is entirely 자연보전권역 with 팔당 특별대책지역 overlap; large-company advanced-fab expansion capped (1,000 m2 in 2012 sources). SK hynix grandfathered building-area capacity (news).
- 대기환경보전법: 비소 및 그 화합물 is a 특정대기유해물질 (KOSAE 2013); numeric emission limits not checked.
Not verified: TBAs/TDMAAs/silylarsine legal classification, official 규정수량 for arsine, SK hynix internal approval status.

### Water-protection rules (added 2026-11-09)
- 수질 및 수생태계법 제33조: 폐수배출시설 중 특정수질유해물질(비소화합물 포함 25종) 발생 시설, 특별대책지역 내 시설, 배출시설 설치제한지역(상수원보호구역 상류 유하거리 10 km 등)은 허가 대상 (state.gwd.go.kr summary). Process change that newly generates a 특정수질유해물질 also triggers permit.
- 2014 시행령 개정: 먹는물 수준 기준 미만으로 발생하는 시설은 허가 제외 및 제한지역 입지 허용 (news, 산업일보). The numeric threshold was not checked.
- 한강수계법: 수변구역에서 특정수질유해물질 사용/발생 공장 입지 제한. Icheon is within 팔당 특별대책지역 (1998 환경부 문서).
- Context: 2026-10 경기도 조사에서 이천 SK하이닉스 방류 하천(죽당천) 염소·황산이온이 FAO 권고 초과 -> 경기도가 기준 마련 건의. Water discharge from Icheon is currently politically sensitive.
- Implication: the water-law burden is driven by total As generated in wastewater, not by which As source is used. Small-quantity ALD use is favorable, but this is my inference, not verified against the threshold.
