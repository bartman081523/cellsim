// CUDA-Skelett für RDME (Lattice-Microbes-Kompatibilitäts-Layer).
//
// LIMITATION 2: Lattice Microbes ist closed-source und nur als
// fertige Binaries verfügbar. Dieses Skelett ist die Vorlage für
// einen eigenen CUDA-Coupler, der das Lattice-Microbes-Lattice
// emuliert. Status: PLATZHALTER, kein ausführbarer Code.
//
// Erwartete Schnittstelle (kompatibel mit Luthey-Schulten-Lab-Konventionen):
//   - lattice_dim: 3D-Gitter-Dimension (nx, ny, nz)
//   - voxel_nm:    Voxel-Kantenlänge in nm (typisch 5–20 nm)
//   - dt_s:        Gillespie-Zeitschritt in Sekunden
//   - diffusion_nm2_per_s: Diffusionskoeffizient in nm²/s
//   - reactions:   Liste von (species_change, k, educt_species)
//   - volumes_a3:  Excluded-Volume pro Spezies in Å³
//
// CUDA-Kernel (Pseudocode):
//
// __global__ void gillespie_step(
//     int* voxel_counts,       // [n_voxels, n_species]
//     float* rates,            // [n_reactions]
//     int* stoch_matrix,       // [n_reactions, n_species]
//     float* d_local,          // [n_voxels] lokal variabler D
//     curandState* rng_state,  // [n_voxels] CUDA RNG
//     int n_voxels,
//     int n_reactions,
//     int n_species,
//     float dt_s,
//     float* out_particle_flux // [n_voxels]
// ) {
//     int voxel = blockIdx.x * blockDim.x + threadIdx.x;
//     if (voxel >= n_voxels) return;
//     // ... Gillespie-SSA-Logik pro Voxel ...
// }
//
// Für eine echte Implementation:
// 1. curandState initialisieren (curand_init mit Seed)
// 2. Reaktionsraten aus lokaler Konzentration berechnen
// 3. SSA-Wahl-Reaktion pro Voxel
// 4. Stochastische Diffusion via Metropolis-Hastings
// 5. Output: Partikel-Flux für RDME-Output
//
// Build-Anleitung (Platzhalter):
//   nvcc -O3 -arch=sm_80 -o rdme_cuda rdme_skeleton.cu -lcurand
//
// Performance-Erwartung (NVIDIA A100):
//   - 64³-Gitter: ~10⁶ Voxels × ~50 Spezies = 5·10⁷ Updates/s
//   - 105-min-Simulation: ~10⁸ Zeitschritte → ~5 h auf A100
//   - 60-s-Smoke auf 32³: ~10⁶ Schritte → ~3 s
//
// Aktueller Status: PLATZHALTER. Siehe LIMITATIONS.md §6.
//
// Verweise:
//   - Lattice Microbes: https://github.com/Luthey-Schulten-Lab/Minimal_Cell_4DWCM
//   - CUDA curand: https://docs.nvidia.com/cuda/curand/
//   - Gillespie-SSA auf GPU: https://arxiv.org/abs/1109.6633

#include <stdio.h>

// Vorlage — wird im cellsim-Projekt NICHT kompiliert.
// Realer Build würde nvcc + curand linking erfordern.

__global__ void placeholder_kernel() {
    // TODO: Implement RDME-SSA
    printf("rdme_cuda: PLACEHOLDER — siehe LIMITATIONS.md §6\n");
}
