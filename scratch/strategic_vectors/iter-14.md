# Strategic Vectors — iter-14 (Falsifikator auf Produktionstack)

## Ergebnis: VECTOR_WINDOW_REPLICATION ✅ geschlossen (REPLICATED_STRONG
## im vorab registrierten Kriterium, mit methodischer Korrektur)

### Was replizierte

Das bimodale Damköhler-Phänomen überlebt **Gitterwechsel (16³→24³),
Seed-Wechsel (disjunkt 42-44→100-102), Numerikwechsel
(rint-Laplace → stochastische Sprünge) und Code-Trägerwechsel
(Scratch → Produktion)**:

- U-Form der Cross-Species-Dekorrelation in allen 3 D-Regimen
  (Minimum bei mittleren Raten, Rückkehr an beiden Enden)
- Sättigungs-Rückkehr ✓, Fenster-Ordnung 3/3 ✓, 0 Runaway

### Was NICHT replizierte (methodischer Fund)

Die iter-11-**Magnitude** corr 1.0 → 0.025 war **operator-kalibriert,
nicht physikalisch**: die rint-Laplace-Kontrolle ist deterministisch
auf beiden Spezies geteilt → identische Felder bleiben ewig
identisch (corr ≡ 1.000, tMI 0.681). Echte stochastische Migration
dekoreliert zwei identische Spezies sofort (molekularer Lärm) —
iter-14-Kontrolle: corr 0.02–0.10, tMI ≈ 0–0.02. ~90 % des iter-11-
Drops war geteilter Determinismus, nicht Chemie.

**Regel ab iter-14**: Chemie-Sichtbarkeit wird relativ zu einer
**stochastischen Migrations-Kontrolle** definiert; Signatur ist die
U-Form-Tiefe relativ zum Kontroll-Rausch-Floor, nicht der absolute
Corr-Abfall. Alle iter-11-corr-Zahlen sind als
operator-abhängig markiert (iter-11/experiment.md bleibt gültig, mit
diesem Vorbehalt).

## Vektoren

### VECTOR_STOCH_CONTROL_METRIC (offen)
Effektgrößen-Metrik relativ zum Kontroll-Rausch-Floor +
Permutationstest direkt auf die U-Form. Adressiert den letzten
Steelman („U-Form ist Metrik-Noise auf nahe-uniformen Feldern").

### VECTOR_SATURATION_MARGIN (offen)
Registry-k-Sweep Richtung Sättigung, jetzt auf Produktionstack.

### VECTOR_ENDOGEN_UVC_TIMESCALE (offen)
1 Event/Molekül/~6.6 Jahre — präbiotisch vs. in-vivo.

## Evidenz-Buchhaltung (CellsimMixMind)

| Befund | Vor iter-14 | Nach iter-14 |
|---|---|---|
| Damköhler-Fenster (Phänomen) | CANDIDATE | **CANDIDATE robust** (B) — Struktur überlebt Gitter/Seed/Numerik/Kode-Wechsel |
| Corr-Magnitude des Fensters | als Chemie gelesen | **operator-kalibriert** — Neuinterpretation nötig |
| Kalibrierung Sprung-Diffusion | p=𝒟/6 (untermischt) | ✅ p=𝒟 (Varianzwachstum 6𝒟/Schritt) |

## Verweise

- scratch/experiments/iter-14/{window_replication.py,result.json,experiment.md}
- iter-11 (Fenster-Erstsichtung), iter-13 (Produktionstack)
- Kalibrier-Korrektur in `modules/emergence.py` (p_dir = 𝒟)