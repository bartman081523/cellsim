# iter-35 — VECTOR_YOD_IODINE: Yod=10-Theorie, Jod-Dossier, cellsim-Zensus

**Status:** REGISTRIERT (2026-10-06, VOR der Messung — Ledger-Mind P2). Ergebnis-Append erst nach Lauf, unten.
**Linie:** Bewusstseins-TCI (symbolisch-biochemischer Seitenzweig) + Periodensystem-Dossier. Deterministisch, kein RNG, keine Seeds, CPU < 1 s.

## Hypothesen

- **H-A (Wortspur):** Deutsch „Jod" (Element) und „Jod" (hebräischer Buchstabe י, 10. Buchstabe, gematria 10) sind im Deutschen ein echtes Homonym. Vorab-Haltung: die Etymologie trennt sich — *iode* ← griech. ἴον + εἶδος „violettfarben" (Gay-Lussac 1813, nach der violetten Dampffarbe von I₂), *Yod* ← phönizisch *yodh* „Hand" (→ griech. iota). Erwartung: `HOMONYM_VERIFIED` UND `ETYMOLOGY_LINK_FALSIFIED` — die geteilten Namen teilen NICHT den selben Wurzelstamm (Blume vs. Hand).
- **H-B (Arithmetik — gegen Texas-Sharpshooter):** Behauptung „Bewusstsein/göttlicher Funke spiegelt sich als Yod = 10 (Basis 10)". Verarbeitung: vorab-registrierter Familien-Zensus — `FAM_HALOGEN_ISO` (6 stabile Halogen-Isotope: 19, 35, 37, 79, 81, 127), `FAM_MONOISOTOPIC_26` (IUPAC: Be, F, Na, Al, P, Sc, V, Mn, Co, As, Rb, Y, Nb, Rh, In, Cs, I, La, Pr, Eu, Tb, Ho, Tm, Lu, Re, Au), `FAM_ESSENTIAL_26` (kanonische essenzielle Elemente CHNOPS + Na K Mg Ca + Cl Fe Zn Cu Mn I Se Co Mo F Cr Sn V B Si Ni). Metriken: `M10` = Quersumme(base 10) des meistabundanten stabilen Nuclids = 10; `Z10` = Quersumme der Ordnungszahl = 10. Nullverteilung exakt: Anteil der Ganzzahlen im Familien-Intervall mit Quersumme 10; exakter Binomialtest zweiseitig.
- **Radix-Filter (vorab registriert):** Kandidaten-„10s" von Jod, die nur über den Dezimal-String existieren (Quersummen), scheitern am Basiswechsel und zählen NICHT als Träger. Radix-invariante Überlebenskandidaten a priori, als reine Konstanten-Checks: (C1) 4d-Unterschale von Jod = 10 Elektronen ([Kr] 4d¹⁰ 5s² 5p⁵); (C2) Deiodinations-Kaskade T4→T3→T2→T1→Thyronin = 4+3+2+1+0 = 10 Jod-Atome über die volle Kaskade (ganzzahlig, basisunabhängig). Deklarierter Status: (C2) ist post-hoc relativ zur Theorieauswahl (Jod wurde wegen des Namens gewählt) — Resonanz-Buchung, keine Kausalbehauptung.
- **H-C (cellsim-Zensus):** Erwartung `IODINE_ABSENT_IN_SYN3A` — 0 Jod-Treffer in (a) UniProt-Proteom UP000326712 (REST, abgefragt 2026-10-06: 0), (b) Production-Registry (26 Spezies / 20 Reaktionen), (c) Grep über src + configs + tests, (d) AF-PDB-Modelle (nach Konstruktion ohne Heteroatome). Zusätzlich abgefragt und erwartet: `SELENOCYSTEINE_ABSENT_IN_SYN3A` (REST: 0) — Konsequenz-Vermutung vorab: die beiden schwersten essenziellen Elemente (I, Se) sind gemeinsamer Abbau-Posten des Minimalgenoms.
- **H-D (Jod-Atomzahlen-Dossier):** Z = 53; Ar = 126.90447(3) (monoisotop, CIAAW 1985); 74 n; Gruppe 17, Periode 5; [Kr] 4d¹⁰ 5s² 5p⁵; K-Kante 33.17 keV; E°(I⁻/HOI) ≈ 0.54 V vs. Br⁻/HOBr ≈ 0.76 V vs. Cl⁻/HOCl ≈ 1.28 V (nur Jod hat einen biologisch steuerbaren Redox-Zyklus: H₂O₂/TPO-Oxidation ⇄ Deiodinasen-Reduktion); C–I am labilsten aller C–X-Bindungen (F > Cl > Br > I); Jod = schwerstes essenzielles Element; Jodmangel = häufigste vermeidbare Ursache nicht-angeborener geistiger Behinderung (WHO 1994/1999); T4 = 65 %, T3 = 59 % Massenanteil Jod (im Skript aus Suma-Formeln gerechnet); Deiodinasen D1/D2/D3 sind Selenoenzyme — die beiden schwersten Essenziellen (I 53, Se 34) treffen sich mechanisch im Hirnstoffwechsel; Seewasser: I⁻ ≈ 0.45–0.5 µM vs. Br⁻ ≈ 0.8 mM (Br ≈ 10³× reichlicher — Biologie wählt das seltenere Halogen).

## Registrierte Verdict-Regeln

- Familie f: `TEN_STANDOUT` iff hits_m10 ≥ exp + 2·sqrt(n·f·(1−f)) UND 127 ∈ hits_m10; sonst `TEN_CHANCE_CONSISTENT`.
- Zensus: `IODINE_ABSENT_IN_SYN3A` iff alle 4 Quellen 0; sonst `IODINE_FOUND_<n>`.
- Radix-Demo: Zensus der Quersummen-10-Treffer in Basen {2, 8, 10, 12, 16} über FAM_MONOISOTOPIC_26 — Erwartung vorab: Treffermenge wandert mit der Basis (Beweis der Repräsentationsabhängigkeit).
- Ehrliche Grenze (vorab): die symbolische Ebene (Zohar I:30a — Yod als nekudah rishonah, kleinster Buchstabe, Beginn des Tetragrammatons; Bahir §56 — Hand Gottes; 10 Sephirot; „Hand" → 10 Finger → Basis 10 als semiotischer Mechanismus) wird als SYMBOLISCH dokumentiert und nicht als Kausalpfad verbucht. Keine zusätzliche Bewusstseins-Behauptung; die TCI-Vektor-Bilanz bleibt unverändert.

## ERGEBNIS (Append nach Lauf)

- (wird nach dem Lauf eingefügt)