# BreadScan — Bread Crumb Porosity Analyzer

[![Launch BreadScan](https://img.shields.io/badge/Launch_BreadScan-Open_App-c9a84c?style=for-the-badge)](https://luciabuzzeo.github.io/Bread_porosity_scan/bread_porosity_analyzer.html)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Browser-based](https://img.shields.io/badge/runs%20in-browser-blue)]()

> A browser-based digital image analysis (DIA) tool for objective characterization of bread crumb structure. BreadScan quantifies void fraction, gas-cell density, mean cell area, cell-size uniformity, wall thickness and macro-pore fraction from a transverse cross-section of the loaf, and outputs a **Digital Texture Fingerprint** suitable for comparing formulations. The tool implements two thresholding pathways validated in the cereal-science literature, selected according to crumb colour, so that fibre-enriched and dark crumbs (BSG, whole-wheat, multigrain) are not biased by global thresholding designed for white bread.

---

## Contents

- [Overview](#overview)
- [Output Metrics](#output-metrics)
- [How to Use](#how-to-use)
- [Parameters Reference](#parameters-reference)
- [Methodology](#methodology)
- [Limitations](#limitations)
- [Scientific Background and Validation](#scientific-background-and-validation)
- [References](#references)
- [Suggested Citation](#suggested-citation)
- [License](#license)

---

## Overview

Bread crumb is a cellular foam: its porosity, gas-cell size distribution, and wall structure determine specific volume, softness, elasticity, and the perceived sensory quality of the loaf. BreadScan provides an objective, reproducible, and non-destructive measurement of these morphological descriptors directly from a digital image of the crumb cross-section.

The tool runs entirely in the browser — no installation is required. It applies one of two thresholding algorithms automatically, depending on whether the operator selects a **white/control** crumb or a **BSG/dark** crumb:

| Crumb type | Algorithm | Source |
|---|---|---|
| White / control wheat | Sauvola local adaptive thresholding on CLAHE-enhanced grayscale | Sauvola & Pietikäinen (2000) |
| BSG / dark / fibre-enriched | HisAnalysis peak-mode threshold on raw grayscale | Bosakova-Ardenska et al. (2015) |

A spatial calibration step (using a ruler or coin in the image) converts pixel measurements to physical units (mm, mm², cells/cm²), which is essential for inter-sample and inter-laboratory comparability.

---

## Output Metrics

After analysis, BreadScan reports the following descriptors of crumb structure. When the image is spatially calibrated, areas are returned in mm² and cell density in cells/cm²; otherwise units are pixel-based.

### Primary metrics

| Metric | Definition | Cereal-science term |
|---|---|---|
| **Void fraction** | Fraction of analysed crumb area classified as gas cells | 2D porosity (Zghal et al., 1999) |
| **3D-corrected porosity** | Void fraction × volumetric correction factor (default 1.50) | Estimated volumetric porosity |
| **Cell count** | Number of valid gas cells after size filtering | Cell count (Gonzales-Barron & Butler, 2006) |
| **Cell density** | Cells per cm² (calibrated) or cells / 100 px² (uncalibrated) | Crumb fineness (Zghal et al., 1999) |
| **Mean cell area** | Mean projected area of valid gas cells, in mm² or px² | Mean cell area |
| **Cell uniformity** | 1 − coefficient of variation of cell areas (1 = perfectly uniform) | Crumb homogeneity |

### Digital Texture Fingerprint

A six-parameter morphological profile, presented in normalized form for direct comparison across formulations (after Ruderman et al., 2025):

| Parameter | Description | Sensory correlate |
|---|---|---|
| Void fraction | Fraction of crumb area occupied by gas cells | Lightness, softness |
| Cell density | Spatial frequency of cells | Crumb fineness, silkiness |
| Mean cell area | Average gas-cell projected area | Coarseness |
| Cell uniformity | 1 − CV of cell areas | Homogeneity |
| Wall thickness | √(solid crumb area / cell count) | Structural integrity |
| Macro-pore fraction | Fraction of crumb area in cells > 2000 px² | Open-crumb character |

### Visual outputs

| Panel | Description |
|---|---|
| Original | Uploaded image, optionally cropped to the selected ROI |
| CLAHE-enhanced | Local-contrast-enhanced grayscale (input to Sauvola in white mode; visualization only in BSG mode) |
| Binary mask | Segmented gas cells (gold pixels) after thresholding and morphological closing |
| Colormap by area | Cell-size map: blue (micro) → green → yellow → red (macro) |
| Histogram + threshold | Intensity histogram with threshold and crumb-peak markers |
| Cell-size distribution | Discretised gas-cell distribution: micro / small / medium / large / macro |

---

## How to Use

### 1. Sample preparation and image acquisition

Slice the loaf transversely with a sharp serrated knife and image the crumb face under uniform, diffuse illumination. A flatbed scanner at 200–300 dpi is the gold standard ([Gonzales-Barron & Butler, 2006](#references)); a smartphone photograph in diffuse light without flash is acceptable for relative comparison across formulations imaged under identical conditions.

**Always include a spatial reference in the frame**: a ruler placed alongside the slice is strongly preferred. A coin is acceptable when no ruler is available, but provides only a single reference distance.

### 2. Upload the image

Drop the file onto the upload area or click to select it. A calibration dialog opens with three options:

- **Calibrate with ruler** *(recommended)*
- **Calibrate with coin** *(alternative)*
- **Crumb only** *(no spatial calibration; results in pixel units)*

### 3. Spatial calibration with a ruler

This is the recommended workflow. The dialog displays the uploaded image; you tap two points along the ruler and declare the real distance between them.

1. **Tap the first point** at a known mark on the ruler (e.g. the 0 mm line). The point appears as a pulsing marker labelled *Confirm?*.
2. Press **Confirm point** to lock the point in. If the placement was inaccurate, press **Redo** and tap again.
3. **Tap the second point** at a second known mark (e.g. the 50 mm line) and press **Confirm point** again.
4. Enter the **distance in mm** between the two points (the field defaults to 50 mm; adjust to match the marks you selected).
5. The tool computes and displays the scale factor (px/mm) and proceeds to the ROI step.

> *Place the two points as far apart as the ruler allows. A longer reference line reduces the relative error introduced by tap precision and gives a more accurate scale factor.*

### 4. Spatial calibration with a coin

Same two-tap workflow as the ruler, but tap two **opposite edges of the coin** (across its diameter), then select the coin from the drop-down. Built-in references: 1 €, 2 €, 50 ¢, 10 ¢, US Quarter, US Nickel, UK £1.

### 5. Define the region of interest (ROI)

After calibration, drag a rectangle over the crumb area, **excluding the crust**, and press **Confirm ROI**. Crust pixels skew the intensity histogram and bias the threshold, so cropping is important. Use **Redo ROI** to redraw, or **Skip — use full image** if no cropping is needed. The ROI dimensions are shown in mm.

### 6. Select the bread type

Choose **Control / White** (Sauvola adaptive thresholding) or **BSG / Dark** (HisAnalysis peak-mode). Default preprocessing and segmentation parameters auto-switch with the selection.

### 7. Run the analysis

Press **Analyze — Generate Fingerprint**. The metrics bar, fingerprint panel, image panels, cell-size distribution and analysis log are populated.

<sub>**Optional — preprocessing fine-tuning.** Defaults are set per crumb type and are appropriate for most images. If the binary mask shows under- or over-segmentation, consult the *Parameters Reference* below: increase Gaussian σ to suppress fibre noise; lower the BSG peak offset to detect more cells; raise the minimum cell area to remove single-pixel artefacts; raise CLAHE clip on flat-histogram images. Visual inspection of the binary mask is recommended in all cases.</sub>

---

## Parameters Reference

| Parameter | White default | BSG default | Range | Function |
|---|---|---|---|---|
| Gaussian σ | 1.0 | 2.0 | 0.0 – 3.0 | Pre-thresholding denoising; higher values smooth fibre texture in BSG crumbs |
| CLAHE clip | 2.0 | 2.0 | 0.5 – 5.0 | Local-contrast enhancement; used as input to Sauvola in white mode, visualization only in BSG mode |
| Peak offset | n/a | −8 % | −20 % to +30 % | BSG mode only: threshold offset from histogram peak. More negative = stricter (only the darkest pixels are classified as cells) |
| Min cell area | 20 px² | 10 px² | 5 – 300 | Minimum area for a detected blob to be counted as a gas cell |
| Max cell area | 15 000 px² | 15 000 px² | 500 – 40 000 | Upper size cut-off; rejects large background artefacts |
| 3D correction | 1.50 | 1.50 | 1.0 – 3.0 | Multiplier applied to 2D void fraction to estimate volumetric porosity |

> **On the 3D correction factor.** 2D image analysis systematically underestimates true volumetric porosity. X-ray microtomography studies report 60–80 % volumetric porosity in white wheat bread; a multiplier of 1.5 is a conservative default. Adjust based on published values for the specific bread system under study.

---

## Methodology

### Pipeline

```
Input image
    │
    ▼
Spatial calibration (ruler or coin) → px/mm factor
    │
    ▼
Region-of-interest (ROI) selection — crust excluded
    │
    ▼
Grayscale conversion (0.299R + 0.587G + 0.114B)
    │
    ▼
Gaussian blur (σ = 1.0 white, 2.0 BSG)
    │
    ├── White / control crumb:
    │     CLAHE (32 px tile) → Sauvola (window 51 px, k = 0.2)
    │
    └── BSG / dark crumb:
          HisAnalysis peak-mode on blurred grayscale (no CLAHE)
    │
    ▼
Morphological closing (r = 1 white, r = 3 BSG)
    │
    ▼
Connected-component labelling (8-connectivity)
    │
    ▼
Size filtering (min / max cell area)
    │
    ▼
Metrics, Digital Texture Fingerprint, visualizations
```

### Segmentation algorithms

**Sauvola local adaptive thresholding** (white crumb).
A per-pixel threshold is computed from the local mean and standard deviation in a 51 px window: `T(x,y) = μ(x,y) · [1 + k · (σ(x,y)/R − 1)]`. Each region of the image therefore receives a threshold appropriate to its local brightness, which is robust to the illumination gradients common in photographic acquisition. Sauvola is applied to the CLAHE-enhanced image so that local cell–wall contrast is maximised before segmentation.

**HisAnalysis peak-mode thresholding** (BSG / dark crumb).
The intensity bin with the highest frequency in the blurred raw grayscale histogram corresponds to the dominant crumb colour. The threshold is set at `peak + offset` (default offset = −8 %); pixels darker than this threshold are classified as gas cells. HisAnalysis is computed on the unenhanced grayscale because CLAHE redistributes the histogram and destroys the peak that the method depends on. This is the configuration validated by Bosakova-Ardenska et al. (2015) for brown bread, with a reported correlation of *r* = 0.93 against physicochemical porosity.

---

## Limitations

1. **Flatbed scan vs. photograph.** Photographs taken under directional or flash illumination produce highlights inside large gas cells, which are then missed by the segmentation. This systematically underestimates porosity. Flatbed scanning at 200 dpi or higher is recommended for thesis and publication-grade work ([Gonzales-Barron & Butler, 2006](#references)).
2. **2D vs. 3D porosity.** Image analysis measures a single cross-section. True volumetric porosity, accessible by X-ray microtomography, is higher; the 3D correction factor is an approximation and should be reported transparently.
3. **Fibre artefacts in BSG crumb.** Coarse bran particles and fibre shadows that are darker than the crumb peak can be classified as gas cells. The binary mask should always be inspected visually before reporting results.
4. **Display resolution.** The working canvas is downsampled to a maximum of 650 px on the longer edge for performance. Full-resolution analysis (e.g. ImageJ with the same parameters) is recommended for archival work on high-resolution scans.
5. **Crust exclusion.** Crust pixels bias the histogram and the threshold. Always select an ROI that contains crumb only.

---

## Scientific Background and Validation

Digital image analysis (DIA) of bread crumb cross-sections is established in the cereal-science literature as an objective, non-destructive method for quantifying crumb structure. The following findings provide the validation basis for BreadScan's metrics and algorithmic choices:

- **Crumb density prediction.** Image-derived parameters including void fraction and cell-wall thickness predict crumb density with approximately 80 % accuracy ([Zghal, Scanlon & Sapirstein, 1999](#references)).
- **Comparative thresholding study.** A systematic comparison of seven thresholding techniques established the suitability of histogram-based methods for white bread under diffuse illumination, and identified the conditions under which they fail — uneven illumination and dark crumbs — motivating BreadScan's two-pathway design ([Gonzales-Barron & Butler, 2006](#references)).
- **Local-adaptive thresholding for uneven illumination.** Sauvola & Pietikäinen (2000) demonstrated that a per-pixel threshold derived from local mean and standard deviation produces robust binarisation under spatial illumination gradients, the regime in which Otsu fails on photographic crumb images.
- **HisAnalysis for brown bread.** Bosakova-Ardenska et al. (2015) validated the histogram-peak-offset approach specifically for brown bread crumb, reporting *r* = 0.93 against physicochemical porosity — the closest published method to the BSG/dark mode in BreadScan.
- **Multi-parameter fingerprinting.** Ruderman et al. (2025) introduced the digital-texture-fingerprint concept for bread, in which crumb structure is summarised by a small number of orthogonal morphological descriptors suitable for formulation comparison and quality benchmarking; BreadScan implements this concept with six descriptors.

---

## References

- **Bosakova-Ardenska, A., Danev, A., Andreeva, H. & Gogova, T.** (2015). Application of thresholding algorithms for brown bread porosity evaluation. *International Journal of Food Science and Applied Biotechnology*.
- **Gonzales-Barron, U. & Butler, F.** (2006). A comparison of seven thresholding techniques with the k-means clustering algorithm for measurement of bread-crumb features by digital image analysis. *Journal of Food Engineering*, 74(2), 268–278. https://doi.org/10.1016/j.jfoodeng.2005.03.007
- **Ruderman, G., Bretherton, I. and colleagues** (2025). Digital image analysis to assess the texture of bread products. *Current Research in Food Science*. https://doi.org/10.1016/j.crfs.2025.100007
- **Sauvola, J. & Pietikäinen, M.** (2000). Adaptive document image binarization. *Pattern Recognition*, 33(2), 225–236.
- **Zghal, M.C., Scanlon, M.G. & Sapirstein, H.D.** (1999). Prediction of bread crumb density by digital image analysis. *Cereal Chemistry*, 76(5), 734–742.

---

## Suggested Citation

```
Buzzeo, L. (2025). BreadScan: A browser-based digital image analysis tool
for bread crumb porosity. https://github.com/luciabuzzeo/Bread_porosity_scan
```

Cite the underlying algorithmic literature as appropriate (see [References](#references)).

---

## Repository Structure

```
Bread_porosity_scan/
├── bread_porosity_analyzer.html   ← Application (self-contained)
├── README.md                      ← This file
├── CHANGELOG.md                   ← Version history
├── LICENSE                        ← MIT licence
└── Test/
    ├── IMG_*.jpg                  ← Crumb cross-section images analysed with BreadScan
    └── Results.xlsx               ← Output metrics and Digital Texture Fingerprint per sample
```

---

## License

MIT Licence — see [LICENSE](LICENSE). Free to use, modify, and distribute for academic and commercial purposes with attribution.
