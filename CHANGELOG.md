# Changelog

All notable changes to BreadScan are documented here.

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
