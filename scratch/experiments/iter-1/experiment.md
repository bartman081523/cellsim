# iter-1: EM-Schicht als Basis für Biophotonen

## Hypothese

Eine Zelle sendet Biophotonen im UV-Bereich (200-400 nm) aus, die
mit Nachbarzellen wechselwirken können. Aktuelle cellsim-Simulation
hat keine elektromagnetische Schicht — daher fehlt diese Kopplung.

Dieses Experiment baut eine minimale EM-Schicht (Maxwell-Gleichungen
im statischen Limit + Dipol-Strahlung) und prüft, ob eine JCVI-syn3A-
Zelle realistische Biophotonen-Intensitäten produziert.

## Method

1. **EM-Layer** mit gekoppelten Maxwell-Gleichungen in 1D (zylindrische
   Symmetrie der Zelle).
2. **Dipol-Quelle** im Cytoplasma: ATP-Hydrolyse erzeugt Dipolfluktuationen.
3. **Emissionsrate**: Schwarzkörper-Strahlung bei T=310 K ×
   zellulärer Extinktion + Popp-Faktor.
4. **Output**: Photonen-Fluss in 1 Zelle + Nachbar-Signalstärke.

## Result

*Wird automatisch durch iter_loop.py ausgewertet. Vorläufige Hypothese:
Bei 310 K ist Schwarzkörper-Strahlung vernachlässigbar im UV,
aber zelluläre Chemolumineszenz (Singulett-Sauerstoff, Lipid-Peroxidation)
kann messbare UV-Photonen erzeugen — Popp berichtet ~10² Photonen/cm²/s.*

## Strategic Vectors

- Wenn UV-Emission messbar: → iter-2 (Biophotonen-Synchronisation zwischen Zellen)
- Wenn nicht: → iter-1-retire (EM-Schicht nur als Maxwell-Hülle, nicht als Quelle)
