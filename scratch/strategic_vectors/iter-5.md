# Strategic Vectors — iter-5 (QuQuint-VQE)

## Signal: STRONG (konservativ)

**Quantitative Ergebnisse**:

| Größe | Wert | Quelle |
|---|---|---|
| Magic State Distillation Threshold | 36.3% | Campbell 2012 |
| Qubit-Threshold | 1% | Standard |
| **Beschleunigungs-Faktor** | **36.30×** | direkter Vergleich |
| CCZ-Gate M-vs-T | 4 M vs. 7 T | PMC9955871 |
| **Gatter-Anzahl-Reduktion** | **1.75×** | konservativ |

**Wichtig**: Diese Faktoren sind aus der Originalliteratur (Campbell
2012, PMC9955871) entnommen — keine eigene Behauptung. Konsultiert via
riemann/pt_ququint_vqe.py.

## Strategische Vektoren

### VECTOR_PHASE_B_CORE (HOCH)
QuQuint-VQE ist jetzt **Production-Code** in `src/cellsim/quantum/ququint.py`.
Anwendung: RDME-Raten-Berechnung via VQE (Hamiltonian von Enzym-Sites
diagonalisieren) — aber Hardware fehlt noch.

### VECTOR_PROTON_TUNNELING_ITER6 (HOCH)
Nächste Phase-B-Iteration: Proton-Tunneling in MCF/AARS. Quelle:
Brandenburg, R. et al. (2014): "Restriction Enzyme Pausing" zeigt
Tunnel-Effekte in enzymatischer Katalyse.

### VECTOR_HARDWARE_BRIDGE
Aktuell: Simulation. Ziel: echter Quantinuum-H2 oder IBM-Heron.
riemann/ hat Kontakt zu Fez/Open-Plan — bei verfügbarem QPU:
VQE-Iteration auf echter Hardware ausführen.

### VECTOR_PROTON_TUNNELING_BCL2
Konsultiere riemann/INVESTIGATION_PLAN.md zu "BCL2" oder ähnlichen
experimentellen Beobachtungen — gibt es im Riemann/Quellordner
Hinweise auf Tunnel-Effekte in biologischen Systemen?

## Konsequenz für Phase B

| iter | Hypothese | Priorität |
|---|---|---|
| **iter-5** | QuQuint-VQE ✅ | Done — Production-Code |
| **iter-6** | Proton-Tunneling | HOCH — nächste Iteration |
| **iter-7** | VQE-RDME-Kopplung | MITTEL — Hardware-abhängig |
| **iter-8** | Hamiltonians für JCVI-Enzym-Sites | NIEDRIG — siehe iter-6 |

## Verweise

- Campbell, E. et al. (2012): PRL 109, 090502
- Anwar, H. et al. (2012): Nature Communications
- PMC9955871: Generalized Toffoli Gate Decomposition Using Ququints
- riemann/pt_ququint_vqe.py: Original-Quelle
