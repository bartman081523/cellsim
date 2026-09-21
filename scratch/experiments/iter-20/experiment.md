# iter-20 — VECTOR_REGISTRY_TURING_EXT

**Datum**: 2026-09-21 · **Layer**: L3-Registry (produktion) · **Grade**: B
**Skript**: `registry_turing_ext.py` · **Daten**: `result.json`
**Vorab-Registrierung**: im Modul-Docstring, fixiert vor dem finalen Lauf

## Frage

Kann die ECHTE Produktions-Registry (`modules/reactions.py:default_registry`,
26 Spezies, 20 Reaktionen, NETTO-Stöchiometrie) Turing-Muster tragen — oder
ist Musterbildung in dieser Zellsim auf den künstlichen Schnakenberg-Kern
(iter-17/19) beschränkt? Das entscheidet die offene Behauptung aus iter-17
(`registry_audit`): "Net-Stöchiometrie verdeckt Autokatalyse;
Turing-Substrat nicht entscheidbar."

## Vorab registrierte Erwartung

FALSIFIED_REGISTRY_TURING_INCOMPETENT (Via-Negativa: strukturell kann
Netto-Form Autokatalyse nicht ausdrücken; dynamisch sollte der Test das
bestätigen — negative Kenntnis, nicht Bestätigungssuche).

## Ergebnisse

**Teil A — Autokatalyse-Zensus (Nettoform): 0/20.**
Per Konstruktion unerzwingbar: `species_change` hat EINEN Koeffizienten pro
Spezies, S[i,r] kann nicht zugleich < 0 (Reactant) und > 0 (Product) sein.
Das ist ein REPRÄSENTATIONS-Befund, kein chemischer.

**Teil B — Zwei-Reaktions-Zyklen: 48 Konversions-Zyklen, 0 Verstärkungs-Zyklen.**
Alle 48 laufen über den ATP⇌ADP-Loop (glycolysis erzeugt ATP → 9+ ATP-Verbraucher
→ ADP/Pi → zurück). Netto-Gewinn pro Umlauf: 0 (Erhaltungs-Loops). Kein
Aktivator-Inhibitor-Verstärkungs-Motiv.

**Teil D — Katalysator-Platzhalter: 14/20 Reaktionen** mit "X": 0-Einträgen —
in Mass-Action-Rate (v_r = k·∏_{S<0} x^{|S|}) wirkungslos, träge Dekoration.

**Teil C — Jacobian-Turing-Test (volle 26×26-Matrix):**
Referenzen: R1 = ODE-Attraktor (TOTZUSTAND, resid 8.6e-9: ATP=0, Pi=0,
Glucose=0, ADP=100, Pyruvat/NADH=150, Ribosomen 70S≈99, Rest eingefroren);
R2 = homogener Init x=50 (TRANSIENT). D-Szenarien: S1 uniform (1.0),
S2 Metabolit-schnell (3.0/0.06), S3 Metabolit-langsam (0.06/3.0).
Scan d ∈ (0, 12] (Summe der Achsen-Symbole), Kriterium max Re eig > 1e-6.

| Referenz | Szenario | max Re eig | d* | homogenes max Re eig |
|---|---|---|---|---|
| R1_dead | S1 | −2.000e-03 | 1e-4 | +1.7e-17 |
| R1_dead | S2 | −1.200e-04 | 1e-4 | +1.7e-17 |
| R1_dead | S3 | −1.200e-04 | 1e-4 | +1.7e-17 |
| R2_unif50 | S1 | −2.000e-03 | 1e-4 | +3.7e-07 |
| R2_unif50 | S2 | −1.200e-04 | 1e-4 | +3.7e-07 |
| R2_unif50 | S3 | −1.200e-04 | 1e-4 | +3.7e-07 |

Die Maxima liegen exakt bei der Gitter-Unterkante d=1e-4 und sind genau
−(d/DT)·D_min: das homogene J ist in beiden Referenzen marginal (≈ 0), und
JEDE Diffusion macht alle Moden dämpfender. Das Maximum der Instabilität
liegt bei d→0 — das ist die SIGNATUR eines Systems, das KEINE
diffusionsgetriebene Instabilität hat (ein echtes Turing-System hätte das
Maximum bei d* > 0).

## Verdict

**FALSIFIED_REGISTRY_TURING_INCOMPETENT** (vorab registrierte Erwartung).

Negative Kenntnis, dreifach abgesichert:
1. strukturell: Autokatalyse im Netto-Schema unerzwingbar (0/20),
   keine Verstärkungs-Zyklen (0 mit Gewinn),
2. dynamisch: keine diffusionsgetriebene Instabilität in 6/6
   (Referenz × D-Szenario)-Kombinationen,
3. Attraktor-Problem: die Registry-ODE zieht in den Totzustand (ATP=0),
   dort ist J praktisch nil — es gibt nicht mal ein lebendiges
   Arbeitspunkt-Fixpunkt, an dem man Turing testen könnte.

## CORREKTUR-LOG

- `rhs()`-Signatur zweimal korrigiert (solve_ivp verlangt (t, x)); Rest-
  Aufruf analog `rhs(0.0, x_dead)`.
- Docstring-Zählung 21 → 20 Reaktionen (Registry-real; CLAUDE.md nennt
  noch 21 — dort stale).
- Variablen-Schatten: `out` (Path) wurde vom Ergebnis-dict überschrieben →
  TypeError beim result.json-Schreiben NACH Abschluss aller Berechnungen.
  Fix: dict in `result` umbenannt, Lauf deterministisch wiederholt
  (kein RNG im Skript, Totzustand resid 8.6e-9 identisch) — Ergebnisse
  unverändert, nur die Persistenz war betroffen.
- Folgekorrektur (Dokumentation): CLAUDE.md und Selbst-Audit-Claim
  VECTOR_BRENDA_FULL trugen Altstände ("21 Komplexe", "BRENDA-extrahiert",
  "22 Spezies + 21 Reaktionen"). Gemessener Stand (iter-20-Zensus): 26
  Spezies, 20 Reaktionen, 16× MGENITALIUM + 4× HYPOTHESE. Claims/Doku auf
  den Code-Stand korrigiert, Selbst-Audit neu gelaufen (12 Claims:
  4× A, 8× C, 0× F).

## Konsequenzen

- Musterbildung in dieser Zellsim ist REAL auf den künstlichen Kern
  (iter-17/19) beschränkt — die Produktions-Registry trägt kein
  Turing-Substrat, weder strukturell noch dynamisch.
- Damit konsistent: der Fröhlich-Stub und der künstliche Kern sind die
  einzigen Musterkanäle; alle "emergence"-Claims über die Registry sind
  jetzt explizit widerlegt statt nur unbelegt.
- Falls Musterbildung auf der Registry erwünscht wäre: Schema-Änderung
  nötig (z. B. Nicht-Netto-Form mit doppelter Rolle eines Metaboliten,
  oder explizite Dimerisierungs-Reaktionen) — DAS wäre ein Design-Eingriff,
  kein Messbefund, und wird bewusst NICHT als offener Vektor gebucht,
  solange keine biologische Motivation dafür steht.

## Via-Negativa-Status

- Vorab-Registrierung im Docstring fixiert, Erwartung war die Falsifikation
  selbst — kein Bestätigungs-Bias-Risiko.
- R2 ist als TRANSIENT gekennzeichnet (kein Fixpunkt) — der Test wurde auf
  beiden Referenzen konsistent negativ, der Einwand "falscher Referenzpunkt"
  greift damit nicht.
- Grade B: Methodik sauber, aber der Befund ist eine Falsifikation des
  eigenen Architekturtexts (Muster-Erwartung), nicht eines externen Claims.