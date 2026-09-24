"""iter-26 Nachtrag: Mittel-Ebenen-Reklassifikation vs gebuchte Regel.

Frage: Ist die gebuchte DISTINCT/NULL-Klassifikation aus den
persistierten Konfig-Mitteln nachrechenbar? Die registrierte Regel
(iter-14/24/25 VERBATIM, config_classification) klassifiziert PER-SEED
gegen die seed-gepaarte Kontrolle und wählt per Mehrheit (≥2/3); die
Artefakte enthalten nur Konfig-Mittel. Hier wird dieselbe Schwellen-
regel (ALLE drei Kriterien: lz_diff > 0.05, corr_drop > 0.3,
tmi_diff > 0.05) auf die Mittel-Ebene angewandt und gegen die gebuchte
Klassifikation verglichen.

Status: Interpretations-Beobachtung, KEIN neuer Befund, KEINE Änderung
der gebuchten Klassifikation. Die gebuchten Labels folgen der
registrierten per-Seed-Regel (in-run, deterministisch, K5 9/9); diese
Analyse quantifiziert nur, dass die Klassifikation KEINE Mittel-Ebenen-
Eigenschaft ist — die harte Zahl hinter der Harness-Lektion
„per-seed-Werte persistieren" (CORREKTUR-LOG #1).

Kontroll-Basis: controls_recovery.json (deterministischer Recovery-Lauf,
Cross-Check D=0.05/0.15 vs iter-25 bit-identisch). D=0.45 hat keine
gerettete Kontrolle (iter-25, rechtszensiert übernommen) → ausgeschlossen.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def mean_level_class(run_mean: dict, ctrl_mean: dict) -> str:
    """Registrierte Kriterien (classify, iter-14/24/25) auf Mittel-Ebene."""
    if run_mean["mass_ratio"] > 3.0:
        return "RUNAWAY"
    lz_diff = abs(run_mean["lz_growth"] - ctrl_mean["lz_growth"])
    corr_drop = abs(run_mean["corr_glc_atp_mean"]
                    - ctrl_mean["corr_glc_atp_mean"])
    tmi_diff = abs(run_mean["temporal_mi_mean"]
                   - ctrl_mean["temporal_mi_mean"])
    if corr_drop > 0.3 or lz_diff > 0.05 or tmi_diff > 0.05:
        return "DISTINCT"
    return "NULL"


def main() -> None:
    result = json.loads((HERE / "result.json").read_text(encoding="utf-8"))
    ctrl = {r["diff_coeff"]: r["mean"] for r in json.loads(
        (HERE / "controls_recovery.json").read_text(encoding="utf-8"))}

    n = 0
    disagree: list[dict] = []
    for row in result["rows"]:
        d = row["diff_coeff"]
        if d not in ctrl:  # D=0.45 (iter-25, keine gerettete Kontrolle)
            continue
        n += 1
        booked = row["classification"]
        recomputed = mean_level_class(row["mean"], ctrl[d])
        if recomputed != booked:
            disagree.append({
                "diff_coeff": d, "k_factor": row["k_factor"],
                "booked": booked, "mean_level": recomputed,
                "lz_diff": round(abs(row["mean"]["lz_growth"]
                                     - ctrl[d]["lz_growth"]), 4),
                "corr_drop": round(abs(row["mean"]["corr_glc_atp_mean"]
                                       - ctrl[d]["corr_glc_atp_mean"]), 4),
                "tmi_diff": round(abs(row["mean"]["temporal_mi_mean"]
                                      - ctrl[d]["temporal_mi_mean"]), 4),
            })

    print(f"{n} Zellen geprüft (ohne D=0.45), "
          f"{len(disagree)} Widersprüche Mittel-Ebene vs per-Seed-Regel\n")
    for x in disagree:
        print(f"  D={x['diff_coeff']:g} k={x['k_factor']:g}: "
              f"gebucht {x['booked']:8s} | Mittel-Ebene {x['mean_level']:8s} "
              f"| lz_diff {x['lz_diff']:.3f} corr_drop {x['corr_drop']:.3f} "
              f"tmi_diff {x['tmi_diff']:.3f}")
    (HERE / "mean_vs_perseed.json").write_text(
        json.dumps({"n_cells": n, "n_disagree": len(disagree),
                    "disagree": disagree}, indent=2),
        encoding="utf-8")
    print("\n→ mean_vs_perseed.json")


if __name__ == "__main__":
    main()
