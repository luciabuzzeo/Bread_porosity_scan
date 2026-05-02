# Changelog

All notable changes to BreadScan are documented here.

---

## [5.2] — 2026

### Added
- **Constant working resolution.** Whenever the image is spatially calibrated, the ROI is rendered internally at a fixed *target px/mm* (default 10 px/mm). Sauvola's window and the morphological-closing kernel therefore correspond to the same physical size on every run, regardless of ROI shape or drawn size. This removes the dominant scale-dependent source of variability between repeats.
- **Cell-size filter in mm².** When the image is calibrated, the *Min/Max cell area* sliders are interpreted as physical sizes in mm² (defaults 0.10/150 mm² for white, 0.05/150 mm² for BSG). When uncalibrated, the legacy px² behaviour is retained. The same physical cell is now accepted or rejected consistently across runs.
- **Median cell area.** A new metric reported alongside the mean. The cell-area distribution is right-skewed; the median is robust to single outlier macro-cells and is less sensitive to small differences in ROI position. Also included in the CSV export.
- **Fixed-size square ROI** as an optional strict-determinism mode. A square of configurable side in mm (default 40 mm); operator drags only, no resize. Useful when the experimental design requires sampling exactly the same physical area on every loaf.
- **Session Results** sidebar block. Each successful analysis is appended to a per-browser store (`localStorage`), with filename, timestamp, calibration, ROI configuration and the full metrics set. *Export CSV* downloads a tidy table; *Clear* empties the store after confirmation. Persists across reloads.
- **← Back** button on the calibration modal. Returns from the ROI step to the calibration step, or from calibration to the upload-mode chooser, without forcing a re-upload of the image.

### Changed
- `reRenderROI()` now applies the constant working-resolution rendering to **both** ROI modes when calibrated; only the uncalibrated path keeps the legacy 650-pixel rescale.
- The generic `input[type=range]` listener that re-runs analysis on slider change is scoped explicitly to the analysis sliders, so ROI controls update the on-screen square live without triggering an analysis.
- Bread-type button toggling no longer accidentally clears the ROI-mode highlight (`#breadTypeBtns` selector restricts the toggle to the bread-type group).

### Why
First-round validation in `Test/Results.xlsx` showed coefficients of variation up to 28 % for *Mean Cell Area* across three repeats of the same loaf. The dominant cause was not operator imprecision but **scale-dependent processing**: the cell-size filter was in pixel units, and the rescale ratio in `reRenderROI()` varied with the ROI size. Same physical cells were accepted in one run and rejected in another. Putting the filter in mm² and locking the working resolution makes the pipeline scale-invariant, so repeated free-rectangle ROIs on the same image now produce closely matching results.

---

## [5.1] — 2025

### Added
- **Spatial calibration with a ruler.** Two-point tap workflow on the uploaded image with explicit *Confirm point* / *Redo* per point, followed by entry of the real distance in millimetres. Computes the px/mm scale factor and reports areas in mm², cell density in cells/cm², and wall thickness in mm.
- **Spatial calibration with a coin.** Same two-tap workflow across the coin diameter, with built-in references for 1 €, 2 €, 50 ¢, 10 ¢, US Quarter, US Nickel and UK £1.
- **Region-of-interest (ROI) selection.** After calibration, the operator drags a rectangle over the crumb area, excluding the crust, and confirms it. Crust pixels otherwise bias the histogram and the threshold. *Skip — use full image* and *Redo ROI* are also available.
- **Calibration badge** in the sidebar showing the active px/mm factor, calibration mode, and ROI dimensions in mm.
- **Automatic unit switching** in the metrics, fingerprint, log, and visualizations: physical units (mm, mm², cells/cm²) when calibrated; pixel units otherwise.

### Changed
- Renamed application file from `bread_porosity_analyzer_v5.html` to `bread_porosity_analyzer.html`. The version label is removed from page title, header strap-line, and badges.

---

## [5.0] — 2025

### Added
- **Sauvola local adaptive thresholding** for white/control bread. Replaces global Otsu. Computes a per-pixel threshold based on local mean and standard deviation (window=51px, k=0.2), eliminating the uneven-lighting problem where Otsu's single global threshold caused half the image to be misclassified.
- **8-connectivity** in connected components labeling (was 4-connectivity). Diagonal pixel connections are now recognized, preventing valid pores from being split into sub-threshold fragments.
- **Bread-type-specific default parameters** that auto-switch when selecting white vs. BSG mode.
- BSG-specific expected-range validation in analysis log (10–40% for photos, 35–47% for flatbed scans, per PMC9957138).
- Diagnostic warnings when BSG porosity falls below 5%.

### Changed
- **BSG thresholding now computed on RAW blurred grayscale, not CLAHE output** — faithful to Bosakova-Ardenska (2015). CLAHE flattens the histogram, destroying the peak that HisAnalysis uses to identify the dominant crumb color. This was the root cause of ~1.88% porosity (should be 15–40%).
- **BSG default Gaussian σ** increased from 1.0 to **2.0** — smooths BSG fiber texture before thresholding, reducing salt-and-pepper noise in the binary mask.
- **BSG default peak offset** changed from +5% to **−8%** — threshold is now set below the histogram peak, detecting only pixels significantly darker than the dominant crumb color as pores.
- **BSG default min cell area** reduced from 20 to **10 px²** — BSG bread has smaller, more fragmented pores.
- **BSG morphological closing radius** increased from 1 to **3** (7×7 kernel) — bridges fragmented pore regions caused by fiber texture. White bread keeps radius 1.
- CLAHE output is now used for **visualization only** in BSG mode (still used for Sauvola input in white mode).
- Histogram panel shows the image that was actually used for thresholding (CLAHE for white, raw grayscale for BSG).

### Fixed
- **BSG bread porosity ~1.88% instead of expected 15–40%** — caused by CLAHE destroying histogram peak before HisAnalysis threshold computation.
- **Colormap showing pores in only half the image for white bread** — caused by Otsu's single global threshold misclassifying the darker half of unevenly-lit photographs. Sauvola local adaptive thresholding resolves this.
- **Diagonally-connected pore pixels split into separate blobs** — 4-connectivity flood fill was fragmenting valid pores, inflating cell count and losing small pores below the min-area filter.

---

## [4.0] — 2025

### Added
- **HisAnalysis peak-mode algorithm** for BSG/dark bread thresholding, based on Bosakova-Ardenska (2015). Validated correlation r = 0.93 vs. physicochemical porosity for brown bread.
- **Digital Texture Fingerprint panel** — 6 structural parameters inspired by Ruderman et al. (2025): void fraction, cell density, mean cell area, cell uniformity, wall thickness estimate, macro pore %.
- **Colormap view** — pore size visualization using area-based color mapping (blue = micro, red = macro), after the "connected regions by area" visualization in Ruderman et al. (2025).
- **Histogram + threshold view** — intensity histogram of CLAHE-enhanced image showing threshold placement (gold line) and histogram peak (amber line). Essential for BSG mode parameter tuning.
- Cell density metric (cells per 100 px²) — crumb fineness indicator per Zghal et al. (1999).
- Cell uniformity (1 − CV of cell areas) — per Gonzales-Barron & Butler (2006).
- Literature references embedded in UI headers and algorithm badge.

### Changed
- **Removed circularity filter** as default. Bread pores are elliptical, not circular; circularity filtering rejects real pores (Gonzales-Barron & Butler 2006).
- Algorithm selection is now automatic based on bread type (white → Otsu, BSG → HisAnalysis).
- CLAHE default clip reduced to 2.0 (was 2.5) for less aggressive contrast enhancement on well-lit images.

### Fixed
- V3 LAB/chroma filter caused near-zero porosity (0.1%) on all images — removed entirely.
- V2 adaptive threshold with circularity ≥ 0.30 was rejecting valid BSG bread pores — replaced.

---

## [3.0] — 2025

### Added
- LAB colorspace conversion for color-aware pore detection.
- Chroma filter to distinguish neutral-dark pores from warm-colored BSG particles.

### Known Issues
- LAB + chroma approach caused ~0.1% porosity on photographic images due to ambient color cast across the entire image including pores. Deprecated in v4.

---

## [2.0] — 2025

### Added
- Shape filter: circularity (4πA/P²) and solidity validation per detected blob.
- Analysis log with per-step pixel counts.
- Validated pores view (gold = valid, red = rejected).
- Bread type preset system.

### Known Issues
- Default circularity threshold (0.30) too aggressive for real bread pores which are typically elliptical. Caused high rejection rates on valid pores.

---

## [1.0] — 2025

### Initial Release
- Grayscale → Gaussian blur → CLAHE → threshold (adaptive/Otsu/fixed).
- Connected components labeling.
- Pore size histogram.
- Basic metrics: 2D porosity, 3D estimated, pore count, mean area.
