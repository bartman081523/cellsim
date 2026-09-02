# iter-16: Orch-OR unter der Hagan-Parametrisierung — korrigierte Nachrechnung

## Kontext (CORRECTION-Log — unsere eigenen iter-7-Fehler)

1. **iter-7's E_G-Formel war dimensional invalid**: E_G = ħ²/(G·m²·τ)
   hat Einheit J·s/m, nicht J. Das berechnete "E_G = 187 J" für ein
   Protein und τ_collapse = 5.66e-37 s sind Artefakte.
2. **iter-7's Kriterium war invertiert**: Orch-OR braucht τ_OR < τ_dec
   (OR muss VOR der Umgebungs-Dekohärenz greifen); iter-7 wertete
   τ_collapse > τ_decoherence als "viable".

Korrekte Penrose-Formel: **E_G = G·(ΔM)²/a; τ_OR = ħ/E_G**
(Penrose 1994; Hagan et al. 2002). Kollektiv korreliert: E_G ∝ N².

## Vorab registrierte Kriterien

OPEN_SUBSTRATE: viable (f, a, N, S)-Region mit τ_OR < τ_dec UND
τ_OR physiologisch ([1e-5, 1e-1] s) innerhalb großzügiger
HYPOTHESE-Bereiche; FALSIFIED_EVERYWHERE sonst; plus: Bericht, ob
OHNE Shielding (S=1) irgendetwas viable ist.

## Result

**Signal: OPEN_SUBSTRATE** — mit ehrlicher Eingrenzung.

| Fall | E_G | τ_OR |
|---|---|---|
| iter-7-Artefakt ("Dimer") | 187 J (invalid) | 5.66e-37 s |
| Korrekt: Dimer-Masse, 8 nm | 2.79e-46 J | **3.77e11 s** (~12,000 Jahre) |
| Hagan: Proton-Displ., N=1e9, korreliert | — | 1.41e3 s |
| Konformation f=1 %, a=2.5nm, N=1e9, korreliert | — | ~1.2e-3 s (Hagan-Ballpark ✓) |

Phasen-Diagramm (3 f × 3 a × 4 N × 2 Korrelation × 4 S = 288 Konfigs):

- **7 viable Konfigs** mit physiologischem τ_OR — ALLE in der
  großzügigen Ecke: f=5e-2, a=8nm, N=1e9, korreliert, **S=1e6**
  (τ_OR/τ_dec = 0.61).
- **0 viable ohne Shielding (S=1)** — Tegmarks bulk-Wasser-Befund
  bleibt vollständig konsistent.
- Die ms-Region reproduziert Hagan's Ballpark nur mit
  Konformationsmasse (f≈1 %), nicht mit Einzel-Proton-Displacement
  (τ=1.4e3 s) — Hagans Rechnung verteilt die Massen-Differenz über
  das ganze Protein.

## Interpretation

- **iter-7's 27-Dekaden-CONTRADICTION ist zurückgezogen** (Formel-
  Artefakt + invertiertes Kriterium). LIMITATIONS.md aktualisiert:
  Status F → **C (OPEN)**.
- Die korrekte Rechnung lässt Orch-OR's Substrat in einer NARREN,
  generösen Parameter-Region zu: kollektive Konformations-Superposition
  (5 % Massen-Umverteilung, 8 nm Verschiebung) + starkes Shielding
  (S ≈ 1e6, ordered water/Debye/Gel). Das ist eine **Parameter-Region,
  keine Evidenz**.
- **Tegmark bleibt zielführend FÜR bulk water**: ohne Shielding ist
  keine Konfiguration viable. Der Unterschied zur alten Lesart:
  Tegmark's Rechnung ist eine Grenzbedingung (S=1-Grenze), kein
  universelles Verdikt — auf den photonischen Kanal (iter-15)
  sowieso nicht anwendbar.
- Via-Negativa: eigene früheren Resultate unterliegen denselben Tests
  wie Fremdtheorien. Der Status "bewusstseinserzeugend" bleibt
  unbelegt — geändert hat sich nur die numerische Haltbarkeit des
  Substrats.

## Verweise

- scratch/experiments/iter-16/{hagan_eg.py,result.json}
- iter-7 (zu korrigierend), theory/orchor_tegmark_rekonstruktion.md
- Penrose 1994 (Shadows of the Mind); Hagan et al. 2002 (Phys. Rev. E 65, 061901);
  Tegmark 2000 (Phys. Rev. E 61, 4194)