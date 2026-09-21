# iter-20 — VECTOR_REGISTRY_TURING_EXT

**Status**: ABGESCHLOSSEN (2026-09-21) · **Verdict**: FALSIFIED_REGISTRY_TURING_INCOMPETENT
**Layer**: L3-Registry · **Grade**: B · **Ergebnisse**: `scratch/experiments/iter-20/`

## Was der Vektor wollte

Die offene Behauptung aus iter-17 ("Net-Stöchiometrie verdeckt Autokatalyse;
Turing-Substrat nicht entscheidbar") programmatisch auf der Produktions-
Registry entscheiden — strukturell (Autokatalyse-Zensus, Zyklen-Suche) UND
dynamisch (Jacobian-Turing-Test über 6 Referenz×D-Kombinationen).

## Ergebnis

Falsifikation wie vorab registriert:

- **0/20** Autokatalyse (im Netto-Schema per Konstruktion unerzwingbar),
- **48** Konversions-Zyklen (alle ATP⇌ADP-Loops, Gewinn 0), **0** Verstärkungs-Zyklen,
- **14/20** Reaktionen mit wirkungslosen "X": 0-Platzhaltern,
- Jacobian-Turing-Test: alle 6 Kombinationen negativ; max Re eig liegt bei
  d→0 und ist exakt −(d/DT)·D_min — homogenes J marginal, Diffusion dämpft
  nur. Keine Turing-Kompetenz.
- Zusatzbefund: Registry-ODE-Attraktor ist der **Totzustand** (ATP=0,
  Glucose=0, Ribosomen eingefroren) — ein lebendiger Arbeitspunkt existiert
  in der reinen ODE nicht.

## Konsequenz (offen bleibt)

Musterbildung in dieser Zellsim ist auf den künstlichen Schnakenberg-Kern
(iter-17/19) beschränkt. Die Architektur-Erwartung "die Registry trägt
Emergenz" ist jetzt explizit WIDERLEGT statt nur unbelegt. Ein
Schema-Wechsel (Nicht-Netto-Form) wäre Design-Eingriff ohne biologische
Motivation — bewusst nicht als Vektor gebucht.

## Offene Vektoren danach

- iter-19 (Turing prospektiv, L=48, exakte diskrete Abbildung vs
  kontinuierliches Symbol): läuft, Auswertung folgt.
- Selbst-Audit-Eintrag für REGISTRY_TURING_EXT (und iter-18 OR_KERNEL)
  steht noch aus.