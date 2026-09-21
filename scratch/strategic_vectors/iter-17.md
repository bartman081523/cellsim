# iter-17 — VECTOR_PATTERN_FORMATION

**Datum**: 2026-09-21 · **Layer**: L3 (RDME/Gillespie) · **Grade**: B

## Kernresultat

Turing-Muster im RDME-Substrat: Die vorab registrierte Banden-Vorhersage
wurde FALSIFIZIERT (Muster entstand bei Box-Skala k=0.262 statt
k*=1.42), aber die Falsifikation ist auf einen Einheiten-Bug im
**Analyse-Layer** zurückführbar (D pro Schritt vs. pro Zeiteinheit,
Faktor 20; korrekt D_eff = D/DT). Korrigierte Disperson post-hoc
konsistent: die 3 gemessenen Moden (0.262/0.370/0.453) sind exakt die
n=1-Schale = die einzige Mode-Familie in der korrigierten Bande
[0.186, 0.456]; Wachstumsrate 0.0064/Schritt vs. 2σ·dt = 0.0081
vorhergesagt (within 20 %); Onset 1.556 (dt-invariant, analytisch
geprüft) ✓.

- D_v=0.25/1.0: STABLE_AS_PREDICTED ✓ (robust gegen den Bug)
- D_v=3/10: Muster JA, aber vorab-Verdict FALSIFIED_NO_PATTERN steht
  (vorab registrierte Bande falsch; Korrektur dokumentiert)
- Neuentdeckung: emergente kollektive Turing-artige Struktur aus
  reinem demographischem Rauschen, Aktivator patterned / Inhibitor
  flach (std-Ratio 0.29), nichtlineare Sättigung

## Via-Negativa (ehrliche Abgrenzung)

- KEINE Bestätigung der korrigierten Theorie — post-hoc ist keine
  Bestätigung; prospektiver Re-Test erforderlich (iter-17b).
- Metrik-Defekt offengelegt: peak_excess ≥ 5 im matched-Null selbst
  erfüllt (5.64) → Kriterium war nicht diskriminativ; Null-Flag
  ARTIFACT_PATTERN dokumentiert statt verschwiegen.
- Substrat ist ein künstlicher Schnakenberg-Kern, KEIN Registry-
  Ausschnitt (Netto-Stöchiometrie verdeckt Autokatalyse —
  VECTOR_REGISTRY_TURING_EXT weiter offen).
- σ_meas-Extraktion im sättigten Regime invalid (nan) — Methoden-Fehler
  dokumentiert.

## Nächste Vektoren

1. **iter-17b** (prospektiv): korrigierte Disperson als neue
   Vorab-Registrierung, L=48-Stack (löst λ*≈21.5 erst wirklich auf),
   band-selektive Permutations-Metrik, Wachstumsphasen-Fit.
2. **VECTOR_REGISTRY_TURING_EXT**: Registry-Reaktionen auf
   autokatalytische Zyklen prüfen (Netto-Stöchiometrie → explicate).
3. **VECTOR_OR_KERNEL**: iter-18 abgeschlossen (SIGNATURE_ROBUST),
   Rest: C2-Claim-Deckel im Modul-Docstring verankert (erledigt).

## Status

iter-17 abgeschlossen: Falsifikation dokumentiert + Ursache (Analyse-
Bug) isoliert + korrigierte, jetzt registrierte Vorhersage. iter-18
abgeschlossen: OR-Kollaps-Kern in Produktion (modules/orch_or.py),
Diskrimination SIGNATURE_ROBUST 3/3 Seeds, korrigierte S2/S3-Formeln
im CORREKTUR-LOG.