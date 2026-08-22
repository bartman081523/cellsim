# Strategic Vectors — iter-4 (CONTRADICTION)

## Signal: CONTRADICTION

**Drei Iter an derselben ODE-Hürde gescheitert**: UV-Sync im gewählten
Modell nicht entscheidbar. Die ODE ist der Bottleneck, nicht die Hypothese.

## Diagnose

Isolated-Kontrolle: r = 1.0 trivial. UV-Kopplung: ATP divergiert.
Beide scheitern an derselben ODE-Vereinfachung.

## Strategische Vektoren

### VECTOR_PHASE_A_RETIRE
→ UV-Sync-Hypothese ist *vorerst* aufgegeben. EM-Schicht (Chemolumineszenz)
bleibt im Code als **Daten-Lieferant**, aber die UV-Sync-These bekommt
Priorität *niedrig*. Stattdessen:

### VECTOR_PHASE_B_PRIORITY (HOCH)
→ **Direkter Sprung zu Phase B (QM-Elektronen)**.

Die nächsten realistischen Iters sind:
- **iter-5**: QuQuint-VQE-Beschleunigung der Hamiltonian-Diagonalisierung
  (siehe riemann/pt_ququint_vqe.py)
- **iter-6**: Protonen-Tunneling in MCF/AARS (experimentell validiert)
- **iter-7**: JCVI-spezifische Crypto-Proteine (BRENDA-Annotation)

### VECTOR_ODE_MODERNIZATION (MITTEL)
Wenn wir später UV-Sync nochmal versuchen wollen: ATP-ODE mit:
- Mehrere ATP-Verbraucher (Translation 70%, Motor 20%, etc.)
- Michaelis-Menten-Kinetik statt linear
- Homeostatische Regulation

→ Kein sofortiger Aufwand, spätere Iteration falls Phase B/C
  erfolgreich.

### VECTOR_RECONSULT_SOURCE (HOCH)
Konsultiere direkt:
- **Cifra & Sonn 2011**: ihre ODE war deutlich komplexer (11 Metabolite)
- **Popp 2003**: was wurde experimentell bestätigt/widerlegt?
- **Rattemeyer 1981**: Kritik an Popp

Diese Konsultation bestimmt, ob UV-Sync überhaupt noch sinnvoll ist
oder ganz fallen gelassen wird.

## Konsequenz für den Plan

| Phase | Status neu |
|---|---|
| **Phase A (EM + UV)** | EM-Schicht produktiv; UV-Sync-Pfad *pausiert* |
| **Phase B (QM-Elektronen)** | **Aktivierung empfohlen** |
| **Phase C (Mikrotubuli)** | Später |
| **Phase D (Integration)** | Später |

## Verweise

- Cifra, M. & Sonn, K.V. (2011)
- Rattemeyer, M. et al. (1981): Naturwissenschaften 68, 572
- Popp, F.A. (2003)
