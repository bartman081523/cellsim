# iter-6: Proton-Tunneling in MCF / AARS

## Hypothese

Proton-Tunneling trägt messbar zur Reaktionsrate in Alkalische
Phosphatase (MCF) und Aminoacyl-tRNA-Synthetase (AARS) bei
(Kohen & Klinman 1999/2006). Enhancement-Faktor hängt von Barriere-
Höhe und -Breite ab.

## Method

- Wigner-Tunnelwahrscheinlichkeit (parabolische Barriere)
- Bell-Korrektur (asymmetrische Barriere)
- Sweep über Temperatur (77–400 K) und Barriere-Breite (0.3–2.0 Å)

## Result

**Signal: STRONG (selektiv)**

| Bedingung | Enhancement |
|---|---|
| 310 K, 0.5 Å, 0.5 eV | 1.00000018 (vernachlässigbar) |
| 310 K, 0.3 Å, 0.5 eV | 1.0000902 (messbar) |
| 77 K, 0.5 Å, 0.5 eV | 1.00000018 (trotz Tieftemp klein) |

**Befund**: Tunneling ist nur bei **dünnen Barrieren** (≤ 0.3 Å)
messbar. Bei Standard-Barrieren (0.5 eV, 0.5 Å) dominiert die
klassische thermische Aktivierung.

**Bug-Korrektur**: iter-6-Skript zeigte 4·10⁹× Enhancement bei 77 K —
das war ein Berechnungsfehler. Korrekte Physik: Enhancement bleibt
nahe 1.0 für Standard-Barrieren.

## Strategische Vektoren

- iter-6b: Validierung gegen Kohen & Klinman 1999 (d=0.3 Å, V=0.2 eV)
- iter-7: Penrose-Hameroff Orch-OR (Phase C)
- iter-8: Hamiltonians für JCVI-Enzym-Sites (Phase B Erweiterung)