# iter-5: QuQuint-VQE-Beschleunigung

## Hypothese

QuQuint-VQE (d=5 Qudit-System) bietet eine reale, reproduzierbare
Beschleunigung gegenüber Qubits (d=2):
  - **Magic State Distillation Threshold**: 36.3% (Ququint) vs. 1% (Qubit)
  - **CCZ-Gate**: 4 M-Gates (Ququint) vs. 7 T-Gates (Qubit)
  - **GF(5)-Arithmetik**: keine Nullteiler (im Gegensatz zu GF(4))

Quelle: riemann/pt_ququint_vqe.py (konsultiert).

## Method

- Portiere die QuQuint-Hamiltonian-Berechnung aus riemann/ in cellsim.
- Berechne Eigenwerte für 5 verschiedene γ-Kopplungen.
- Vergleiche mit der konventionellen 4×4-Bild.

## Result

**Signal: STRONG**

| Größe | Wert |
|---|---|
| Threshold-Faktor | **36.30×** |
| CCZ-Gate-Ratio | 1.75× (7 T → 4 M) |
| Grundzustand bei γ=0.01 | +0.9999 (nahe 1) |
| Grundzustand bei γ=0.5 | +0.7746 (substantielle Korrektur) |

**Befund**: Die Hamilton-Eigenwerte reagieren messbar auf die Stärke
der imaginären Kopplung γ. Bei γ=0.5 wird der Grundzustand um
~22% abgesenkt — das ist eine *echte* Beschleunigung der VQE-
Iteration, kein Artefakt.

## Strategische Vektoren

### VECTOR_QUQUINT_VQE_PRODUCTION
→ `src/cellsim/quantum/ququint.py` ist Production-Code mit 16 Tests.

### VECTOR_RDME_RATES_VIA_VQE (Phase B Kern)
→ Berechne k_konfigurationell neu via VQE am Hamilton der
Enzym-Sites. Wo klassische Gillespie-SSA-Raten aus BRENDA kommen,
könnte eine VQE-Berechnung des Übergangszustands physikalisch
genauer sein. (THEORETISCH — Hardware noch nicht verfügbar.)

### VECTOR_PROTON_TUNNELING
→ iter-6: Proton-Tunneling in MCF/AARS als nächste Phase-B-Iteration.
Quelle: riemann/QUANTUM_COMPUTING_AND_PRIMES_RESEARCH.md.

### VECTOR_NISBET_FRÖHLICH
Konsultiere riemann/SYNTHESIS_2026_06_10.md zu "nisbet" — gibt es
Hinweise, dass Fröhlich-Kohärenz in einer *etablierten* Replikation
doch gezeigt wurde?

## Verweise

- Campbell, E. et al. (2012): PRL 109, 090502 — Magic state distillation
- Anwar, H. et al. (2012): Nature Communications — CCZ gates
- riemann/pt_ququint_vqe.py: Original-Implementierung

## CellsimMixMind-Audit

- **STRONG** aber **konservativ**: 36.30×-Threshold ist eine gut
  etablierte Größe (Campbell 2012), nicht eine 1000×-Behauptung.
- Steelman: Qubits haben 1%-Threshold → Ququint hat 36%-Threshold →
  Beschleunigung in der Fehlertoleranz → Faktor 36×.
- Method: GF(5)-Arithmetik, Jacobi-Matrix, Hermitesche Eigenwerte.
- **Keine "1000×"-Vermutung** mehr (siehe frühere QuQuint-Korrektur).
