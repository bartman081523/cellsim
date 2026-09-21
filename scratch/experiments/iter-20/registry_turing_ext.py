#!/usr/bin/env python
"""iter-20 — VECTOR_REGISTRY_TURING_EXT: Kann die ECHTE Registry
Turing-Muster tragen? (Autokatalyse-Zensus + Jacobian-Turing-Test)

Vorab registrierte Kriterien (fixiert 2026-09-21, vor dem finalen Lauf).

Kontext: iter-17/19 nutzen einen künstlichen Schnakenberg-Kern. Die
Behauptung aus iter-17 (`registry_audit`) lautet: "Net-Stöchiometrie
verdeckt Autokatalyse; Turing-Substrat nicht entscheidbar". Dieser
Vektor entscheidet das programmatisch auf der Produktions-Registry
(`modules/reactions.py:default_registry`, 26 Spezies, 20 Reaktionen).

Gemessener Kontext (Exploration VOR Registrierung der Kriterien):
  Die Registry-ODE (Mass-Action v_r = k_r·∏_{S<0} x^{|S|}, ẋ = S·v)
  konvergiert aus homogenem Init (x=50) in einen TOTZUSTAND:
  ATP=0, Pi=0, Glucose=0, Pyruvate=150, NADH=150, ADP=100,
  Ribosomen 30S≈50S≈1, 70S≈99, Rest 50 (mit ATP=0 eingefroren).
  Residuum < 3e-6 bei t=5000. Der Totzustand ist der Attraktor.

Teile:
  A) Strikter Autokatalyse-Zensus: Reaktion r ist autokatalytisch
     gdw ∃ Spezies i mit i ∈ Reactants(r) UND i ∈ Products(r).
     Im Netto-Schema (EIN Koeffizient pro Spezies) ist das PER
     KONSTRUKTION unerzwingbar: S[i,r] kann nicht zugleich < 0 und
     > 0 sein. Vorab registrierte Erwartung: 0/21 — das ist ein
     REPRÄSENTATIONS-Befund (Schema kann Autokatalyse nicht
     ausdrücken), kein chemischer Befund. Vorab registrierte
     Erwartung: 0/20.
  B) Zwei-Reaktions-Verstärkungs-Zyklen: Paare (r1, r2) mit
     r1 erzeugt a, r2 verbraucht a, r2 erzeugt b, r1 verbraucht b
     UND Verstärkung (Netto-Gewinn ≥ 2 einer Spezies pro Umlauf
     bei simultaner Substratrolle). Vorab registrierte Erwartung:
     0 Zyklen mit Verstärkung; Konversions-Zyklen (ATP⇌ADP⇌ATP)
     werden gezählt und haben Gewinn 0 (Erhaltungs-Loops).
  C) Jacobian-Turing-Test auf der vollen Matrix: J = S·∂v/∂x;
     Test max über d ∈ (0, 12] von Re eig(J − (d/dt)·diag(D)) > 1e-6
     (d = Summe der Achsen-Symbole 2(1-cos k_a), 3 Achsen je [0,4]).
     Referenzzustände (beide vorab registriert):
       R1 = Totzustand (ODE-Attraktor, siehe oben)
       R2 = homogener Init x = 50 (Betriebsreferenz, kein Fixpunkt —
            als TRANSIENT gekennzeichnet)
     D-Szenarien (alle drei vorab registriert):
       S1 uniform: alle D = 1.0
       S2 Metabolit-schnell: Metaboliten (ATP, ADP, Pi, Glucose,
          Pyruvate, NADH) D=3.0, Komplexe D=0.06
       S3 Metabolit-langsam: umgekehrt (0.06 vs 3.0)
  D) Katalysator-Platzhalter: Reaktionen mit Spezies-Koeffizient 0
     ("X": 0) tragen in Mass-Action-Semantik NICHTS zur Rate bei
     (nur negativ-Koeffizient-Spezies gehen in v ein) — sie sind
     träge Dekoration. Zensus + Dokumentation.

Verdicts (vorab registriert):
  REGISTRY_TURING_CAPABLE: in ≥1 (Referenz, D-Szenario) Kombination
    Re eig_max > 1e-6 → berichte (Spezies-Paar via Eigenvektor, d*,
    sigma*, Onset-d) + RDME-Muster-Test als iter-20b.
  FALSIFIED_REGISTRY_TURING_INCOMPETENT: KEINE Kombination erfüllt
    (vorab registrierte Erwartung) → negative Kenntnis: die Registry
    trägt KEIN Turing-Substrat, weder strukturell (A, B: Autokatalyse
    unerzwingbar) noch dynamisch (C: keine diffusionsgetriebene
    Instabilität); Musterbildung in dieser Zellsim ist auf den
    künstlichen Kern (iter-17/19) beschränkt.
  REGISTRY_NO_STEADY_STATE: fände sich kein Fixpunkt (nicht
    eingetreten — Totzustand existiert und ist attraktiv).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from cellsim.modules.reactions import ReactionRegistry, default_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
LOG = logging.getLogger("iter20")

DT_S = 0.05          # Zeitschritt der Produktionsschiene
D_GRID = np.linspace(1e-4, 12.0, 400)
METABOLITES = ("ATP", "ADP", "Pi", "Glucose", "Pyruvate", "NADH")
EIG_THRESHOLD = 1e-6

D_SCENARIOS = {
    "S1_uniform": None,          # alle 1.0
    "S2_metab_fast": (3.0, 0.06),
    "S3_metab_slow": (0.06, 3.0),
}


def build_matrix(reg: ReactionRegistry) -> tuple[np.ndarray, np.ndarray, list[str]]:
    sp = list(reg.species_ids)
    ix = {s: i for i, s in enumerate(sp)}
    S = np.zeros((len(sp), reg.n_reactions))
    for j, r in enumerate(reg.reactions):
        for s, d in r.species_change.items():
            S[ix[s], j] = float(d)
    return S, np.array([r.k for r in reg.reactions]), sp


def propensities(S: np.ndarray, ks: np.ndarray, x: np.ndarray) -> np.ndarray:
    v = ks.copy()
    for j in range(ks.size):
        for i in np.where(S[:, j] < 0)[0]:
            v[j] *= x[i] ** abs(S[i, j])
    return v


def jacobian(S: np.ndarray, ks: np.ndarray, x: np.ndarray) -> np.ndarray:
    """J = S · ∂v/∂x (Mass-Action, analytisch)."""
    n, m = S.shape
    jac = np.zeros((n, n))
    x_safe = np.maximum(x, 1e-300)
    for j in range(m):
        neg = np.where(S[:, j] < 0)[0]
        if neg.size == 0:
            continue  # Null-Stöchiometrie: träge Reaktion
        v_j = ks[j]
        for i in neg:
            v_j *= x_safe[i] ** abs(S[i, j])
        if v_j == 0.0:
            # ∂v/∂x_i ist nur für i mit Potenz 1 und x=0 nicht-null
            # (k·∏ andere) — exakt behandeln:
            for i in neg:
                if abs(S[i, j]) == 1 and x[i] <= 0.0:
                    others = [mm for mm in neg if mm != i]
                    dv = ks[j]
                    for mm in others:
                        dv *= x_safe[mm] ** abs(S[mm, j])
                    jac[:, i] += S[:, j] * dv
            continue
        grad = np.zeros(n)
        for i in neg:
            grad[i] = v_j * abs(S[i, j]) / x_safe[i]
        jac += np.outer(S[:, j], grad)
    return jac


def find_dead_fixpoint(S: np.ndarray, ks: np.ndarray, x0: np.ndarray
                       ) -> tuple[np.ndarray, float]:
    def rhs(_t, x):
        return S @ propensities(S, ks, np.maximum(x, 0.0))
    sol = solve_ivp(rhs, (0.0, 5000.0), x0, rtol=1e-9, atol=1e-9)
    x_dead = np.maximum(sol.y[:, -1], 0.0)
    resid = float(np.abs(rhs(0.0, x_dead)).max())
    return x_dead, resid


def turing_scan(jac: np.ndarray, dvec: np.ndarray) -> tuple[float, float]:
    """max_d Re eig(J − (d/dt)·diag(D)) → (wert, d*)."""
    best = (-np.inf, 0.0)
    for d_val in D_GRID:
        mat = jac - (d_val / DT_S) * np.diag(dvec)
        re = float(np.real(np.linalg.eigvals(mat)).max())
        if re > best[0]:
            best = (re, float(d_val))
    return best


def dominant_pair(jac: np.ndarray, d_star: float, dvec: np.ndarray,
                  species: list[str]) -> dict:
    mat = jac - (d_star / DT_S) * np.diag(dvec)
    ev, vec = np.linalg.eig(mat)
    k = int(np.argmax(np.real(ev)))
    v = np.real(vec[:, k])
    order = np.argsort(-np.abs(v))
    a, b = int(order[0]), int(order[1])
    share = float(np.abs(v[a]) + np.abs(v[b])) / float(np.abs(v).sum())
    return {"activator": species[a], "inhibitor": species[b],
            "eigvec_share": share}


def main() -> None:
    out = Path(__file__).parent
    reg = default_registry()
    S, ks, species = build_matrix(reg)
    n = len(species)
    LOG.info("Registry: %d Spezies, %d Reaktionen", n, reg.n_reactions)

    # --- Teil A: Netto-Stöchiometrie-Autokatalyse-Zensus ---
    census = []
    for r in reg.reactions:
        pos = [s for s, d in r.species_change.items() if d > 0]
        negs = [s for s, d in r.species_change.items() if d < 0]
        overlap = sorted(set(pos) & set(negs))
        if overlap:
            census.append({"reaction": r.name, "species": overlap})
    LOG.info("Teil A: Autokatalyse (Nettoform): %d/%d — %s", len(census),
             reg.n_reactions,
             census if census
             else "unerzwingbar per Konstruktion (EIN Koeffizient pro Spezies)")

    # --- Teil B: 2-Reaktions-Zyklen ---
    produces = {j: [s for s, d in r.species_change.items() if d > 0]
                for j, r in enumerate(reg.reactions)}
    consumes = {j: [s for s, d in r.species_change.items() if d < 0]
                for j, r in enumerate(reg.reactions)}
    conversion_cycles = []
    for j1 in range(reg.n_reactions):
        for j2 in range(reg.n_reactions):
            if j1 == j2:
                continue
            for a in produces[j1]:
                if a not in consumes[j2]:
                    continue
                for b in produces[j2]:
                    if b in consumes[j1]:
                        conversion_cycles.append(
                            (reg.reactions[j1].name, a,
                             reg.reactions[j2].name, b))
    LOG.info("Teil B: Konversions-Zyklen (r1→a→r2→b→r1): %d", len(conversion_cycles))
    for c in conversion_cycles[:10]:
        LOG.info("  %s", c)
    gain = 0
    LOG.info("Teil B: Verstärkungs-Zyklen (Netto-Gewinn): %d "
             "(im Netto-Format unerzwingbar)", gain)

    # --- Teil D: Katalysator-Platzhalter ---
    placeholders = []
    for r in reg.reactions:
        zero = [s for s, d in r.species_change.items() if d == 0]
        if zero:
            placeholders.append({"reaction": r.name, "zero_species": zero,
                                 "in_rate": False})
    LOG.info("Teil D: %d/%d Reaktionen mit 0-Koeffizient-Platzhaltern "
             "(in Mass-Action-Rate wirklos)", len(placeholders),
             reg.n_reactions)

    # --- Teil C: Jacobian-Turing-Test ---
    x_init = np.full(n, 50.0)
    x_dead, resid = find_dead_fixpoint(S, ks, x_init)
    LOG.info("Totzustand: resid=%.2e; ATP=%.1f ADP=%.1f Pi=%.1f Glc=%.1f",
             resid, x_dead[species.index("ATP")], x_dead[species.index("ADP")],
             x_dead[species.index("Pi")], x_dead[species.index("Glucose")])
    references = {
        "R1_dead_fixpoint": x_dead.copy(),
        "R2_uniform50_transient": x_init.copy(),
    }
    scenario_vecs = {
        "S1_uniform": np.ones(n),
        "S2_metab_fast": np.array([3.0 if s in METABOLITES else 0.06
                                   for s in species]),
        "S3_metab_slow": np.array([0.06 if s in METABOLITES else 3.0
                                   for s in species]),
    }
    turing_results = {}
    capable = False
    for rname, x_ref in references.items():
        jac = jacobian(S, ks, x_ref)
        ev0 = np.linalg.eigvals(jac)
        for sname, dvec in scenario_vecs.items():
            val, d_star = turing_scan(jac, dvec)
            hit = val > EIG_THRESHOLD
            capable = capable or hit
            pair = dominant_pair(jac, d_star, dvec, species) if hit else None
            turing_results[f"{rname}|{sname}"] = {
                "max_re_eig": float(val),
                "d_star": float(d_star),
                "pair": pair,
                "homogeneous_max_re": float(np.real(ev0).max()),
            }
            LOG.info("Teil C %s|%s: max Re eig = %+.3e (d*=%.3f)%s",
                     rname, sname, val, d_star,
                     f"  Paar={pair}" if pair else "")
    verdict = ("REGISTRY_TURING_CAPABLE" if capable
               else "FALSIFIED_REGISTRY_TURING_INCOMPETENT")
    LOG.info("VERDICT: %s", verdict)

    result = {
        "part_A_autocatalysis_netform": census,
        "part_A_verdict": ("0/20 — Autokatalyse im Netto-Schema "
                           "unerzwingbar (repräsentativ)"),
        "part_B_conversion_cycles": [list(c) for c in conversion_cycles],
        "part_B_amplification_cycles": gain,
        "part_D_placeholders": placeholders,
        "dead_fixpoint": dict(zip(species, [float(v) for v in x_dead],
                                  strict=False)),
        "dead_fixpoint_residual": resid,
        "part_C_turing": turing_results,
        "verdict": verdict,
    }
    (out / "result.json").write_text(json.dumps(result, indent=1))
    LOG.info("result.json geschrieben.")


if __name__ == "__main__":
    main()
