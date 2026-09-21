"""Iter-17: Turing-Instabilität im RDME (VECTOR_PATTERN_FORMATION).

Frage: Bildet die Sprung-Diffusions-Numerik + lokale Tau-Leap-Chemie
eine Turing-Instabilität aus uniformem Anfangszustand + Schuss-Rauschen
aus — und bei genau den Diffusions-Ratio-Werten, die die lineare
Stabilitätstheorie vorhersagt?

Chemie (Schnakenberg 1979, kanonisches Turing-Schema):
    ∅ → X        (Ω·a)        Feed (Aktivator-Quelle)
    X → ∅        (k2)         Zerfall
    2X + Y → 3X  (k1/Ω²)      Autokatalyse (Ordnung 3, Mass-Action in Counts)
    ∅ → Y        (Ω·b)        Feed (Inhibitor-Quelle)
X diffundiert langsam (D_u), Y schnell (D_v) — klassische
Aktivator-Inhibitor-Geometrie. Ω = Systemgröße: deterministische
Dynamik in u=X/Ω, v=Y/Ω ist Ω-invariant; demografisches Rauschen
skaliert mit 1/√Ω (Ω=200 → 7 %).

VORAB-REGISTRIERTE Falsifikations-Kriterien (fixiert vor dem Lauf):

  PATTERN_FORMED_QUANTITATIVE (pro instabil-predizierter Konfig):
    peak_excess ≥ 5  UND  band_ratio ≥ 3× matched-Null  UND
    k_peak innerhalb der analytischen Bandkanten (±15 %)  UND
    σ_meas ∈ [0.4·σ_pred, 2.5·σ_pred]  UND  Persistenz
    (σ(k_peak)/k_peak im letzten Quartal < 15 %).
  PATTERN_FORMED_NO_GROWTH_FIT: wie oben, aber σ-Fit nicht auswertbar
    oder außerhalb des Fensters (quantitativer Test offen).
  PATTERN_OFF_BAND: Peak + Kontrast, aber k_peak außerhalb der Bande.
  FALSIFIED_NO_PATTERN: peak_excess < 3 oder band_ratio < 3× Null in
    einer instabil-predizierten Konfig.
  ARTIFACT_PATTERN: das matched Null (D-Ratio=1, identische Chemie und
    Numerik) zeigt selbst peak_excess ≥ 5 → Gitter-/Operator-Artefakt.
  ONSET_MISMATCH: Muster (peak_excess ≥ 5 UND band_ratio ≥ 3× Null) in
    einer stabil-predizierten Konfig → Feed-Rauschen-getriebenes
    Numerik-Artefakt.

Quantitative Vorhersage (exakte diskrete lineare Stabilität, im Script
berechnet): σ(k) = max Re(Eigenwert(J − 2(1−cos k)·diag(D_u, D_v))) —
2(1−cos k) ist das exakte Eigenwert-Symbol des 6-Nachbar-Sprung-
Operators (nicht die Kontinuum-Näherung k²). Bandkanten = kontiguale
Region um argmax mit σ > 0. Parameter: a=0.35, b=0.65 (U=1), k1=0.5,
k2=1.0, Ω=400, D_u=0.06, dt=0.05, Gitter 24³, 800 Schritte.
Sweep D_v ∈ {0.25, 1.0, 3.0, 10.0}.

Kalibrierung des Arbeitspunkts (vorab registrierte Methode): die
Dispersionsrelation wird am GEMESSENEN homogenen Arbeitspunkt des
stochastischen Systems ausgewertet (aus dem matched-Null, D-Ratio=1),
nicht am deterministischen Fixpunkt angenommen. Begründung (gemessen,
iter-17-Vorbereitung): (a) Tau-Leap-Ordering-Bias — R2 auf
fortgeschriebenem x statt Schritt-Anfang verschiebt den Fixpunkt
Ω-unabhängig um ~5 %; (b) demografisches Rauschen erzeugt
corr(x, y) < 0 und Varianz-Inflation E[X²] ≫ Poisson, die die
Autokatalyse-Rate systematisch verschieben. Beides ist Physik des
stochastischen Systems, kein Bug — die Vorhersage muss am
tatsächlichen Arbeitspunkt gelten.

Diffusion: Produktionsoperator `stochastic_jump_diffusion` (iter-15,
beidseitig); Y wird via Substepping (p ≤ 0.3 pro Subschritt) auf D_v
gebracht — exaktes Substepping desselben Random Walks.
Chemie: synchrones Tau-Leaping (Propensities am Schritt-Anfang;
Ordnungs-Lektion oben), Feasibility-Cap nur gegen netto konsumierte
Spezies — der frühere x//2-Cap erzwang x≥2 pro Voxel und strangle die
Autokatalyse exakt im Turing-Regime; R3 als Net-Ereignis
{X:+1, Y:−1}.

Status: EXPERIMENT (scratch) — kein Produktionspfad. Sekundär: Audit
des Produktions-Registry auf Turing-fähige Topologie (Autokatalyse/
Aktivator-Inhibitor) mit ehrlicher Grenze: Net-Stöchiometrie
(species_change) verdeckt Autokatalyse-Loops.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from cellsim.core.rng import make_rng  # noqa: E402
from cellsim.modules.emergence import (  # noqa: E402
    radial_power_spectrum,
    stochastic_jump_diffusion,
)

# --- Parameter (fixiert) ----------------------------------------------

A_FEED, B_FEED = 0.35, 0.65      # U = a + b = 1
K1, K2 = 0.5, 1.0
OMEGA = 400.0                     # Systemgröße (Shot-Noise 1/√Ω ≈ 5 %)
DT = 0.05
D_X = 0.06                        # langsamer Aktivator (p=0.06, 1 Subschritt)
D_V_SWEEP = (0.25, 1.0, 3.0, 10.0)
GRID = (24, 24, 24)
N_STEPS = 800
SNAP_EVERY = 25
SEEDS = (300, 301, 302)
K_MIN = 0.15                      # Peak-Suche oberhalb (k≈0 ausklammern)
OUT_DIR = Path(__file__).resolve().parent / "out"


# --- Analytische Dispersionsrelation (exaktes Gitter-Symbol) ------------


def jacobian_at(u: float, v: float) -> tuple[float, float, float, float]:
    """Jacobian am Arbeitspunkt (u, v): (f_u, f_v, g_u, g_v) in u,v."""
    f_u = -K2 + 2.0 * K1 * u * v
    f_v = K1 * u**2
    g_u = -2.0 * K1 * u * v
    g_v = -K1 * u**2
    return f_u, f_v, g_u, g_v


def jacobian() -> tuple[float, float, float, float]:
    """Jacobian am deterministischen Fixpunkt (Referenz)."""
    u_star = A_FEED + B_FEED
    v_star = B_FEED / (K1 * u_star**2)
    return jacobian_at(u_star, v_star)


def sigma_at_k(k: float, d_v: float,
               jac: tuple[float, float, float, float]) -> float:
    """σ(k): max Re(Eigenwert(J − 2(1−cos k)·diag(D_u, D_v))).

    2(1−cos k) ist das exakte Eigenwert-Symbol des 6-Nachbar-Sprung-
    Operators pro Achse (identisch zur Kalibrierung in
    stochastic_jump_diffusion: Varianzwachstum 2·p pro Achse).
    """
    f_u, f_v, g_u, g_v = jac
    damp = 2.0 * (1.0 - math.cos(k))
    mat = np.array([[f_u - damp * D_X, f_v],
                    [g_u, g_v - damp * d_v]])
    return float(np.max(np.linalg.eigvals(mat).real))


def dispersion(d_v: float, jac: tuple[float, float, float, float]) -> dict:
    """Bandkanten (kontigual um argmax, σ > 0), schnellste Mode, σ_max."""
    ks = np.linspace(1e-3, math.pi, 600)
    sig = np.array([sigma_at_k(k, d_v, jac) for k in ks])
    i_star = int(np.argmax(sig))
    if sig[i_star] <= 1e-9:
        # Kontinuum-Margin für den Report: B²/(4A·k1)
        f_u, _, _, g_v = jac
        det_j = jac[0] * jac[3] - jac[1] * jac[2]
        bb = f_u * d_v + g_v * D_X
        margin = (bb * bb / (4.0 * D_X * d_v)) / (jac[0] * jac[3] - jac[1] * jac[2])
        return {"unstable": False, "band": None, "k_star": None,
                "sigma_max": 0.0, "margin": margin,
                "trace_j": jac[0] + jac[3], "det_j": det_j}
    # kontiguale instabile Region um das Maximum
    lo = i_star
    while lo > 0 and sig[lo - 1] > 0:
        lo -= 1
    hi = i_star
    while hi < sig.size - 1 and sig[hi + 1] > 0:
        hi += 1
    f_u, _, _, g_v = jac
    bb = f_u * d_v + g_v * D_X
    det_j = jac[0] * jac[3] - jac[1] * jac[2]
    margin = (bb * bb / (4.0 * D_X * d_v)) / det_j
    return {"unstable": True, "band": (float(ks[lo]), float(ks[hi])),
            "k_star": float(ks[i_star]), "sigma_max": float(sig[i_star]),
            "margin": margin, "trace_j": jac[0] + jac[3], "det_j": det_j}


def onset_threshold(jac: tuple[float, float, float, float]) -> float:
    """Kleinste D_v mit σ_max > 0 (numerische Bisektion, 40 Iterationen)."""
    lo, hi = 0.05, 100.0
    if not dispersion(hi, jac)["unstable"]:
        return float("nan")
    for _ in range(40):
        mid = math.sqrt(lo * hi)
        if dispersion(mid, jac)["unstable"]:
            hi = mid
        else:
            lo = mid
    return hi


# --- Simulation ---------------------------------------------------------


def init_state(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Uniformer Anfangszustand am Fixpunkt (Counts = Ω·u*) + Rauschen."""
    u_star = A_FEED + B_FEED
    v_star = B_FEED / (K1 * u_star**2)
    x = rng.poisson(OMEGA * u_star, size=GRID).astype(np.int64)
    y = rng.poisson(OMEGA * v_star, size=GRID).astype(np.int64)
    return x, y


def tau_leap(x: np.ndarray, y: np.ndarray,
             rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Tau-Leaping: alle Propensities vom Schritt-Anfang (synchron).

    Ordnungs-Lektion (iter-17): die frühere Sequenz (Feed → R3 → R2 auf
    fortgeschriebenem x) liess R2 auf x+Feed+R3 wirken → systematische
    R2-Überfeuerung (+8 %), Fixpunkt x=190 statt 200, Ω-unabhängig
    (Feed und Raten skalieren beide mit Ω). Synchrones Tau-Leaping
    (Propensities am Schritt-Anfang, Änderungen als Netto-Delta)
    eliminierst das.

    Mass-Action in Counts: R3-Propensity = k1·X²Y/Ω² (Ordnung 3).
    Net-Ereignis {X:+1, Y:−1} — Feasibility nur gegen netto konsumierte
    Spezies (Y für R3, X für R2).
    """
    lam_r3 = np.minimum(K1 * DT * x.astype(np.float64) ** 2 * y / OMEGA**2, 1e6)
    lam_r2 = np.minimum(K2 * DT * x.astype(np.float64), 1e6)
    n_r3 = np.minimum(rng.poisson(lam_r3), y)
    n_r2 = np.minimum(rng.poisson(lam_r2), x)
    x = x + rng.poisson(OMEGA * A_FEED * DT, size=GRID) + n_r3 - n_r2
    y = y + rng.poisson(OMEGA * B_FEED * DT, size=GRID) - n_r3
    return x, y


def simulate(d_v: float, seed: int, cfg_idx: int,
             chem: bool = True) -> list[dict]:
    """Ein Lauf; rohe Feld-Snapshots alle SNAP_EVERY Schritte.

    Spektrale Diagnostik wird post-hoc gerechnet (`analyze`), damit die
    Banden-Wahl frei ist (Arbeitspunkt-Kalibrierung läuft vor der
    Vorhersage).
    """
    rng = make_rng(seed, 17, cfg_idx)
    x, y = init_state(rng)
    n_sub = max(1, int(math.ceil(d_v / 0.3)))
    p_sub = d_v / n_sub
    snaps: list[dict] = []
    for step in range(1, N_STEPS + 1):
        if chem:
            x, y = tau_leap(x, y, rng)
        xd = {"X": x}
        stochastic_jump_diffusion(xd, D_X, rng)
        x = xd["X"]
        if d_v > 0.0:
            yd = {"Y": y}
            for _ in range(n_sub):
                stochastic_jump_diffusion(yd, p_sub, rng)
            y = yd["Y"]
        if step % SNAP_EVERY == 0:
            snaps.append({"step": step,
                          "field_x": x.astype(np.float32),
                          "field_y": y.astype(np.float32)})
    return snaps


def analyze(snaps: list[dict],
            band: tuple[float, float] | None) -> list[dict]:
    """Spektrale Diagnostik pro Snapshot (post-hoc, Bande als Argument)."""
    out: list[dict] = []
    for s in snaps:
        field = s["field_x"].astype(np.float64)
        k_vals, power = radial_power_spectrum(field)
        mask = k_vals > K_MIN
        row = {"step": s["step"], "k_peak": 0.0, "peak_excess": 0.0,
               "band_ratio": 0.0, "band_amp": 0.0,
               "mean": float(field.mean()),
               "mean_y": float(s["field_y"].mean(dtype=np.float64))}
        if mask.any():
            k_sel, p_sel = k_vals[mask], power[mask]
            pk = int(np.argmax(p_sel))
            row["k_peak"] = float(k_sel[pk])
            row["peak_excess"] = float(p_sel[pk]
                                       / max(np.median(p_sel), 1e-12))
            if band is not None:
                bmask = (k_vals >= band[0]) & (k_vals <= band[1])
                band_power = float(power[bmask].sum())
                total = float(power[mask].sum())
                row["band_amp"] = math.sqrt(band_power)
                row["band_ratio"] = (band_power / total
                                     if total > 0 else 0.0)
        out.append(row)
    return out


# --- Auswertung ---------------------------------------------------------


def sigma_fit(snaps: list[dict]) -> float:
    """σ_meas: Fit von log(Band-Amplitude) im Mittelwachstum (pro Schritt).

    Fit-Fenster vorab registriert: Snapshots mit Band-Amplitude in
    [0.1·A_sat, 0.5·A_sat] (unterhalb Sättigung, oberhalb Rauschboden).
    Weniger als 3 Punkte → nan.
    """
    amps = np.array([s["band_amp"] for s in snaps])
    if not np.isfinite(amps).all() or amps.size < 8:
        return float("nan")
    a_sat = float(np.median(amps[-max(1, amps.size // 4):]))
    sel = (amps > 0.1 * a_sat) & (amps < 0.5 * a_sat)
    if int(sel.sum()) < 3:
        return float("nan")
    steps = np.array([s["step"] for s in snaps], dtype=np.float64)
    return float(np.polyfit(steps[sel], np.log(amps[sel]), 1)[0])


def summarize(snaps: list[dict]) -> dict:
    last_q = snaps[-max(1, len(snaps) // 4):]
    peaks = np.array([s["k_peak"] for s in last_q])
    k_peak = float(np.median(peaks))
    return {
        "k_peak": k_peak,
        "peak_excess": float(np.median([s["peak_excess"] for s in last_q])),
        "band_ratio": float(np.median([s["band_ratio"] for s in last_q])),
        "band_amp": float(np.median([s["band_amp"] for s in last_q])),
        "mean_x": float(np.median([s["mean"] for s in last_q])),
        "mean_y": float(np.median([s["mean_y"] for s in last_q])),
        "persistenz": float(peaks.std() / k_peak) if k_peak > 0 else 0.0,
    }


def classify(pred: dict, meas: dict, null_band_ratio: float) -> str:
    if not pred["unstable"]:
        pattern_like = (meas["peak_excess"] >= 5.0
                        and meas["band_ratio"] >= 3.0 * null_band_ratio)
        return "ONSET_MISMATCH" if pattern_like else "STABLE_AS_PREDICTED"
    peak = meas["peak_excess"] >= 5.0
    above = meas["band_ratio"] >= 3.0 * null_band_ratio
    if not (peak and above):
        return "FALSIFIED_NO_PATTERN"
    if meas["persistenz"] >= 0.15:
        return "PATTERN_UNSTABLE"
    k1e, k2e = pred["band"]
    in_band = (k1e * 0.85) <= meas["k_peak"] <= (k2e * 1.15)
    sigma = meas.get("sigma_meas", float("nan"))
    quant = (not math.isnan(sigma)
             and 0.4 * pred["sigma_max"] <= sigma <= 2.5 * pred["sigma_max"])
    if in_band and quant:
        return "PATTERN_FORMED_QUANTITATIVE"
    if in_band:
        return "PATTERN_FORMED_NO_GROWTH_FIT"
    return "PATTERN_OFF_BAND"


# --- Sekundär: Registry-Audit ------------------------------------------


def registry_audit() -> dict:
    """Hat das Produktions-Registry Turing-fähige Topologie?

    Ehrliche Grenze: species_change speichert NET-Deltas; Autokatalyse
    (2X+Y→3X → net {X:+1, Y:-1}) ist daraus nicht entscheidbar. Geprüft
    werden deshalb nur sichtbare Strukturen: Feedback-Kandidaten
    (Spezies net-Produkt in einer, net-Substrat in anderer Reaktion).
    """
    from cellsim.modules.reactions import default_registry

    reg = default_registry()
    net_pos: dict[str, list[str]] = {}
    net_neg: dict[str, list[str]] = {}
    for rxn in reg.reactions:
        for sp, delta in rxn.species_change.items():
            if delta > 0:
                net_pos.setdefault(sp, []).append(rxn.name)
            elif delta < 0:
                net_neg.setdefault(sp, []).append(rxn.name)
    feedback = sorted(set(net_pos) & set(net_neg))
    return {
        "n_species": len(reg.species_ids),
        "n_reactions": len(reg.reactions),
        "feedback_candidates": feedback,
        "note": ("Net-Stöchiometrie verdeckt Autokatalyse; Turing-Substrat "
                 "nicht entscheidbar (VECTOR_REGISTRY_TURING_EXT)"),
    }


# --- Mean-Field-Null (räumliche Kopplung abgeschaltet) ------------------


def mean_field_null() -> dict:
    """ODE am Punkt: konvergiert zum homogenen Fixpunkt (keine Struktur)."""
    u, v = A_FEED + B_FEED + 0.05, B_FEED / (K1 * (A_FEED + B_FEED) ** 2) + 0.05
    for _ in range(20000):
        u += DT * (A_FEED - K2 * u + K1 * u * u * v)
        v += DT * (B_FEED - K1 * u * u * v)
    u_star, v_star = A_FEED + B_FEED, B_FEED / (K1 * (A_FEED + B_FEED) ** 2)
    return {"u_final": u, "v_final": v,
            "dev_u": abs(u - u_star), "dev_v": abs(v - v_star)}


# --- Haupt ---------------------------------------------------------------


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    u_det = A_FEED + B_FEED
    v_det = B_FEED / (K1 * u_det**2)
    print(f"Deterministischer Fixpunkt: u*={u_det:.3f}, v*={v_det:.3f} "
          f"(Counts: X*={OMEGA * u_det:.0f}, Y*={OMEGA * v_det:.1f})")

    # --- 1. Matched-Null zuerst: liefert Rauschboden UND Arbeitspunkt ---
    # (Vorab registrierte Kalibrierung: die Dispersionsrelation wird am
    #  gemessenen homogenen Arbeitspunkt des stochasticen Systems
    #  ausgewertet, nicht am deterministischen Fixpunkt angenommen —
    #  demografisches Rauschen verschiebt den Arbeitspunkt.)
    null_snaps = [simulate(D_X, seed, 90) for seed in SEEDS]
    mean_x_op = float(np.median([np.mean(s["field_x"], dtype=np.float64)
                                 for r in null_snaps
                                 for s in r[-max(1, len(r) // 4):]]))
    mean_y_op = float(np.median([np.mean(s["field_y"], dtype=np.float64)
                                 for r in null_snaps
                                 for s in r[-max(1, len(r) // 4):]]))
    u_op, v_op = mean_x_op / OMEGA, mean_y_op / OMEGA

    jac = jacobian_at(u_op, v_op)
    det_j = jac[0] * jac[3] - jac[1] * jac[2]
    print(f"Arbeitspunkt (gemessen, matched-Null): u={u_op:.4f}, "
          f"v={v_op:.4f} (Counts: {mean_x_op:.1f}, {mean_y_op:.1f})")
    print(f"Jacobian (am Arbeitspunkt): f_u={jac[0]:.3f}, f_v={jac[1]:.3f}, "
          f"g_u={jac[2]:.3f}, g_v={jac[3]:.3f}")
    print(f"traceJ={jac[0] + jac[3]:.3f} (<0: homogen stabil), "
          f"detJ={det_j:.3f}")
    print(f"Onset-Schwelle (numerisch, exaktes Gitter-Symbol, am "
          f"gemessenen Arbeitspunkt): D_v ≈ {onset_threshold(jac):.3f}\n")

    preds = {d: dispersion(d, jac) for d in D_V_SWEEP}
    preds[D_X] = dispersion(D_X, jac)
    for d, p in sorted(preds.items()):
        band_txt = (f"k∈[{p['band'][0]:.3f},{p['band'][1]:.3f}]"
                    if p["band"] else "stabil")
        k_txt = "—" if p["k_star"] is None else f"{p['k_star']:.3f}"
        print(f"  D_v={d:>6}: {band_txt}, k*={k_txt}, "
              f"σ*={p['sigma_max']:.4f}, Margin={p['margin']:.2f}")

    results: dict = {
        "operating_point": {"u": u_op, "v": v_op,
                            "mean_x": mean_x_op, "mean_y": mean_y_op,
                            "jacobian": list(jac),
                            "deterministic_fp": [u_det, v_det]},
        "predictions": {}, "runs": {}, "nulls": {},
    }
    for d, p in preds.items():
        results["predictions"][str(d)] = {
            "unstable": p["unstable"],
            "band": None if p["band"] is None else list(p["band"]),
            "k_star": p["k_star"], "sigma_max": p["sigma_max"],
            "margin": p["margin"], "trace_j": p["trace_j"],
            "det_j": p["det_j"],
        }

    # Referenz-Bande der instabilsten Konfig D_v=10
    band_ref = preds[10.0]["band"] if preds[10.0]["unstable"] else None
    assert band_ref is not None, "D_v=10 muss instabil sein"

    # Matched-Null: spektrale Diagnostik post-hoc mit band_ref
    null_rows = [summarize(analyze(r, band_ref)) for r in null_snaps]
    null_match = {
        "band_ratio": float(np.median([r["band_ratio"] for r in null_rows])),
        "peak_excess": float(np.median([r["peak_excess"] for r in null_rows])),
        "k_peak": float(np.median([r["k_peak"] for r in null_rows])),
    }
    artifact = null_match["peak_excess"] >= 5.0
    results["nulls"]["matched_dratio1"] = {**null_match, "artifact": artifact}
    print(f"\nNull (D-Ratio=1): band_ratio={null_match['band_ratio']:.4f}, "
          f"peak_excess={null_match['peak_excess']:.2f} "
          f"{'→ ARTIFACT_PATTERN' if artifact else ''}")

    diff_rows = [summarize(analyze(simulate(10.0, seed, 91, chem=False),
                                   band_ref))
                 for seed in SEEDS]
    null_diff = {
        "band_ratio": float(np.median([r["band_ratio"] for r in diff_rows])),
        "peak_excess": float(np.median([r["peak_excess"] for r in diff_rows])),
    }
    results["nulls"]["diffusion_only_dv10"] = null_diff
    print(f"Null (diffusion-only, D_v=10): "
          f"band_ratio={null_diff['band_ratio']:.4f}, "
          f"peak_excess={null_diff['peak_excess']:.2f}")

    mf = mean_field_null()
    results["nulls"]["mean_field"] = mf
    print(f"Null (mean-field ODE): dev_u={mf['dev_u']:.2e}, "
          f"dev_v={mf['dev_v']:.2e} (konvergiert homogen)\n")

    null_ref = null_match["band_ratio"]

    # --- Sweep ---
    for i, d in enumerate(D_V_SWEEP):
        pred = preds[d]
        band = pred["band"] if pred["unstable"] else band_ref
        rows = []
        for seed in SEEDS:
            snaps = simulate(d, seed, i)
            analyzed = analyze(snaps, band)
            s = summarize(analyzed)
            if pred["unstable"]:
                s["sigma_meas"] = sigma_fit(analyzed)
            rows.append(s)
        meas = {
            "k_peak": float(np.median([r["k_peak"] for r in rows])),
            "peak_excess": float(np.median([r["peak_excess"] for r in rows])),
            "band_ratio": float(np.median([r["band_ratio"] for r in rows])),
            "mean_x": float(np.median([r["mean_x"] for r in rows])),
            "mean_y": float(np.median([r["mean_y"] for r in rows])),
            "persistenz": float(np.median([r["persistenz"] for r in rows])),
        }
        if pred["unstable"]:
            sig = [r.get("sigma_meas", float("nan")) for r in rows]
            meas["sigma_meas"] = float(np.nanmedian(sig))
        verdict = classify(pred, meas, null_ref)
        results["runs"][str(d)] = {
            "verdict": verdict, "measured": meas,
            "predicted_unstable": pred["unstable"],
            "predicted_band": None if pred["band"] is None else list(pred["band"]),
            "predicted_sigma": pred["sigma_max"],
            "per_seed": rows,
        }
        sig_txt = ("" if not pred["unstable"]
                   else f", σ_meas={meas.get('sigma_meas', float('nan')):.4f} "
                        f"(σ_pred={pred['sigma_max']:.4f})")
        print(f"D_v={d:>6}: peak_excess={meas['peak_excess']:>6.2f}, "
              f"k_peak={meas['k_peak']:.3f}, "
              f"band_ratio={meas['band_ratio']:.4f}, "
              f"mean_x={meas['mean_x']:.1f}{sig_txt}")
        print(f"          → {verdict}")

    audit = registry_audit()
    results["registry_audit"] = audit
    print(f"\nRegistry-Audit: {audit['n_reactions']} Reaktionen, "
          f"{audit['n_species']} Spezies, Feedback-Kandidaten: "
          f"{audit['feedback_candidates'] or 'keine'}")
    print(f"  ({audit['note']})")

    (OUT_DIR / "result.json").write_text(json.dumps(results, indent=2))
    print(f"\n→ {OUT_DIR / 'result.json'}")


if __name__ == "__main__":
    main()
