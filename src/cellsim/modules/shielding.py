"""Ortsaufgelöstes Dekohärenz-Feld (L4-Brücke) — iter-21 VECTOR_SHIELDING_FIELD.

Frage (vorab registriert, vor jedem Lauf): Ist das iter-16-Schild
S=1e6 in ORConfig (HYPOTHESE-Konstante) mechanistisch ableitbar — oder
stirbt die großzügige Hagan-Ecke (f=5e-2, a=8 nm, N=1e9, korreliert)?

Zentrale physikalische Aussage der Registrierung:
  Die registrierte iter-16-Bilanz für τ_dec ist Tegmarks
  KOLLISIONS-Kanal (τ_dec = ħ/(k_B·T·(Δm/m)²), S=1 → Bulk-Grenze).
  Debye-Screening schirmt FELD-Kanäle (elektrostatische Kopplung an
  die Ionen-Atmosphäre) ab — NICHT Kontakt-Kollisionen. Auf den
  registrierten Kollisions-Kanal wirken daher nur zwei Hebel:

    M1  Streuter-Ausschluss: Γ ∝ Flux freier Wassermoleküle im Kern;
        gebundenes/geordnetes Wasser (Hydrationshülle, Cytogel)
        trägt nur mit ε_res bei. S_1 = 1/(φ_free + ε_res).
    M2  Formfaktor: thermale Wassermoleküle haben λ_deB ≈ 0.023 nm
        ≪ Δx = 8 nm → volle Pfad-Auflösung, KEINE Unterdrückung.
        Registriert als GESCHLOSSEN (S_2 = 1) — verhindert falsches
        Shielding durch Wellenlängen-Argumente.

  Registrierte Schranken (Literatur-verankert, großzügig):
    φ_free ≥ 1e-4  (dichtes Cytogel + Hydrationshüllen; selbst in
                    dichten Gelen bleibt ~1 % bulk-artiges Wasser)
    ε_res  ∈ {1e-2 (PESSIMISTISCH: gebundenes Wasser dekohäriert
                    ≥ 1 % der Bulk-Rate — klassisches Bad),
              1e-6 (OPTIMISTISCH: Motional-Narrowing mit schneller
                    Korrelationszeit ~ ps und kleinem Branch-Coupling)}
    Δm/m   ∈ [1e-4, 1e-2]  (Konformations-Achse M4: iter-16 fixierte
                    1e-2; der Floor 1e-4 ist die großzügige
                    Konform-Superposition-HYPOTHESE)

  Ausgeschlossene Kanäle (registrierte Best-Fall-Wahl zugunsten von
  Orch-OR): Γ_ion (Ionen-Feld-Kanal) wird zu 0 gesetzt — jeder
  κ_ion > 0 verschlechtert das Überleben nur. Debye-Screening (λ_D)
  tritt daher NICHT als Rettungshebel auf.

  Konsistenz-Haken zur Vector-Kette: der EINZIGE Weg zu ε_res ≪ 1e-6
  läuft über ein Fröhlich-artiges kohärentes Schild (gebundenes Wasser
  als Teil des Quantensystems) — genau die Annahme, die in diesem Repo
  durch Reimers 2010 (VECTOR_FROEHLICH_CONDENSATION) bereits als
  REFUTED gebucht ist.

Claim-Deckel: dieses Modul leitet OB das Schild S≈1e6 innerhalb
klassischer Bad-Physik ableitbar ist. Es behauptet NICHT, dass Orch-OR
falsch oder richtig ist — die Konsequenzen trägt die Verdict-Logik im
Experiment (scratch/experiments/iter-21, Kriterien G1-G4 vor dem Lauf).
"""

from __future__ import annotations

from dataclasses import dataclass

from cellsim.modules.orch_or import KB, ORConfig, penrose_tau_or_s

# --- Registrierte Schranken (VOR dem Lauf fixiert; siehe Modul-Docstring) ---

PHI_FREE_FLOOR = 1e-4          # M1: minimaler bulk-artiger Wasseranteil
EPS_RES_PESSIMISTIC = 1e-2     # M1: gebundenes Wasser, klassisches Bad
EPS_RES_OPTIMISTIC = 1e-6      # M1: Motional-Narrowing (großzügig)
DELTA_M_FLOOR = 1e-4           # M4: Konform-Superposition (großzügig)
DELTA_M_ITER16 = 1e-2          # M4: iter-16-Fixierung (Tegmark-Bulk)
KAPPA_ION_BEST_CASE = 0.0      # Ionen-Kanal ausgeschlossen (Best-Fall)


@dataclass(frozen=True)
class ShieldingConfig:
    """Parameter des ortsaufgelösten Dekohärenz-Feldes (Zonên-Modell).

    Zwei Zonen, radialsymmetrisch um einen Tubulin-Kollektiv-Kern:
      r ≤ r_core:   φ_free (geschützte Zone: Cytogel + Hydrationshülle)
      r >  r_core:  1.0 (Bulk-Cytosol)
    d_w_nm (Hydrationshüllen-Dicke) ist ANZEUGE-Parameter: sie schränkt
    plausibles Kern-Geometry ein, geht aber NICHT in Γ ein (registriert).
    """

    phi_free: float = PHI_FREE_FLOOR
    eps_res: float = EPS_RES_PESSIMISTIC
    delta_m_over_m: float = DELTA_M_ITER16
    r_core_nm: float = 8.0
    d_w_nm: float = 2.0
    lambda_debye_nm: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.phi_free <= 1.0:
            raise ValueError("phi_free in [0, 1]")
        if not 0.0 <= self.eps_res <= 1.0:
            raise ValueError("eps_res in [0, 1]")
        if self.delta_m_over_m <= 0.0:
            raise ValueError("delta_m_over_m > 0")
        if self.r_core_nm <= 0.0 or self.d_w_nm < 0.0:
            raise ValueError("r_core_nm > 0, d_w_nm >= 0")
        if self.lambda_debye_nm <= 0.0:
            raise ValueError("lambda_debye_nm > 0")


def phi_free_at(r_nm: float, cfg: ShieldingConfig) -> float:
    """Freier Wasseranteil an Ort r (Zwei-Zonen-Feld)."""
    return cfg.phi_free if r_nm <= cfg.r_core_nm else 1.0


def gamma_bulk_collision_per_s(or_cfg: ORConfig,
                               delta_m_over_m: float) -> float:
    """Γ_bulk = k_B·T·(Δm/m)²/ħ — exakte Inverse von tegmark_tau_dec_s(S=1).

    Unabhängige zweite Herleitung gegen orch_or.py (iter-19-Lektion:
    niemals die Registrierung gegen sich selbst prüfen).
    """
    if delta_m_over_m <= 0.0:
        raise ValueError("delta_m_over_m > 0")
    return KB * or_cfg.t_k * delta_m_over_m**2 / 1.054_571_817e-34


def gamma_collision_per_s(r_nm: float, cfg: ShieldingConfig,
                          or_cfg: ORConfig) -> float:
    """Γ_M(r) = Γ_bulk · (φ(r) + (1−φ(r))·ε_res) — Kollisions-Kanal.

    Freies Wasser dekohäriert mit Bulk-Rate; gebundenes Wasser nur mit
    ε_res·Bulk (registrierte Schranke, siehe Modul-Docstring).
    """
    phi = phi_free_at(r_nm, cfg)
    return gamma_bulk_collision_per_s(or_cfg, cfg.delta_m_over_m) * (
        phi + (1.0 - phi) * cfg.eps_res)


def gamma_needed_per_s(or_cfg: ORConfig) -> float:
    """Γ_need = 1/τ_OR — Kollaps muss VOR Umgebungs-Dekohärenz greifen."""
    return 1.0 / penrose_tau_or_s(or_cfg)


def mean_core_gamma_per_s(cfg: ShieldingConfig, or_cfg: ORConfig) -> float:
    """Volumengemittelte Kollisionsrate im geschützten Kern [0, r_core].

    Zwei-Zonen: konstant φ_free im Kern → Γ̄ = Γ_bulk·(φ_in + (1−φ_in)·ε).
    """
    phi = cfg.phi_free
    return gamma_bulk_collision_per_s(or_cfg, cfg.delta_m_over_m) * (
        phi + (1.0 - phi) * cfg.eps_res)


def effective_suppression(cfg: ShieldingConfig, or_cfg: ORConfig) -> float:
    """S_eff = Γ_bulk / Γ̄_core — das ABLEITBARE Schild (vs. S=1e6 HYPOTHESE)."""
    return gamma_bulk_collision_per_s(or_cfg, cfg.delta_m_over_m) \
        / mean_core_gamma_per_s(cfg, or_cfg)


def s_needed(or_cfg: ORConfig, delta_m_over_m: float) -> float:
    """Erforderliches Schild S_need = Γ_bulk/Γ_need = Γ_bulk·τ_OR."""
    return gamma_bulk_collision_per_s(or_cfg, delta_m_over_m) \
        / gamma_needed_per_s(or_cfg)


def required_phi_free(cfg: ShieldingConfig, or_cfg: ORConfig) -> float:
    """φ_in + (1−φ_in)·ε_res ≤ Γ_need/Γ_bulk → erforderliches φ_free.

    Negativ → Kern existiert sogar ohne Ausschluss (Bulk genügt).
    """
    frac = gamma_needed_per_s(or_cfg) / gamma_bulk_collision_per_s(
        or_cfg, cfg.delta_m_over_m)
    return frac - cfg.eps_res


def coherence_core_radius_nm(cfg: ShieldingConfig, or_cfg: ORConfig) -> float:
    """Größter Radius mit Γ(r) < Γ_need (Kohärenz-Kern, mt_quantum-Pattern).

    Zwei-Zonen: Kern existiert ⇔ Γ(0) < Γ_need → Radius = r_core, sonst 0.
    """
    if gamma_collision_per_s(0.0, cfg, or_cfg) < gamma_needed_per_s(or_cfg):
        return cfg.r_core_nm
    return 0.0


def corner_ratio(cfg: ShieldingConfig, or_cfg: ORConfig) -> float:
    """τ_OR/τ_dec_eff = Γ̄_core·τ_OR; < 1 → Gate ON (Überleben der Ecke)."""
    return mean_core_gamma_per_s(cfg, or_cfg) * penrose_tau_or_s(or_cfg)
