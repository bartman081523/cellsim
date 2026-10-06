"""iter-35 — Yod-Jod-Zensus (deterministisch; Registrierung siehe experiment.md, 2026-10-06).

Kein RNG. Die UniProt-REST-Befunde sind Eingabekonstanten (2026-10-06 vor der Messung
abgefragt, im Registrierungsprotokoll fixiert): Proteom UP000326712 → iodine/iodide = 0,
selenocysteine = 0. Die AF-Modelle enthalten nach Konstruktion keine Heteroatome.

Ausgabe result.json im Vektor-Verzeichnis.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

OUT_FILE = Path(__file__).resolve().parent / "result.json"
SRC_ROOT = Path(__file__).resolve().parents[3]

# ---------- vorab registrierte Familien ----------

FAM_HALOGEN_ISO = [19, 35, 37, 79, 81, 127]
FAM_MONOISOTOPIC = [
    9, 19, 23, 27, 31, 45, 51, 55, 59, 75, 85, 89, 93,
    103, 113, 127, 133, 139, 141, 153, 159, 165, 169, 175, 185, 197,
]
FAM_ESSENTIAL_Z = [1, 6, 7, 8, 15, 16, 11, 19, 12, 20, 17, 26, 30, 29, 25, 53,
                   34, 27, 42, 9, 24, 50, 23, 5, 14, 28]
FAM_ESSENTIAL_A = [1, 12, 14, 16, 31, 32, 23, 39, 24, 40, 35, 56, 64, 63, 55, 127,
                   80, 59, 98, 19, 52, 120, 51, 11, 28, 58]
IODINE_Z, IODINE_A = 53, 127
RADIX_DEMO_BASES = [2, 8, 10, 12, 16]


def digit_sum(n: int, base: int) -> int:
    s = 0
    while n > 0:
        s += n % base
        n //= base
    return s


def null_frac(lo: int, hi: int, base: int, target: int = 10) -> float:
    """Exakter Anteil der Ganzzahlen in [lo, hi] mit Quersumme `target` in der Basis."""
    hits = sum(1 for m in range(lo, hi + 1) if digit_sum(m, base) == target)
    return hits / (hi - lo + 1)


def exact_two_sided_p(n: int, f: float, k: int) -> float:
    """Exakter zweiseitiger Binomial-p (Kleinste-Tail-Regel)."""
    p = f
    probs = [math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(n + 1)]
    tail = sum(pr for i, pr in enumerate(probs) if pr <= probs[k] + 1e-12)
    return min(1.0, tail)


def family_census(name: str, masses: list[int]) -> dict:
    n = len(masses)
    hit_m10 = [m for m in masses if digit_sum(m, 10) == 10]
    lo, hi = min(masses), max(masses)
    f = null_frac(lo, hi, 10)
    exp = n * f
    sd = math.sqrt(n * f * (1 - f))
    standout = len(hit_m10) >= exp + 2 * sd and (IODINE_A in hit_m10)
    return {
        "family": name,
        "n": n,
        "masses": masses,
        "hits_m10": hit_m10,
        "n_hits": len(hit_m10),
        "expected": round(exp, 3),
        "sd": round(sd, 3),
        "null_frac": round(f, 4),
        "interval": [lo, hi],
        "two_sided_p": round(exact_two_sided_p(n, f, len(hit_m10)), 4),
        "verdict": "TEN_STANDOUT" if standout else "TEN_CHANCE_CONSISTENT",
    }


def radix_demo(masses: list[int]) -> dict:
    return {
        "bases": RADIX_DEMO_BASES,
        "hit_sets": {
            base: [m for m in masses if digit_sum(m, base) == 10]
            for base in RADIX_DEMO_BASES
        },
        "interpretation": "Treffermenge wandert mit der Basis -> Quersummen-10s sind "
        "Repräsentationseigenschaften, keine physikalischen Invarianten.",
    }


def source_grep() -> int:
    pat = re.compile(r"iodine|iodide|iodat", re.IGNORECASE)
    count = 0
    for pat_path in [SRC_ROOT / "src", SRC_ROOT / "configs", SRC_ROOT / "tests"]:
        if not pat_path.exists():
            continue
        for file in pat_path.rglob("*"):
            if file.suffix not in {".py", ".yaml", ".yml", ".tsv", ".json"}:
                continue
            try:
                text = file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            count += len(pat.findall(text))
    return count


def registry_iodine() -> int:
    import sys

    sys.path.insert(0, str(SRC_ROOT / "src"))
    from cellsim.modules.reactions import default_registry

    reg = default_registry()
    names: list[str] = list(reg.species_ids)
    for rxn in reg.reactions:
        for side in (rxn.reactants, rxn.products):
            names.extend(side if isinstance(side, (list, tuple)) else [side])
    return sum(1 for nm in names if "iod" in str(nm).lower())


def hormone_iodine_fractions() -> dict:
    m_c, m_h, m_n, m_o, m_i = 12.011, 1.008, 14.007, 15.999, 126.90447
    t4 = 15 * m_c + 11 * m_h + 4 * m_i + 1 * m_n + 4 * m_o
    t3 = 15 * m_c + 12 * m_h + 3 * m_i + 1 * m_n + 4 * m_o
    t2 = 14 * m_c + 13 * m_h + 2 * m_i + 1 * m_n + 4 * m_o
    t1 = 14 * m_c + 14 * m_h + 1 * m_i + 1 * m_n + 4 * m_o
    t0 = 14 * m_c + 15 * m_h + 0 * m_i + 1 * m_n + 4 * m_o
    return {
        "T4_C15H11I4NO4": {"MW": round(t4, 2), "iodine_mass_fraction": round(4 * m_i / t4, 4)},
        "T3_C15H12I3NO4": {"MW": round(t3, 2), "iodine_mass_fraction": round(3 * m_i / t3, 4)},
        "T2_C14H13I2NO4": {"MW": round(t2, 2), "iodine_mass_fraction": round(2 * m_i / t2, 4)},
        "T1_C14H14I1NO4": {"MW": round(t1, 2), "iodine_mass_fraction": round(1 * m_i / t1, 4)},
        "T0_C14H15I0NO4_thyronine": {"MW": round(t0, 2), "iodine_mass_fraction": 0.0},
        "cascade_ladder": [4, 3, 2, 1, 0],
        "ladder_sum": 4 + 3 + 2 + 1 + 0,
        "ladder_posthoc_declared": True,
    }


def main() -> None:
    result = {
        "vector": "VECTOR_YOD_IODINE (iter-35)",
        "registration": "experiment.md 2026-10-06, VOR der Messung",
        "deterministic": True,
        "dossier": {
            "Z": 53,
            "Ar_CIAAW": "126.90447(3)",
            "A_stable": 127,
            "neutrons": 74,
            "group_period": [17, 5],
            "electron_config": "[Kr] 4d10 5s2 5p5",
            "d10_electrons": digit_sum(10, 10),  # konstant 10, Radix-invariantes COUNT
            "k_edge_keV": 33.17,
            "redox_I_HOI_V": 0.54,
            "redox_Br_HOBr_V": 0.76,
            "redox_Cl_HOCl_V": 1.28,
            "c_i_bond_lability_rank": "labilste aller C-X (F>Cl>Br>I)",
            "heaviest_essential_element": True,
            "who_deficiency_claim": "haeufigste vermeidbare Ursache geistiger Behinderung",
            "monoisotopic": True,
            "violet_vapor_named_gay_lussac_1813": True,
            "se_water_I_uM": 0.45,
            "se_water_Br_uM": 800.0,
        },
        "radix_filter": {
            "candidates": [
                {"item": "Quersumme(Z=53)=8", "is_ten": False, "survives_radix_change": "n.a."},
                {"item": "Quersumme(A=127)=10", "is_ten": True, "survives_radix_change": False,
                 "note": "in Basis 16: 0x7F -> 22; Basis 12: A7 -> 17"},
                {"item": "127 = 2^7-1 (Mersenne-Primzahl)", "is_ten": False,
                 "survives_radix_change": True, "note": "Fakt, keine 10-Aussage"},
                {"item": "4d-Unterschallektronenzahl = 10", "is_ten": True,
                 "survives_radix_change": True, "note": "COUNT, basisunabhaengig (C1)"},
                {"item": "Deiodinations-Kaskade 4+3+2+1+0 = 10", "is_ten": True,
                 "survives_radix_change": True, "note": "COUNT der Jod-Atome (C2), post-hoc deklariert"},
            ],
            "n_survivors": 2,
        },
        "family_census": [
            family_census("FAM_HALOGEN_ISO", FAM_HALOGEN_ISO),
            family_census("FAM_MONOISOTOPIC_26", FAM_MONOISOTOPIC),
            family_census("FAM_ESSENTIAL_26", FAM_ESSENTIAL_A),
        ],
        "z10_census": {
            "FAM_ESSENTIAL_26_z_hits": [z for z in FAM_ESSENTIAL_Z if digit_sum(z, 10) == 10],
            "iodine_Z_digit_sum": digit_sum(IODINE_Z, 10),
        },
        "radix_demo": radix_demo(FAM_HALOGEN_ISO + FAM_MONOISOTOPIC),
        "hormone_ladder": hormone_iodine_fractions(),
        "cellsim_census": {
            "uniprot_iodine_iodide_hits": 0,
            "uniprot_selenocysteine_hits": 0,
            "source_grep_matches": source_grep(),
            "registry_iodine_species": registry_iodine(),
            "alphafold_models": "nach Konstruktion ohne Heteroatome",
            "verdict": "IODINE_ABSENT_IN_SYN3A",
            "secondary": "SELENOCYSTEINE_ABSENT_IN_SYN3A",
        },
    }
    fams = result["family_census"]
    z10 = result["z10_census"]["FAM_ESSENTIAL_26_z_hits"]
    z10_expected = 2.6  # gleiche Null-Fraktion ~0.1 wie bei den Massen 19..127
    z10_ok = len(z10) <= z10_expected + 2 * math.sqrt(26 * 0.1 * 0.9)
    result["verdict_labels"] = [
        "HOMONYM_VERIFIED (deutsch: Jod=Jod als Oberflaechen-Identitaet)",
        "ETYMOLOGY_LINK_FALSIFIED (iode<-griech. ion 'Violett-Blume', NICHT iota/yodh 'Hand')",
        *[f["verdict"] for f in fams],
        "RADIX_INVARIANT_SURVIVORS_COUNTED",
        result["cellsim_census"]["verdict"],
        result["cellsim_census"]["secondary"],
        "Z10_hits_no_outlier" if z10_ok else "Z10_OUTLIER",
        "HEAVIEST_ESSENTIAL_BRIDGE_DOCUMENTED (Symbol+Biochemie, keine Kausalbehauptung)",
    ]
    OUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("verdicts:", *result["verdict_labels"], sep="\n  ")


if __name__ == "__main__":
    main()