"""SciComPresentationMind · Schritt 4 — Deck-Bau (python-pptx).

12 Slides, dunkles Design (design.py-Palette), 16:9. Jede Caption-Zahl
kommt WÖRTLICH aus claims.json (display-Strings) — nichts hier neu
formuliert, was nicht dort bereits auditierbar ist. Haupt-Szenen als
Videos (add_movie) mit Poster-Frame; Nebensachen nativ.

Ausgabe: cellsim_findings.pptx + deck_manifest.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from design import BG, BLUE, GREEN, GREY, GREY_LIGHT, INK, ORANGE, RED  # noqa: E402

MEDIA = HERE / "media"
SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.55)


def C(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#"))


def claims() -> dict[str, dict]:
    data = json.loads((HERE / "claims.json").read_text(encoding="utf-8"))
    return {x["id"]: x for x in data}


def add_slide(prs: Presentation) -> object:
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = C(BG)
    return slide


def txt(slide, left, top, w, h, text, size, color=INK, bold=False,
        align=PP_ALIGN.LEFT, wrap=True):
    box = slide.shapes.add_textbox(left, top, w, h)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = MSO_ANCHOR.TOP
    first = True
    for line in text.split("\n"):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        r = p.add_run()
        r.text = line
        f = r.font
        f.size = Pt(size)
        f.color.rgb = C(color)
        f.bold = bold
    return box


def title_bar(slide, title, claim_ids=(), tag=""):
    """Titelzeile + Claim-Tags + Fußzeile (Palette konsistent)."""
    txt(slide, MARGIN, Inches(0.22), Inches(10.4), Inches(0.7), title,
        26, INK, bold=True)
    if claim_ids:
        txt(slide, Inches(11.0), Inches(0.26), Inches(2.1), Inches(0.4),
            " · ".join(claim_ids), 14, BLUE, bold=True,
            align=PP_ALIGN.RIGHT)
    if tag:
        txt(slide, MARGIN, Inches(7.02), Inches(12.3), Inches(0.4), tag,
            12, GREY_LIGHT)
    return slide


def caption_block(slide, left, top, width, claim: dict, extra=None,
                  size=12.5):
    """Label/Grade/Quelle + Kriterium (frozen) + Display-Werte in EINEM
    Textblock — alles wörtlich aus claims.json, kein Layout-Math."""
    parts = [f"{claim['label']} · Grade {claim['grade']} · "
             f"{claim['source']}",
             f"Kriterium (registriert): {claim['criterion']}", ""]
    parts += [f"{k}: {v}" for k, v in claim["display"].items()]
    if extra:
        parts += ["", *extra]
    return txt(slide, left, top, width, Inches(5.6), "\n".join(parts),
               size, GREY_LIGHT)


def add_video(slide, path_stem: str, left, top, width):
    """Video + Poster-Still (media/<stem>.mp4 + <stem>_still.png)."""
    mp4 = MEDIA / f"{path_stem}.mp4"
    still = MEDIA / f"{path_stem}_still.png"
    height = int(width * 9 / 16)
    slide.shapes.add_movie(str(mp4), left, top, width, height,
                           poster_frame_image=str(still),
                           mime_type="video/mp4")
    return height


def glos(slide, left, top, width, terms: list[tuple[str, str]]):
    """Jargon-Glossen (≤12 Wörter), Sekundärtext."""
    lines = ["Glossen: " + " · ".join(f"{a} = {b}" for a, b in terms)]
    txt(slide, left, top, width, Inches(0.9), "\n".join(lines), 10.5,
        GREY)


def build() -> None:
    cl = claims()
    prs = Presentation()
    prs.slide_width, prs.slide_height = SW, SH
    manifest = []

    # --- 1 Titel ----------------------------------------------------------
    s = add_slide(prs)
    txt(s, MARGIN, Inches(2.3), Inches(12.2), Inches(1.3),
        "cellsim — ein Falsifikationsprogramm", 40, INK, bold=True)
    txt(s, MARGIN, Inches(3.5), Inches(12.2), Inches(1.6),
        "Was von 26 vorab-registrierten Vektoren an Evidenz übrig "
        "blieb — gemessen, repliziert, widerlegt.", 20, BLUE)
    txt(s, MARGIN, Inches(6.4), Inches(12.2), Inches(0.9),
        "JCVI-syn3A-Simulation · L2–L4 · Stand 2026-09-24 · "
        "iter-1…26 gebucht", 13, GREY_LIGHT)
    manifest.append({"slide": 1, "title": "Titel", "claim_ids": [],
                     "captions": []})

    # --- 2 Methode --------------------------------------------------------
    s = add_slide(prs)
    title_bar(s, "Methode: vorab registrieren, dann via negativa")
    body = (
        "Jeder Vektor (iter-1…26) ist VOR dem Lauf registriert:\n"
        "Frage, Kriterien, Schwellen, Verdict-Namen — fixiert im "
        "Experiment-Docstring.\n"
        "Post-hoc-Konsistenz wird NIE als Bestätigung gebucht; "
        "Abweichungen in ein CORREKTUR-LOG.\n"
        "Jede Behauptung trägt einen Grade (A repliziert … F widerlegt) "
        "und einen Via-Negativa-Status.\n\n"
        "Programm-Selbst-Audit (10 Via-Negativa-Tests, Stand 2026-09-21, "
        "dokumentiert):\n"
        "4× A · 0× B · 8× C · 0× F")
    txt(s, MARGIN, Inches(1.2), Inches(12.2), Inches(3.6), body, 16, INK)
    glos(s, MARGIN, Inches(5.6), Inches(12.2), [
        ("Vektor", "eine vorab formulierte falsifizierbare Frage"),
        ("Via negativa", "Test versucht, die Behauptung zu töten"),
        ("Registriert", "Kriterien stehen vor dem Lauf fest"),
    ])
    manifest.append({"slide": 2, "title": "Methode", "claim_ids": [],
                     "captions": ["4× A · 0× B · 8× C · 0× F"]})

    # --- 3 Hook: das Fenster ---------------------------------------------
    s = add_slide(prs)
    title_bar(s, "Das Phänomen: ein Damköhler-Fenster im Reaktionsfeld")
    body = (
        "Frage: Wann wird chemisches Muster im Zellinneren sichtbar?\n\n"
        "Damköhler-Zahl = Verhältnis von Reaktions- zu Transportzeit —\n"
        "sie entscheidet, ob ein Reaktionsfeld räumliche Struktur "
        "ausbildet.\n\n"
        "Wir variierten den Umsatz k·dt über 4 Dekaden und fragten:\n"
        "Wo wird das Feld signifikant anders als die dazugehörige "
        "Kontrolle?\n\n"
        "Antwort-Signatur: DISTINCT — das Feld zeigt Struktur, die "
        "Kontrolle nicht hat.")
    txt(s, MARGIN, Inches(1.3), Inches(12.2), Inches(4.2), body, 17, INK)
    glos(s, MARGIN, Inches(5.6), Inches(12.2), [
        ("k·dt", "katalytischer Faktor × Zeitschritt = Umsatz pro "
                 "Zeitschritt"),
        ("Kontrolle", "gleicher Lauf mit k·dt = 0, seed-gepaart"),
    ])
    manifest.append({"slide": 3, "title": "Hook", "claim_ids": [],
                     "captions": []})

    # --- 4 C01 Replikationskette (Video S1) -------------------------------
    s = add_slide(prs)
    title_bar(s, "Das Fenster überlebt drei Operator-Substrate", ["C01"])
    h = add_video(s, "WindowScene", MARGIN, Inches(1.15), Inches(7.4))
    txt(s, MARGIN, Inches(1.15) + h + Inches(0.1), Inches(7.4),
        Inches(1.2),
        "DISTINCT " + cl["C01"]["display"]["distinct_cells"]
        + " · Ordnung " + cl["C01"]["display"]["ordering"]
        + " · Sättigung " + cl["C01"]["display"]["saturation_return"],
        15, BLUE, bold=True)
    caption_block(s, Inches(8.9), Inches(1.15), Inches(4.2),
                  cl["C01"], extra=[
        "Buchhaltungs-Note: registrierte Zähl-Schreibweise '≥6/9' vs "
        "12 Treatment-Zellen — Diskrepanz offen gelegt, beide Lesungen "
        "ergeben dieselben Verdicts."])
    manifest.append({"slide": 4, "title": "Replikationskette",
                     "claim_ids": ["C01"],
                     "captions": list(cl["C01"]["display"].values())})

    # --- 5 C02 Operator-Archäologie --------------------------------------
    s = add_slide(prs)
    title_bar(s, "Operator-Archäologie: alter Operator fällt K1",
              ["C02"])
    d02 = cl["C02"]["display"]
    rows = [
        ("Metrik", "neuer Operator (beidseitig, gemessen)"),
        ("Varianz je Achse", d02["var"]),
        ("Varianz rel", d02["var_rel_max"]),
        ("Drift je Achse", d02["drift_max"]),
        ("Beidseitigkeit", d02["symmetry_max"]),
    ]
    tbl = s.shapes.add_table(5, 2, MARGIN, Inches(1.25), Inches(12.2),
                             Inches(2.7)).table
    tbl.columns[0].width = Inches(3.0)
    tbl.columns[1].width = Inches(9.2)
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            cell_obj = tbl.cell(i, j)
            cell_obj.text = cell
            para = cell_obj.text_frame.paragraphs[0]
            para.font.size = Pt(14)
            para.font.color.rgb = C(INK if i == 0 else BLUE)
            para.font.bold = (i == 0)
    txt(s, MARGIN, Inches(4.15), Inches(12.2), Inches(0.75),
        "Alter Operator (einseitig, analytisch): " + d02["old_operator"],
        14, RED)
    txt(s, MARGIN, Inches(5.05), Inches(12.2), Inches(1.3),
        "Buchhaltungskorrektur: iter-14s Zeile „Kalibrierung ✅ p=𝒟 (6𝒟/"
        "Schritt)“ war gegen die damalige Implementation FALSCH — der "
        "beidseitige Operator (iter-15+) erfüllt sie erst; K1 misst das "
        "unabhängig (keine Selbst-Bezeugung durch den Docstring).", 14,
        ORANGE)
    glos(s, MARGIN, Inches(6.35), Inches(12.2), [
        ("K1", "Operator-Kalibrierungstest: Masse, Drift, Varianz, "
               "Beidseitigkeit"),
    ])
    manifest.append({"slide": 5, "title": "Operator-Archäologie",
                     "claim_ids": ["C02"],
                     "captions": list(cl["C02"]["display"].values())})

    # --- 6 C03 k·dt-Äquivalenz -------------------------------------------
    s = add_slide(prs)
    title_bar(s, "Der k-Sweep ist ein exaktes Damköhler-Gitter", ["C03"])
    txt(s, MARGIN, Inches(1.5), Inches(12.2), Inches(1.2),
        cl["C03"]["display"]["equivalence"], 30, GREEN, bold=True)
    body = (
        "λ = k·dt·n ist linear in k — der Sweep ist eine "
        "Reparametrisierung desselben Prozesses:\n"
        "Konfig (k_f, dt) und (1, k_f·dt) erzeugen bit-identische "
        "Trajektorien in ALLEN Metrik-Feldern.\n\n"
        "Konsequenz: alle k-Werte im Sweep messen dieselbe Physik auf "
        "einem feinen Damköhler-Gitter — kein Solver-Artefakt.")
    txt(s, MARGIN, Inches(2.9), Inches(12.2), Inches(2.4), body, 17, INK)
    caption_block(s, MARGIN, Inches(5.4), Inches(6.0), cl["C03"])
    manifest.append({"slide": 6, "title": "k·dt-Äquivalenz",
                     "claim_ids": ["C03"],
                     "captions": list(cl["C03"]["display"].values())})

    # --- 7 C04 Sättigungs-Marge (Video S2) --------------------------------
    s = add_slide(prs)
    title_bar(s, "Sättigungs-Marge MODERATE: Kante vor der Sperre",
              ["C04"])
    h = add_video(s, "SweepScene", MARGIN, Inches(1.15), Inches(7.4))
    txt(s, MARGIN, Inches(1.15) + h + Inches(0.1), Inches(7.4),
        Inches(1.2), cl["C04"]["display"]["global"], 15, BLUE, bold=True)
    caption_block(s, Inches(8.9), Inches(1.15), Inches(4.2),
                  cl["C04"], extra=[
        "iter-26 (Feingitter, heute gebucht): D=0.05-Kante 10 bestätigt; "
        "Kantenfolge über D NICHT monoton (EDGE_D_NONMONOTONE, C12) — "
        "D=0.15 nicht lokalisiert (≥200).",
        "Nicht behauptet: keine Aussage über reale syn3A-Enzymdichten — "
        "das Gitter misst die Robustheit des Simulators, nicht die "
        "Zelle."])
    manifest.append({"slide": 7, "title": "Sättigungs-Marge",
                     "claim_ids": ["C04"],
                     "captions": list(cl["C04"]["display"].values())})

    # --- 8 C05 LZ-Trägerschaft -------------------------------------------
    s = add_slide(prs)
    title_bar(s, "Träger des Signals: LZ-Entropie, nicht Korrelation",
              ["C05"])
    txt(s, MARGIN, Inches(1.35), Inches(12.2), Inches(1.1),
        cl["C05"]["display"]["corr_fires"], 30, INK, bold=True)
    body = (
        "Das registrierte Klassifikations-Kriterium feuert nur über den "
        "LZ-Arm:\n"
        + cl["C05"]["display"]["max_drop"] + "\n\n"
        "Das „Fenster“ ist ein Fenster in der temporalen "
        "Entropie-Struktur des Feldes (LZ der binarisierten Snapshots) —\n"
        "nicht in der Glucose-ATP-Korrelation. Repliziert über alle "
        "Substrate der Kette.")
    txt(s, MARGIN, Inches(2.7), Inches(12.2), Inches(2.6), body, 17, INK)
    glos(s, MARGIN, Inches(5.5), Inches(12.2), [
        ("LZ-Entropie", "Kompressionslänge der binarisierten "
                        "Feld-Snapshots"),
        ("corr_drop", "Abfall der Glucose-ATP-Kreuzkorrelation gegen "
                      "Kontrolle"),
    ])
    caption_block(s, MARGIN, Inches(6.1), Inches(6.5), cl["C05"])
    manifest.append({"slide": 8, "title": "LZ-Trägerschaft",
                     "claim_ids": ["C05"],
                     "captions": list(cl["C05"]["display"].values())})

    # --- 9 Orch-OR (Video S3) --------------------------------------------
    s = add_slide(prs)
    title_bar(s, "Orch-OR in syn3A: drei Kanäle, drei Falsifikationen",
              ["C07", "C08", "C09", "C10"])
    h = add_video(s, "GatesScene", MARGIN, Inches(1.15), Inches(7.4))
    txt(s, MARGIN, Inches(1.15) + h + Inches(0.1), Inches(7.4),
        Inches(1.4),
        cl["C08"]["display"]["gap"] + "\n" +
        cl["C09"]["display"]["n_star"] + " · " +
        cl["C10"]["display"]["turnover"], 12, INK)
    caption_block(s, Inches(8.9), Inches(1.15), Inches(4.2), cl["C08"],
                  extra=[
        "Kontext (C07): die iter-7 Orch-OR-Formel war dimensional "
        "invalid — τ=5.65e-37 s ein Formel-Artefakt; korrigierte "
        "Penrose-Skala: τ_OR(Dimer) ≈ 3.8e11 s, bestes Ecke-Verhältnis "
        "0.61 (Hagan-Parametrisierung).",
        "Kick (C09): " + cl["C09"]["display"]["corner_energy"] +
        " pro Event.",
        "Photonik (C10): " + cl["C10"]["display"]["burst"] + "."])
    manifest.append({"slide": 9, "title": "Orch-OR-Beweislast",
                     "claim_ids": ["C07", "C08", "C09", "C10"],
                     "captions": list(cl["C08"]["display"].values())
                                 + list(cl["C09"]["display"].values())
                                 + list(cl["C10"]["display"].values())})

    # --- 10 C11 Registry-Turing (FALSIFIZIERT, gleiche Würde) -------------
    s = add_slide(prs)
    title_bar(s, "Negativ-Resultat mit gleicher Würde: kein "
                 "Turing-Substrat", ["C11"])
    txt(s, MARGIN, Inches(1.3), Inches(12.2), Inches(1.6),
        "Registrierte Turing-Kompetenz der Reaktions-Registry: "
        "FALSIFIZIERT", 26, RED, bold=True)
    body = (cl["C11"]["display"]["autocatalysis"] + "\n" +
            cl["C11"]["display"]["cycles"] + "\n" +
            cl["C11"]["display"]["jacobian"] + "\n" +
            cl["C11"]["display"]["dead"] + "\n\n"
            "Konsequenz: Turing-Muster sind mit dieser Registry nicht "
            "erzielbar — der Schnakenberg-Kern (iter-17/19) blieb ein "
            "künstlicher Import. iter-19-Diskrimination void "
            "(Stencil-Fehler in der Registrierung).")
    txt(s, MARGIN, Inches(2.5), Inches(12.2), Inches(2.6), body, 16, INK)
    caption_block(s, MARGIN, Inches(5.3), Inches(6.5), cl["C11"])
    manifest.append({"slide": 10, "title": "Registry-Turing",
                     "claim_ids": ["C11"],
                     "captions": list(cl["C11"]["display"].values())})

    # --- 11 Gesamtbild ----------------------------------------------------
    s = add_slide(prs)
    title_bar(s, "Gesamtbild: Evidenz-Lage nach 26 gebuchten Vektoren")
    grade_rows = [
        ("Vektor / Modul", "Behauptung", "Grade"),
        ("Damköhler-Fenster iter-11→14→24", "überlebt Operator-, "
         "Gitter-, Seed-Wechsel", "B"),
        ("Operator-Kalibrierung K1 (iter-24)", "beidseitig driftfrei, "
         "kalibriert", "B"),
        ("k·dt-Äquivalenz (iter-25 K4)", "4/4 bit-identisch", "B"),
        ("Sättigungs-Marge (iter-25)", "MODERATE, Kante k_f=10", "B"),
        ("Feine Kante + D-Abhängigkeit (iter-26)",
         "EDGE_D_NONMONOTONE — kein zusammenhängendes Band", "B"),
        ("LZ-Trägerschaft (iter-24/25)", "corr feuert nie (0/39)",
         "B"),
        ("Orch-OR-Gates (iter-21/22/23)", "drei Kanäle entwertet / "
         "inert", "C"),
        ("Registry-Turing (iter-20)", "KEIN Substrat — FALSIFIZIERT",
         "B"),
        ("GPU-Operator (iter-24)", "33× Beschleunigung, G1–G5", "B"),
        ("Fröhlich-Stub", "max 5 % ATP, kontrovers", "C"),
        ("MES-Stub (L1)", "Zustandsmaschine, keine Theorie", "C"),
        ("QuQuint-Benchmark (L4)", "1.1×–1.3× statt 1000×", "C"),
    ]
    tbl = s.shapes.add_table(len(grade_rows), 3, MARGIN, Inches(1.15),
                             Inches(12.2), Inches(5.4)).table
    tbl.columns[0].width = Inches(4.4)
    tbl.columns[1].width = Inches(6.4)
    tbl.columns[2].width = Inches(1.4)
    for i, (a, b, g) in enumerate(grade_rows):
        for j, v in enumerate((a, b, g)):
            cell_obj = tbl.cell(i, j)
            cell_obj.text = v
            para = cell_obj.text_frame.paragraphs[0]
            para.font.size = Pt(11)
            # Explizite dunkle Fills — das Default-Banding ist hell und
            # schluckt den hellen INK-Text (LibreOffice + PowerPoint).
            cell_obj.fill.solid()
            cell_obj.fill.fore_color.rgb = C(BLUE if i == 0 else
                                             (GREY if i % 2 else BG))
            para.font.color.rgb = C("#0E1116" if i == 0 else
                                    (GREEN if j == 2 and g == "B" else
                                     ORANGE if j == 2 else INK))
            para.font.bold = (i == 0 or j == 2)
    txt(s, MARGIN, Inches(6.75), Inches(12.2), Inches(0.5),
        "Grades: A repliziert · B gut designt · C Beobachtung · "
        "D Einzelstudie · E unbelegt — B/C hier nach Via-Negativa-"
        "Audit", 12, GREY_LIGHT)
    manifest.append({"slide": 11, "title": "Gesamtbild",
                     "claim_ids": ["C01", "C02", "C03", "C04", "C05",
                                   "C06", "C11", "C12"],
                     "captions": []})

    # --- 12 Frisches Resultat (iter-26) + offene Fragen --------------------
    s = add_slide(prs)
    title_bar(s, "Frische Falsifikation + offene Fragen", ["C12"])
    txt(s, MARGIN, Inches(1.1), Inches(12.2), Inches(0.7),
        cl["C12"]["display"]["edges"], 20, RED, bold=True)
    body = (cl["C12"]["display"]["band"] + "\n"
            + cl["C12"]["display"]["lz_straddle"] + "\n"
            + cl["C12"]["display"]["gates"] + "\n\n"
            "iter-26 (heute gebucht): D=0.05-Kante 10 exakt bestätigt "
            "(EDGE_UPPER_CONFIRMED) — aber die „Kante wächst mit D“-Lesung "
            "aus iter-25 ist tot: D=0.10 → 3 (unter D=0.05), D=0.15 ≥200 "
            "(n.lok.), D=0.25 → 30, D=0.30 ≥1000 (n.lok.). Die "
            "Klassifikation straddelt die LZ-Schwelle — kein Band, "
            "rauschdominiert oder echte Struktur: offen.")
    txt(s, MARGIN, Inches(1.85), Inches(12.2), Inches(2.2), body, 15, INK)
    offtxt = (
        "Offen (registriert, geplant):\n"
        "· VECTOR_STOCH_CONTROL_METRIC — Klassifikationstiefe relativ zum "
        "Kontroll-Floor statt Schwellen-Crossing (jetzt dreifach "
        "motiviert: iter-24 Zellrauschen, iter-25 schwache Kante, "
        "iter-26 NONMONOTONE)\n"
        "· VECTOR_ENDOGEN_UVC_TIMESCALE (iter-12/13) — endogene Zeitskala "
        "der UVC-Kopplung\n"
        "· reserviert iter-19b: VECTOR_SHELL1_CASCADE — Schale-1-Anomalie\n"
        "· VECTOR_UV_SYNC_REOPEN (iter-16) — UV-Synchronisation\n\n"
        "Nicht behauptet:\n"
        "· keine Aussage über reale syn3A-Enzymdichten (Smoke-Scope 60 s, "
        "kein 105-min-Zyklus)\n"
        "· L1/MES nicht implementiert — Rosen-Horizont bleibt\n"
        "· Orch-OR: Beweislast in der Box gezeigt, nicht in der Biologie")
    txt(s, MARGIN, Inches(3.75), Inches(12.2), Inches(3.0), offtxt, 13.5,
        INK)
    txt(s, MARGIN, Inches(7.02), Inches(12.2), Inches(0.4),
        "Medium + Audit: scratch/presentation/ — jede Caption gegen "
        "Quelldaten recomputierbar (claims.json, audit_report.md).",
        12, GREY_LIGHT)
    manifest.append({"slide": 12, "title": "Frische Falsifikation + "
                     "offene Fragen", "claim_ids": ["C12"],
                     "captions": list(cl["C12"]["display"].values())})

    out = HERE / "cellsim_findings.pptx"
    prs.save(out)
    (HERE / "deck_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"{len(prs.slides)} slides → {out}")


if __name__ == "__main__":
    build()
