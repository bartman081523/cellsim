#!/usr/bin/env python
"""iter-17 CORREKTUR-LOG: Einheiten-Bug in der Dispersions-Analyse.

Fehler (im Analyse-Layer, NICHT im Simulator):
  Die vorab registrierte Disperson behandelte D_u/D_v als kontinuierliche
  Raten pro Zeiteinheit. Das Sprung-Diffusions-Schema liefert sie aber
  PRO SCHRITT (n_sub·p_sub = D; Varianzzuwachs 2D pro Schritt pro Achse).
  Die korrekte kontinuierliche Entsprechung ist D_eff = D/DT (= Faktor 20
  bei DT=0.05).

  Die Onset-Schwelle ist davon UNBERÜHRT (analytisch dt-invariant:
  (f_u·D_v + g_v·D_u)² > 2·D_u·D_v·det_J, dt kürzt sich exakt heraus) —
  deshalb war die Lauf-Vorhersage D_v ≈ 1.556 korrekt.

  Die Banden-Position ist dt-ABHÄNGIG (Bandkanten d = 2(1-cos k) skalieren
  mit dt; k mit sqrt(dt)): Vorhersage [0.850, 3.142] → korrekt [0.186, 0.456]
  bei D_v=3. Die gemessenen Peaks 0.262/0.370/0.453 sind exakt die drei
  Gitter-Moden der n=1-Schale — die einzigen Moden in der korrigierten
  Bande (0.453 < 0.456, knapp; 0.524 = n=(2,0,0) liegt außerhalb).

Output (2026-09-21):
  D_v=0.25: stabil | D_v=1.0: stabil
  D_v=  3.0: Bande k in [0.186, 0.456], k*=0.292 (lambda*=21.5 Vox),
             sigma*=+0.0808/t = +0.00404/Schritt
  D_v= 10.0: Bande k in [0.094, 0.490], k*=0.222 (lambda*=28.3 Vox),
             sigma*=+0.1763/t = +0.00881/Schritt
  Onset: D_v = 1.556 pro Schritt (dt-invariant, analytisch bestätigt)
"""

from __future__ import annotations

import math

FU, FV, GU, GV, DT = 0.297, 0.500, -1.297, -0.500, 0.05
DU_STEP = 0.06  # pro Schritt


def sigma_correct(k: float, dv_step: float) -> float:
    """Korrigierte Disperson: exaktes Gitter-Symbol 2(1-cos k), D/dt."""
    du, dv = DU_STEP / DT, dv_step / DT
    d = 2.0 * (1.0 - math.cos(k))
    mat = [[FU - d * du, FV], [GU, GV - d * dv]]
    tr = mat[0][0] + mat[1][1]
    det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    disc = tr * tr / 4.0 - det
    if disc < 0:
        return tr / 2.0
    return tr / 2.0 + math.sqrt(disc)


def band(dv_step: float) -> tuple[float, float, float, float] | None:
    ks = [1e-4 + i * (math.pi - 1e-4) / 1999 for i in range(2000)]
    sig = [sigma_correct(k, dv_step) for k in ks]
    imax = max(range(len(ks)), key=lambda i: sig[i])
    if sig[imax] <= 0:
        return None
    step = ks[1] - ks[0]
    lo = hi = ks[imax]
    while lo - step > 0 and sig[max(int((lo - step) / step), 0)] > 0:
        lo -= step
    while hi + step <= math.pi and sig[min(int((hi + step) / step), 1999)] > 0:
        hi += step
    return (lo, hi, ks[imax], sig[imax])


def main() -> None:
    for dv in (0.25, 1.0, 3.0, 10.0):
        b = band(dv)
        if b is None:
            print(f"D_v={dv:>5}: stabil (korrigiert)")
        else:
            print(
                f"D_v={dv:>5}: Bande k in [{b[0]:.3f}, {b[1]:.3f}]"
                f"  k*={b[2]:.3f} (lambda*={2 * math.pi / b[2]:.1f} Vox)"
                f"  sigma*={b[3]:+.4f}/t = {b[3] * DT:+.5f}/Schritt"
            )
    # Onset: bisection über max_k sigma (dv_step in pro-Schritt-Einheiten)
    lo, hi = 0.05, 100.0

    def sigma0(dv_step: float) -> float:
        ks = [1e-4 + i * (math.pi - 1e-4) / 3999 for i in range(4000)]
        return max(sigma_correct(k, dv_step) for k in ks)

    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if sigma0(mid) > 0:
            hi = mid
        else:
            lo = mid
    print(f"Onset (korrigiert): D_v = {math.sqrt(lo * hi):.4f} pro Schritt")
    band3 = band(3.0)
    if band3 is not None:
        print(
            "Gemessene Peaks 0.262/0.370/0.453 vs korrigierte Bande bei"
            f" D_v=3: [{band3[0]:.3f}, {band3[1]:.3f}]"
            " -> exakt die n=1-Schalen-Moden des Gitters"
        )


if __name__ == "__main__":
    main()
