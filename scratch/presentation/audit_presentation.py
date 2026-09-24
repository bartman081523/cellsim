"""SciComPresentationMind · Schritt 5 — Fidelity-Audit (Gate).

Data-Gate (VOR/NACH Produktion): claims.json == recomputed claims aus
den Quelldaten (extract_claims.claims()) — sonst Publish-Stop.
Medium-Gate (NACH Produktion): Slide-Zahl, Claim-Abdeckung (kein
stiller Kanal), Caption-Strings wörtlich auf den Slides, Videos +
Stills vorhanden und nicht leer, Video-Dauern > 0, Diskrepanz-Note
(≥6/9 vs 12 Treatment-Zellen) dokumentiert.

Abweichung = Publish-Stop (Exit 1) + audit_report.md.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_claims  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE_TYPE  # noqa: E402

PPTX = HERE / "cellsim_findings.pptx"
MEDIA = HERE / "media"
VIDEOS = ("WindowScene", "SweepScene", "GatesScene")


def slide_text(prs: Presentation, idx: int) -> str:
    """Gesamter Text einer Slide (0-basiert), inkl. Tabellen."""
    out = []
    for shp in prs.slides[idx].shapes:
        if shp.has_text_frame:
            out.append(shp.text_frame.text)
        if getattr(shp, "has_table", False) and shp.has_table:
            for row in shp.table.rows:
                for cell in row.cells:
                    out.append(cell.text)
    return "\n".join(out)


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    # --- Data-Gate: claims.json ist der recomputete Stand -----------------
    disk = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
    live = extract_claims.claims()
    same = json.dumps(disk, sort_keys=True, default=str) == \
        json.dumps(live, sort_keys=True, default=str)
    checks.append(("Data-Gate: claims.json == recomputed", same,
                   f"{len(live)} Claims"))

    ids = {x["id"] for x in live}
    cl = {x["id"]: x for x in live}

    # --- Medium-Gate -------------------------------------------------------
    prs = Presentation(str(PPTX))
    checks.append(("Deck existiert, 12 Slides", len(prs.slides) == 12,
                   f"{len(prs.slides)} Slides"))

    manifest = json.loads((HERE / "deck_manifest.json")
                          .read_text(encoding="utf-8"))
    used_ids: set[str] = set()
    cap_ok = True
    cap_fail: list[str] = []
    for entry in manifest:
        for cid in entry["claim_ids"]:
            used_ids.add(cid)
        texts = slide_text(prs, entry["slide"] - 1)
        for cap in entry["captions"]:
            if cap not in texts:
                cap_ok = False
                cap_fail.append(f"Slide {entry['slide']}: {cap[:60]}…")
    checks.append(("Caption-Strings wörtlich auf Slides", cap_ok,
                   "alle Captions gefunden" if cap_ok
                   else f"FEHLEN: {cap_fail}"))
    checks.append(("Claim-IDs im Deck existieren", used_ids <= ids,
                   str(sorted(used_ids))))
    checks.append(("Keine stillen Kanäle (alle Claims referenziert)",
                   used_ids == ids, f"ungenutzt: {sorted(ids - used_ids)}"))

    # Videos + Stills
    for name in VIDEOS:
        mp4 = MEDIA / f"{name}.mp4"
        still = MEDIA / f"{name}_still.png"
        dur = 0.0
        if mp4.exists():
            try:
                dur = float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries",
                     "format=duration", "-of", "csv=p=0", str(mp4)],
                    capture_output=True, text=True).stdout.strip())
            except (ValueError, subprocess.CalledProcessError):
                dur = 0.0
        ok = (mp4.exists() and dur > 3.0 and still.exists()
              and still.stat().st_size > 50_000)
        checks.append((f"Video {name} (Dauer > 3 s, Still > 50 kB)", ok,
                       f"{dur:.1f} s, Still "
                       f"{still.stat().st_size // 1024 if still.exists() else 0} kB"))

    movies = [shp for sl in prs.slides for shp in sl.shapes
              if shp.shape_type == MSO_SHAPE_TYPE.MEDIA]
    checks.append(("3 Videos im Deck eingebettet", len(movies) == 3,
                   f"{len(movies)} Media-Shapes"))

    # Diskrepanz-Note (Buchhaltung) dokumentiert?
    note = cl["C01"]["value"].get("note", "") if "C01" in cl else ""
    checks.append(("≥6/9-Diskrepanz-Note vorhanden", "≥6/9" in note,
                   note[:70]))

    # --- Report ------------------------------------------------------------
    ok_all = all(ok for _, ok, _ in checks)
    lines = ["# Fidelity-Audit — cellsim_findings.pptx\n",
             "SciComPresentationMind: Caption-Werte gegen Quelldaten "
             "recomputet; fehlende Kanäle sind Defekte.\n"]
    for name, ok, detail in checks:
        lines.append(f"- {'PASS' if ok else 'FAIL'} — {name} "
                     f"({detail})")
    lines.append("\n## Verdict\n")
    lines.append("AUDIT_PASS — Medium ist veröffentlichbar." if ok_all
                 else "AUDIT_FAIL — PUBLISH-STOP: Defekte oben beheben, "
                      "dann neu auditieren.")
    (HERE / "audit_report.md").write_text("\n".join(lines) + "\n",
                                          encoding="utf-8")
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'} — {name} ({detail})")
    verdict = "AUDIT_PASS" if ok_all else "AUDIT_FAIL — PUBLISH-STOP"
    print(f"\nVERDICT: {verdict}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
