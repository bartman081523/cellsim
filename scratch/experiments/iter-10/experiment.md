# iter-10: Ruliad-Emergenz-Metriken auf dem RDME

## Hypothese

Origin_Ruliad (Wolfram-Ruliad-Framework) misst Emergenz über
Mutual Information (MI) und Lempel-Ziv-Komplexität (LZ) auf binären
Feldern. Unsere RDME-Voxel-Felder sind solche Felder.

**Vorhersage**: Der RDME mit Reaktionen erzeugt nicht-triviale
computationale Struktur:
- MI zwischen aufeinanderfolgenden Voxel-Zuständen > 0.1 (Struktur
  persistiert — "causal fixed points" im Ruliad-Sinn)
- LZ-Komplexität steigt mit der Zeit (computational richness)
- Kontrolle: ein reines Diffusions-RDME ohne Reaktionen hat
  signifikant niedrigere MI (Struktur zerfällt)

## Method

1. **Portierung aus Origin_Ruliad** (Emergence_Phase_6.py, mit
   Attribuierung): `binarize` (Quantil), `mutual_information_binary`,
   `lz_complexity_binary`.
2. **RDME-Läufe**: (a) mit vollem Reaktions-Registry (21 Reaktionen),
   (b) Kontroll-Lauf mit k=0 für alle Reaktionen (nur Diffusion).
3. **Metriken pro Zeitschritt**:
   - Temporale MI: MI(Voxel(t), Voxel(t+1)) für die dominante Spezies
   - LZ-Komplexität des binarisierten Feldes
   - Raumliche MI: MI zwischen benachbarten Voxeln (Kohärenz-Länge)
4. **Signal**: STRONG wenn (MI_reaktiv > MI_diffusiv + 0.05) UND
   MI_reaktiv > 0.1; NULL wenn beide ≈ 0; CONTRADICTION wenn Diffusion
   mehr Struktur zeigt als Reaktion.

## Quellen (konsultiert)

- `/run/media/julian/ML2/Python/Origin_Ruliad/` (Ruliad-Framework,
  Emergenz-Metriken, UPE-Konzept) — **primäre Quelle laut User**
- `/run/media/julian/ML2/Python/MT_Sim/` (Info: LZ/MI als Konvention)
- `/run/media/julian/ML2/Python/upe_ruliad/` (Info: UPE-Thesis-Papers)
- Origin_Ruliad/Genesis.md: UVC 232 nm → UV-getriebene Präbiotik
  (Sutherland 2015) — verbindet an unsere EM-Schicht