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
