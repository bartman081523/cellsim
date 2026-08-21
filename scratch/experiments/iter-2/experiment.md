# iter-2: UV-Phasen-Synchronisation zwischen 2 Zellen

## Hypothese

Zwei benachbarte Zellen (Abstand < 10 µm) können über UV-Biophotonen-
Emission ihre ATP-Synthese-Raten phasen-synchronisieren
(Cifra & Sonn, 2011; Popp, 1988).

**Vorhersage**: ATP-Synthese-Oszillationen in Zelle A und Zelle B sind
mit Korrelationskoeffizient r > 0.5 korreliert, wenn der Abstand
< 10 µm ist.

## Method

1. **2-Zellen-Modell**: beide Zellen haben ODE für ATP-Haushalt.
2. **EM-Kopplung**: UV-Photonen-Fluss von A → B und B → A.
3. **Feedback**: UV-Absorption moduliert ATP-Synthase-Rate in Empfänger.
4. **Output**: Zeitreihen von ATP in A und B + Korrelationskoeffizient.

## Result

*Wird automatisch durch iter_loop.py ausgewertet. Vorläufige Hypothese:
Ohne Kopplung oszillieren beide Zellen unabhängig (r ≈ 0). Mit
Kopplung bei < 5 µm erwarten wir r > 0.3.*

## Strategic Vectors

- r > 0.3 (WEAK): → iter-2-retry mit höherer ATP-Kopplungsstärke
- r > 0.7 (STRONG): → iter-3 (Popp's "biocoherent state")
- r ≈ 0 (NULL): → iter-2-retire (UV-Synchronisation experimentell widerlegt)
