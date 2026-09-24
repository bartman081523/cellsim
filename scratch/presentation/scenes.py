"""Manim-Szenen (SciComPresentationMind: Bewegung nur für das Phänomen;
eine Farbsemantik für das ganze Medium; Text statt MathTex — keine
LaTeX-Abhängigkeit).

S1 WindowScene    — Replikationskette iter-11/14/24 (Klassifikationsgitter)
S2 SweepScene     — k-Sweep + Metrik-Kante + Events-Plateau (iter-25)
S3 GatesScene     — Orch-OR-Beweislast: drei Kanäle (iter-21/22/23)

Render: manim -r 1920,1080 --fps 30 -ql scenes.py <Scene>
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from design import BG, BLUE, GREY, GREY_LIGHT, INK, ORANGE, RED
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    GrowFromEdge,
    LaggedStart,
    Line,
    Rectangle,
    Scene,
    Text,
    VGroup,
    VMobject,
    Write,
    config,
)

config.background_color = BG

EXP = Path(__file__).resolve().parents[1] / "experiments"
CLS_COLOR = {"DISTINCT": BLUE, "NULL": GREY, "RUNAWAY": RED,
             "CONTROL": "#232936"}


def load(it: str) -> dict:
    return json.loads((EXP / it / "result.json").read_text(encoding="utf-8"))


def frame(title: str, takeaway: str, criterion: str, source: str):
    """Scaffold-Rahmen: Titel oben links, Takeaway + Kriterium unten
    links, Quelle unten rechts (kollisionsfrei durch Linksbündung)."""
    t = Text(title, font_size=30, color=INK, weight="BOLD")
    t.to_edge(UP, buff=0.35).to_edge(LEFT, buff=0.7)
    ta = Text(takeaway, font_size=24, color=BLUE)
    ta.to_edge(DOWN, buff=0.4).to_edge(LEFT, buff=0.7)
    cr = Text("Kriterium (registriert): " + criterion, font_size=15,
              color=GREY_LIGHT).next_to(ta, UP, buff=0.16)
    cr.to_edge(LEFT, buff=0.7)
    so = Text("Quelle: " + source, font_size=13, color=GREY_LIGHT)
    so.to_corner(DOWN + RIGHT, buff=0.3)
    return t, ta, cr, so


class WindowScene(Scene):
    """S1 — Das Fenster überlebt drei Operator-Substrate (C01).

    Konsolidierte Tabelle: 9 Zeilen (3 Substrate × 3 D) × 4 Spalten
    (k·dt). Farbe trägt genau eine Variable: die Klassifikation.
    """

    GROUPS = (
        ("11", "iter-11 · Scratch-Hybrid · rint-Laplace · 16³ · Seeds 42–44",
         "iter-11"),
        ("14",
         "iter-14 · Produktionstack · einseitig (upwind) · 24³ · Seeds 100–102",
         "iter-14"),
        ("24", "iter-24 · Produktionstack · beidseitig · 24³ · Seeds 200–202",
         "iter-24"),
    )
    DTS = (1e-6, 1e-5, 1e-4, 1e-3)
    DS = (0.05, 0.15, 0.45)

    def construct(self) -> None:
        t, ta, cr, so = frame(
            "Das Damköhler-Fenster überlebt drei Operator-Substrate",
            "9/12 · 7/12 · 8/12 DISTINCT · Ordnung 3/3 · Sättigung True",
            "≥6 DISTINCT (per-Seed ≥2/3 gegen seed-gepaarte Kontrolle)",
            "iter-11/14/24 result.json")
        self.play(Write(t), FadeIn(so), run_time=1.0)

        # Spaltenköpfe (k·dt) — eine Zeile für die ganze Tabelle
        cw, ch = 0.95, 0.40
        x0 = -3.7
        heads = VGroup(*[
            Text(f"k·dt {dt:g}", font_size=12, color=GREY_LIGHT)
            .move_to([x0 + j * cw, 2.15, 0]) for j, dt in enumerate(self.DTS)])
        self.play(FadeIn(heads), run_time=0.5)

        y = 1.6
        row_y: dict[tuple[str, float], float] = {}
        for tag, _name, it in self.GROUPS:
            rows = {(r["diff_coeff"], r["dt_react"]): r["classification"]
                    for r in load(it)["rows"]}
            anims = []
            for _i, d in enumerate(self.DS):
                lab = Text(f"{tag} · D={d:g}", font_size=14,
                           color=GREY_LIGHT)
                lab.move_to([-4.3, y, 0], aligned_edge=RIGHT)
                anims.append(FadeIn(lab))
                for j, dt in enumerate(self.DTS):
                    box = Rectangle(width=cw - 0.15, height=ch - 0.06,
                                    fill_color=CLS_COLOR[rows[(d, dt)]],
                                    fill_opacity=0.95, stroke_width=0)
                    box.move_to([x0 + j * cw, y, 0])
                    anims.append(FadeIn(box, scale=0.6))
                row_y[(tag, d)] = y
                y -= 0.47
            self.play(LaggedStart(*anims, lag_ratio=0.03), run_time=1.1)
        # Substrat-Trennlinien + rechte Annotation je Substrat
        sep_anims, note_anims = [], []
        for gi, (_tag, name, _it) in enumerate(self.GROUPS):
            if gi < 2:
                sy = 1.6 - (3 * gi + 2.5) * 0.47
                sep_anims.append(Create(
                    Line([-6.5, sy, 0], [-0.4, sy, 0], color=GREY,
                         stroke_width=1)))
            gy = row_y[(self.GROUPS[gi][0], 0.15)]
            note_anims.append(FadeIn(Text(name, font_size=14,
                                          color=GREY_LIGHT)
                                     .move_to([0.5, gy, 0],
                                              aligned_edge=LEFT)))
        self.play(LaggedStart(*sep_anims, lag_ratio=0.3),
                  LaggedStart(*note_anims, lag_ratio=0.3), run_time=0.9)

        leg = VGroup(*[
            VGroup(Rectangle(width=0.3, height=0.2, fill_color=c,
                             fill_opacity=0.95, stroke_width=0),
                   Text(txt, font_size=13, color=GREY_LIGHT))
            .arrange(RIGHT, buff=0.1)
            for c, txt in ((BLUE, "DISTINCT (Feld sichtbar)"),
                           (GREY, "NULL (kontroll-nah)"))])
        leg.arrange(RIGHT, buff=0.35).move_to([0.5, 2.15, 0],
                                              aligned_edge=LEFT)
        self.play(FadeIn(leg), run_time=0.5)
        self.play(Write(cr), FadeIn(ta), run_time=1.0)
        self.wait(1.2)


class SweepScene(Scene):
    """S2 — Metrik-Kante + Substrat-Sperre (C04).

    Oben: Klassifikationsgitter über den k-Faktor (log-äquidistant).
    Unten, getrennter Streifen: Events-Kurve (Messung) mit Plateau.
    """

    KS = (1, 3, 10, 30, 100, 300, 1000, 3000, 10000)
    DS = (0.05, 0.15, 0.45)

    def construct(self) -> None:
        data = load("iter-25")
        rows = data["rows"]
        cellmap = {(r["diff_coeff"], r["k_factor"]): r["classification"]
                   for r in rows}
        ev = {(r["diff_coeff"], r["k_factor"]):
              r["mean"]["reaction_events_total"] for r in rows}
        edges = data["k_edges"]

        t, ta, cr, so = frame(
            "Sättigungs-Marge: Metrik-Kante vor der Substrat-Sperre",
            "Globale Kante k_f = 10 → SATURATION_MARGIN_MODERATE",
            "Kante = größtes k_f mit DISTINCT; Oberende DISTINCT ⇒ "
            "nicht lokalisiert",
            "iter-25 result.json (27 Zellen, GPU, Seeds 200–202)")
        self.play(Write(t), FadeIn(so), run_time=1.0)

        x0, dx = -4.4, 1.1
        logk = {k: x0 + i * dx for i, k in enumerate(self.KS)}
        for k in self.KS:
            lab = Text(f"{k:g}", font_size=14, color=GREY_LIGHT)
            lab.move_to([logk[k], 2.3, 0])
            self.play(FadeIn(lab), run_time=0.1)
        head = Text("k-Faktor (Registry-k × k_f, log-Abstand)",
                    font_size=14, color=GREY_LIGHT)
        head.move_to([logk[1000], 2.72, 0])
        self.play(FadeIn(head), run_time=0.3)

        y = 1.35
        cw = 0.95
        for d in self.DS:
            lab = Text(f"D = {d:g}", font_size=20, color=INK)
            lab.move_to([x0 - 0.95, y, 0], aligned_edge=RIGHT)
            self.play(FadeIn(lab), run_time=0.2)
            anims = []
            for k in self.KS:
                box = Rectangle(width=cw - 0.1, height=0.52,
                                fill_color=CLS_COLOR[cellmap[(d, k)]],
                                fill_opacity=0.95, stroke_width=0)
                box.move_to([logk[k], y, 0])
                anims.append(FadeIn(box, scale=0.6))
            self.play(LaggedStart(*anims, lag_ratio=0.05), run_time=0.8)
            y -= 1.0

        # Registrierte Kanten (orange) — inkl. Oberenden-Regel
        for _d, key in ((0.05, "0.05"), (0.15, "0.15")):
            e = int(edges[key]["k_edge"])
            ln = Line([logk[e], 1.65, 0], [logk[e], -0.95, 0],
                      color=ORANGE, stroke_width=4)
            v = Text(f"Kante {e}", font_size=15, color=ORANGE)
            v.next_to(ln, UP, buff=0.1)
            self.play(Create(ln), FadeIn(v), run_time=0.5)
        ln = Line([logk[10000], 1.65, 0], [logk[10000], -0.95, 0],
                  color=ORANGE, stroke_width=4)
        v = Text("Oberende DISTINCT → nicht lokalisiert", font_size=12,
                 color=ORANGE).next_to(ln, UP, buff=0.1)
        self.play(Create(ln), FadeIn(v), run_time=0.5)

        # Events-Kurve D=0.05 — eigener Streifen UNTER dem Gitter
        ax = Line([x0, -2.55, 0], [logk[10000], -2.55, 0],
                  color=GREY_LIGHT, stroke_width=1.5)
        curve = VMobject(color=BLUE, stroke_width=3)
        curve.set_points_as_corners([
            [logk[k], -2.55 + (ev[(0.05, k)] / 1.7e9) * 1.05, 0]
            for k in self.KS])
        alab = Text("Events (D=0.05, Messung)", font_size=14,
                    color=BLUE).next_to([x0, -2.55, 0], LEFT, buff=0.2)
        pl = Line([logk[300], -2.55, 0], [logk[300], -1.35, 0],
                  color=ORANGE, stroke_width=3)
        plab = Text("Events-Plateau ab k_f ≈ 300 → Substrat-Sperre",
                    font_size=13, color=ORANGE)
        plab.move_to([2.2, -1.15, 0], aligned_edge=LEFT)
        self.play(Create(ax), FadeIn(alab), run_time=0.5)
        self.play(Create(curve), Create(pl), FadeIn(plab), run_time=1.2)
        self.play(Write(cr), FadeIn(ta), run_time=1.0)
        self.wait(1.2)


class GatesScene(Scene):
    """S3 — Orch-OR-Beweislast: drei Kanäle entwertet (C08/C09/C10).

    Log-Skala-Balkenpaare: blau = Messwert, orange = registrierte
    Schwelle; Lücke in Rot (gleiche typografische Würde).
    """

    PAIRS = (
        ("Shielding", "S_max (Box)", 9900.99, "S_need (Ecke)", 612755.27,
         "62× zu wenig", 1e2, 1e6),
        ("Kick", "N* (τ=1 ms)", 1.744e11, "Box-Decke", 1e11,
         "1.74× über Decke", 1e10, 1e12),
        ("Photonik", "Turnover r=100 nm", 5.65e-5, "Fenster-Unterkante",
         0.1, "1.8e3× inert", 1e-6, 1e0),
    )

    def construct(self) -> None:
        t, ta, cr, so = frame(
            "Orch-OR: drei Kanäle, drei Falsifikationen",
            "Kein Kanal trägt in der Box — Beweislast auf zwei Floors",
            "Registrierte Schranken: S = 1/(φ+ε) · E_acc ≥ k_B·T · "
            "Φ_cap = P_ATP/E_photon",
            "iter-21/22/23 result.json")
        note = Text("Messwert (blau) vs registrierte Schwelle (orange) "
                    "— log-Skala", font_size=14, color=GREY_LIGHT)
        note.to_edge(RIGHT, buff=0.4).set_y(2.75)
        self.play(Write(t), FadeIn(so), FadeIn(note), run_time=1.0)

        y = 1.9
        for name, la, va, lb, vb, gap, lo, hi in self.PAIRS:
            lab = Text(name, font_size=24, color=INK)
            lab.to_edge(LEFT, buff=0.7).set_y(y)
            self.play(FadeIn(lab), run_time=0.25)
            span = math.log10(hi / lo)
            lx = math.log10(va / lo) / span * 4.6
            rx = math.log10(vb / lo) / span * 4.6
            bar_a = Rectangle(width=lx, height=0.44, fill_color=BLUE,
                              fill_opacity=0.95, stroke_width=0)
            bar_a.move_to([-2.7, y, 0], aligned_edge=LEFT).shift(
                RIGHT * lx / 2)
            bar_b = Rectangle(width=rx, height=0.44, fill_color=ORANGE,
                              fill_opacity=0.85, stroke_width=0)
            bar_b.move_to([-2.7, y - 0.58, 0], aligned_edge=LEFT).shift(
                RIGHT * rx / 2)
            t_a = Text(f"{la}: {va:.1e}", font_size=16, color=INK)
            t_b = Text(f"{lb}: {vb:.1e}", font_size=16, color=ORANGE)
            t_a.next_to(bar_a, RIGHT, buff=0.15)
            t_b.next_to(bar_b, RIGHT, buff=0.15)
            g = Text(gap, font_size=18, color=RED)
            g.to_edge(RIGHT, buff=0.6).set_y(y - 0.29)
            self.play(GrowFromEdge(bar_a, LEFT), FadeIn(t_a), run_time=0.55)
            self.play(GrowFromEdge(bar_b, LEFT), FadeIn(t_b), run_time=0.55)
            self.play(FadeIn(g), run_time=0.3)
            y -= 1.85
        self.play(Write(cr), FadeIn(ta), run_time=1.0)
        self.wait(1.2)
