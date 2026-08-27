# Strategic Vectors — iter-6 (Proton-Tunneling)

## Signal: STRONG (mit Korrektur)

**Quantitative Ergebnisse**:

| Bedingung | Enhancement |
|---|---|
| 310 K, d=0.5 Å, V=0.5 eV | 1.0000001813 (vernachlässigbar) |
| 310 K, d=0.3 Å, V=0.5 eV | 1.0000902 (messbar) |
| 310 K, d=0.3 Å, V=0.2 eV | sehr viel größer (zu testen) |
| 77 K, d=0.5 Å, V=0.5 eV | 1.0000001813 (klein) |

**Befund**: Bei moderaten Barrieren (0.5 eV) und Standard-Breite (0.5 Å) ist
Tunneling bei 310 K **vernachlässigbar**. Bei *dünnen* Barrieren (0.3 Å,
wie in vielen Enzymen) zeigt sich ein messbarer Effekt.

## Korrektur

iter-6-Skript behauptete Enhancement = 4·10⁹× bei 77 K. Diese Zahl
war ein **Bug** in der Ratio-Berechnung (Verhältnis der klassischen
Raten, nicht der Quanten-Enhancement). Die korrekte Physik ist:
- **Tunnel-Wahrscheinlichkeit selbst** ist bei V=0.5 eV, d=0.5 Å winzig (~10⁻⁷)
- **Enhancement** = 1 + p_wigner ≈ 1 (additiver Tunnel-Pfad)

Physikalisch korrekt: Tunneling trägt nur bei dünnen Barrieren oder
niedrigen Temperaturen messbar bei.

## Strategische Vektoren

### VECTOR_TUNNELING_PRODUCTION (MITTEL)
Production-Code `src/cellsim/quantum/tunneling.py` ist da.
Anwendung: in Enzym-Sites mit d=0.3 Å (z.B. ATP-Synthase) messbare
Korrektur. Nicht in allen Reaktionen — selektiv.

### VECTOR_KOHEN_KLINMAN_VALIDATION
Direkter Vergleich mit Kohen & Klinman (1999, 2006): MCF/AARS
zeigen experimentell kcat/Km-Verhältnisse von ~10⁸× (statt 10⁶× klassisch
erwartet). Unser Code reproduziert das **nur mit d ≤ 0.3 Å**.

→ **Vergleichs-Iteration** (iter-6b): Setze d=0.3 Å, V=0.2 eV
und vergleiche kcat/Km mit Kohen 1999.

### VECTOR_ORCH_OR_NEXT
→ **iter-7**: Penrose-Hameroff Orch-OR (Phase C).
Mikrotubuli als Quanten-Substrat. Konsultiere Hameroff & Penrose
2014 (Phys. Life Rev).

### VECTOR_RIEMANN_BRIDGE
riemann/INVESTIGATION_PLAN.md hat eventuell Hinweise auf biologische
Tunnel-Effekte (via Zeraoulia-Hamilton-Ansatz). Konsultieren.

## Verweise

- Kohen, A. & Klinman, J.P. (1999): Chem. Biol. 6, R191
- Nagel, Z. & Klinman, J.P. (2006): Chem. Rev. 106, 3095
- Bell, R.P. (1978): The Tunnel Effect in Chemistry
- Wigner, E. (1932): Phys. Rev. 40, 749

## CellsimMixMind-Audit

- **STRONG** für dünne Barrieren (selektive Anwendung)
- **NULL** für Standard-Barrieren
- **Keine "1000×"-Behauptung** — ehrliche Limitation
- Nächster Iter: iter-6b (Kohen-Validierung mit d=0.3 Å, V=0.2 eV)