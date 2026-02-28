# 🍞 BreadScan — Bread Crumb Porosity Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-4.0-gold)](CHANGELOG.md)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)]()
[![Browser-based](https://img.shields.io/badge/runs%20in-browser-blue)]()

> **A literature-grounded, browser-based digital image analysis (DIA) tool for quantifying bread crumb porosity and generating digital texture fingerprints. Designed specifically for research on fiber-enriched breads (BSG, whole-wheat, gluten-free), where conventional global thresholding methods fail.**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Scientific Background](#scientific-background)
- [Features](#features)
- [Quick Start](#quick-start)
- [How to Use](#how-to-use)
- [Parameters Reference](#parameters-reference)
- [Output Metrics](#output-metrics)
- [Methodology](#methodology)
- [Limitations](#limitations)
- [Literature References](#literature-references)
- [Suggested Citation](#suggested-citation)
- [License](#license)

---

## Overview

BreadScan is a **single-file, zero-dependency** web application for measuring bread crumb porosity through digital image analysis. It runs entirely in the browser — no server, no installation, no Python environment required.

The tool was developed to address a specific gap in existing DIA workflows: **most published tools assume white bread with a bimodal grayscale histogram** (dark pores against a pale crumb). This assumption breaks down for **brewer's spent grain (BSG)-enriched, whole-wheat, or other dark/fiber-enriched breads**, where the warm-brown crumb color produces false positives when global Otsu thresholding is applied.

BreadScan v4 implements **two distinct thresholding algorithms**, selected automatically based on bread type:

| Bread type | Algorithm | Literature source |
|---|---|---|
| White / control wheat bread | **Otsu** (global, minimizes intra-class variance) | Gonzales-Barron & Butler (2006) |
| BSG / dark / fiber-enriched bread | **HisAnalysis peak-mode** (threshold = histogram peak + offset) | Bosakova-Ardenska (2015) |

---

## Scientific Background

Bread crumb is a cellular foam structure. Its porosity — the fraction of cross-sectional area occupied by gas cells — is one of the primary structural determinants of sensory quality. A well-developed porous crumb contains fine, thin-walled, uniformly sized cells that yield a softer and more elastic texture ([Pyler, 1988](#literature-references); [Lassoued et al., 2008](#literature-references)).

Digital Image Analysis (DIA) of bread crumb cross-sections has been established as a valid, objective, and non-destructive alternative to physicochemical porosity measurement. Published work has demonstrated:

- **~80% accuracy** in predicting crumb density from image-derived parameters including void fraction and cell wall thickness ([Zghal et al., 1999](#literature-references))
- Strong correlations between DIA-derived void fraction and TPA (Texture Profile Analysis) firmness ([Esteller et al., 2006](#literature-references))
- Validated sensory correlations for crumb fineness and homogeneity ([Gonzales-Barron & Butler, 2008](#literature-references); [Lassoued et al., 2008](#literature-references))

BreadScan also outputs a **Digital Texture Fingerprint** — a multi-parameter structural profile inspired by the "digital texture-fingerprints" concept of [Ruderman et al. (2025)](#literature-references) — that enables formulation comparison, baking process monitoring, and quality benchmarking.

---

## Features

- 🔬 **Two literature-validated thresholding algorithms** for white and dark/BSG bread
- 📊 **Digital Texture Fingerprint** — 6 structural parameters per sample
- 🎨 **Colormap visualization** of pore size distribution (blue → red by area)
- 📈 **Intensity histogram view** showing threshold placement on the actual image data
- 📦 **Zero dependencies** — pure HTML + JavaScript, runs in any modern browser
- 🖱️ **Drag-and-drop** image upload
- 🔧 **Fully adjustable parameters** with real-time tuning
- 📝 **Analysis log** with per-step pixel counts for reproducibility

---

## Quick Start

**Option 1 — Use directly from GitHub Pages:**
```
https://<your-username>.github.io/breadscan/bread_porosity_analyzer_v4.html
```

**Option 2 — Clone and open locally:**
```bash
git clone https://github.com/<your-username>/breadscan.git
cd breadscan
open bread_porosity_analyzer_v4.html   # macOS
# or double-click the file in your file explorer
```

No build step. No `npm install`. No server. Just open the HTML file.

---

## How to Use

### 1. Prepare your image
- **Recommended:** flatbed scan of a crumb cross-section at 200–300 DPI
  - Flatbed scanning provides uniform, diffuse illumination independent of external light conditions, which is critical for consistent thresholding ([Gonzales-Barron & Butler, 2006](#literature-references))
- **Acceptable:** digital photograph under diffuse, uniform lighting (avoid flash)
- **Crop to crumb only** — remove crust edges before uploading, as crust pixels skew the histogram and bias the threshold

### 2. Select bread type
- **Control / White** → Otsu algorithm
- **BSG / Dark** → HisAnalysis peak-mode algorithm

### 3. Adjust preprocessing (optional)
- `Gaussian σ`: smoothing before thresholding. Higher = smoother binary mask, fewer noise pixels
- `CLAHE clip`: local contrast enhancement. Increase for dark/flat-histogram images

### 4. For BSG bread: adjust Peak Offset
- The histogram view (5th panel) shows where the threshold is placed on the intensity distribution
- The vertical **amber line** = histogram peak (dominant crumb color)
- The vertical **gold line** = actual threshold = peak + offset
- A positive offset (e.g. +5 to +15%) means: only detect pixels significantly darker than the crumb peak
- Adjust until the binary view (3rd panel) shows pores highlighted without BSG fiber noise

### 5. Adjust size filter
- `Min cell area`: remove noise pixels and single-pixel detections
- `Max cell area`: remove large background artifacts

### 6. Press Analyze
Results appear in the metrics bar, fingerprint panel, colormap view, and analysis log.

---

## Parameters Reference

| Parameter | Default | Range | Notes |
|---|---|---|---|
| Gaussian σ | 1.0 | 0–3.0 | Pre-thresholding denoising |
| CLAHE clip | 2.0 | 0.5–5.0 | Local contrast enhancement before thresholding |
| Peak offset (BSG only) | +5% | −20% to +30% | Threshold offset from histogram peak; positive = stricter (darker pores only) |
| Min cell area | 20 px² | 5–300 | Minimum blob size to count as a pore |
| Max cell area | 15000 px² | 500–40000 | Maximum blob size; set lower to exclude large artifacts |
| 3D correction factor | 1.50 | 1.0–3.0 | Multiplier to estimate 3D volumetric porosity from 2D optical measurement |

> **On the 3D correction factor:** 2D DIA systematically underestimates true 3D porosity. X-ray microtomography studies report volumetric porosities of 60–80% for white wheat bread. A factor of 1.5 is a conservative estimate; adjust based on published values for your specific bread type.

---

## Output Metrics

### Metrics Bar

| Metric | Definition | Literature term |
|---|---|---|
| **Void Fraction** | % of analyzed area classified as pores | `VF`, `porosity %` — Zghal et al. (1999) |
| **3D Corrected** | Void fraction × correction factor | Estimated volumetric porosity |
| **Cell Count** | Number of valid pore regions after size filter | `cell count` — Gonzales-Barron & Butler (2006) |
| **Cell Density** | Cells per 100 px² of analyzed area | `crumb fineness` — Zghal et al. (1999) |
| **Mean Cell Area** | Mean area of valid pores in px² | `mean cell area` — Gonzales-Barron & Butler (2006) |
| **Uniformity** | 1 − CV of cell areas (1 = perfectly uniform) | `cell uniformity` — Gonzales-Barron & Butler (2006) |

### Digital Texture Fingerprint

Six structural descriptors presented as a normalized profile:

| Parameter | Description | Related sensory attribute |
|---|---|---|
| Void Fraction | % pore area | Lightness, softness |
| Cell Density | Cells per 100px² | Crumb fineness, silkiness |
| Mean Cell Area | Average pore size | Coarseness |
| Cell Uniformity | 1 − coefficient of variation | Homogeneity, consistency |
| Wall Thickness | √(solid area / cell count), estimated | Structural integrity |
| Macro Pore % | % area in pores > 2000 px² | Open crumb character |

### Canvas Views

| View | Description |
|---|---|
| **Original** | Uploaded image (resized to max 650px) |
| **CLAHE Enhanced** | Contrast-enhanced grayscale used for thresholding |
| **Binary Mask** | Thresholded image — gold pixels = detected pores |
| **Colormap by area** | Pore size map: blue (micro) → green → yellow → red (macro) |
| **Histogram + threshold** | Intensity histogram of enhanced image; gold line = threshold, amber line = histogram peak |

---

## Methodology

### Pipeline

```
Input image
    ↓
Grayscale (0.299R + 0.587G + 0.114B)
    ↓
Gaussian blur (σ configurable)
    ↓
CLAHE (Contrast Limited Adaptive Histogram Equalization, tile=32px)
    ↓
    ├── White bread → Otsu global threshold
    └── BSG/dark bread → HisAnalysis peak-mode threshold
    ↓
Morphological closing (dilate r=1 → erode r=1)   [fills micro-gaps in pore edges]
    ↓
Connected components labeling (BFS flood-fill)
    ↓
Size filter (min/max area)
    ↓
Metrics + Fingerprint + Visualization
```

### Thresholding Algorithms

**Otsu (white bread):**  
Finds the gray level that maximizes inter-class variance between "pore" and "crumb" pixel classes. Performs best when the intensity histogram is bimodal — which is the case for white bread (dark pores, pale crumb matrix). Validated as the top-performing global method for bread DIA by [Gonzales-Barron & Butler (2006)](#literature-references).

**HisAnalysis peak-mode (BSG / dark bread):**  
Identifies the intensity bin with the highest frequency in the enhanced grayscale histogram (the dominant crumb color). Sets the threshold at `peak_bin + offset`. Pixels darker than this threshold are classified as pores. This approach was validated specifically for brown bread by [Bosakova-Ardenska (2015)](#literature-references), achieving a correlation coefficient of r = 0.93 against physicochemical porosity measurements.

**Why not adaptive thresholding?**  
Adaptive thresholding (local mean) was tested in earlier versions but produced inconsistent results when imaging conditions varied (photographic hotspots, uneven lighting). Global methods with a physically-grounded threshold selection criterion — Otsu or peak-mode — yield more reproducible results across sessions, which is critical for comparative studies across bread formulations.

### Important note on results

Results from photographic images should be interpreted as **relative comparisons** across formulations under identical imaging conditions, not as absolute porosity values. The gold standard for bread DIA remains flatbed scanning under controlled, diffuse illumination ([Gonzales-Barron & Butler, 2006](#literature-references); [Zghal et al., 1999](#literature-references)).

---

## Limitations

1. **Photography vs. scanning:** Camera images with directional or flash lighting create intensity hotspots inside pores, causing them to be missed. This systematically underestimates porosity. Flatbed scanning at 200+ DPI is strongly recommended for thesis/publication work.

2. **2D measurement:** DIA measures a 2D cross-section; true 3D volumetric porosity (accessible via X-ray microtomography) is higher. The 3D correction factor is an approximation.

3. **BSG brown bread:** Even with HisAnalysis peak-mode, BSG particles and fiber shadows that are darker than the crumb peak may be classified as pores. Visual inspection of the binary mask is always recommended.

4. **Image resolution:** The tool resizes images to max 650px for performance. For publication, consider running ImageJ with the same algorithm parameters on full-resolution images.

5. **No crust exclusion:** Results are skewed if crust is included. Always crop to crumb-only ROI before uploading.

---

## Literature References

The algorithms and metrics in BreadScan are directly grounded in the following peer-reviewed literature:

- **Gonzales-Barron, U. & Butler, F. (2006).** A comparison of seven thresholding techniques with the k-means clustering algorithm for measurement of bread-crumb features by digital image analysis. *Journal of Food Engineering*, 74(2), 268–278. https://doi.org/10.1016/j.jfoodeng.2005.03.007

- **Gonzales-Barron, U. & Butler, F. (2008).** Fractal texture analysis of bread crumb digital images. *European Food Research and Technology*, 226(4), 721–729.

- **Zghal, M.C., Scanlon, M.G. & Sapirstein, H.D. (1999).** Prediction of bread crumb density by digital image analysis. *Cereal Chemistry*, 76(5), 734–742.

- **Lassoued, N., Delarue, J., Launay, B. & Michon, C. (2008).** Baked product texture: Correlations between instrumental and sensory characterization using Flash Profile. *Journal of Cereal Science*, 48(1), 133–143. https://doi.org/10.1016/j.jcs.2007.08.014

- **Bosakova-Ardenska, A., Danev, A., Andreeva, H. & Gogova, T. (2015).** Application of thresholding algorithms for brown bread porosity evaluation. *International Journal of Food Science and Applied Biotechnology*.

- **Ruderman, G., Bretherton, I. & colleagues (2025).** Digital image analysis to assess the texture of bread products. *ScienceDirect / Food Science*. https://doi.org/10.1016/j.crfs.2025.100007 *(Bread Texture Analyser — digital texture fingerprint concept)*

- **Esteller, M.S., Zancanaro, O., Palmeira, C.N.S. & da Silva Lannes, S.C. (2006).** The effect of kefir addition on microstructure parameters and physical properties of porous white bread. *European Food Research and Technology*, 222(1–2), 26–31.

- **Pyler, E.J. (1988).** *Baking Science and Technology* (3rd ed.). Sosland Publishing.

---

## Suggested Citation

If you use BreadScan in academic work, please cite as:

```
[Your Name] (2025). BreadScan: A Browser-Based Digital Image Analysis Tool 
for Bread Crumb Porosity. GitHub. 
https://github.com/<your-username>/breadscan
```

And cite the underlying algorithmic literature as appropriate (see [Literature References](#literature-references)).

---

## Repository Structure

```
breadscan/
├── bread_porosity_analyzer_v4.html   ← Main application (self-contained)
├── README.md                         ← This file
├── CHANGELOG.md                      ← Version history
├── LICENSE                           ← MIT License
└── examples/
    ├── white_bread_example.jpg       ← Sample white bread cross-section
    └── bsg_bread_example.jpg         ← Sample BSG bread cross-section
```

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

Free to use, modify, and distribute for academic and commercial purposes with attribution.
