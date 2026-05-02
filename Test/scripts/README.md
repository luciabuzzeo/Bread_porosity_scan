# BreadScan — CV reproducibility tests

Two Python scripts that reimplement the BreadScan v5.2 pipeline and run
it on a single image with several slightly different ROIs (varying
position, size and aspect). They quantify how much variability a manual
ROI selection introduces under the scale-invariant pipeline, isolating
operator-induced variability from genuine intra-loaf heterogeneity.

| Script | Path tested | Image |
|---|---|---|
| `cv_test_white.py` | Sauvola + CLAHE (white / control wheat) | `Test/IMG_2005.jpg` (Flour control) |
| `cv_test_bsg.py`   | HisAnalysis peak-mode (BSG / dark)      | `Test/IMG_2022.jpg` (20 % BSG_fraction + 140 ppm enzyme) |

## Requirements

- Python ≥ 3.10
- `numpy`, `scipy`, `Pillow`
- `scikit-image` *(white-bread script only — used for `equalize_adapthist` and `threshold_sauvola`)*

```
py -m pip install --user numpy scipy Pillow scikit-image
```

## Run

```
py Test/scripts/cv_test_white.py
py Test/scripts/cv_test_bsg.py
```

Each script prints per-ROI metrics and the mean ± SD ± **CV %** across
the 5 ROIs.

## Reference results (v5.2, IMG_2005 white path / IMG_2022 BSG path)

| Metric | White CV | BSG CV |
|---|---:|---:|
| Void Fraction (%)  | 0.13 % | 3.55 % |
| Cell Count         | 4.93 % | 8.33 % |
| Cell Density (cm⁻²)| 4.96 % | 8.33 % |
| Mean Cell Area     | 5.13 % | 11.37 % |

Compare against the pre-v5.2 baseline in `Test/Results.xlsx`, which
showed Mean Cell Area CV up to **28 %** under free-rectangle ROIs with
the old variable-rescale pipeline.

## Calibration

The scripts assume `PX_PER_MM_ORIG = 16.0`, estimated from the ruler
visible in the test images. The exact value does not affect the reported
CV (the same calibration is applied to all ROIs); it only affects
absolute mm² values.

## Faithfulness to the in-browser tool

The scripts mirror the v5.2 JavaScript pipeline:

- Luminance grayscale (`0.299 R + 0.587 G + 0.114 B`)
- Gaussian blur (σ = 1.0 white, 2.0 BSG)
- *White*: CLAHE → Sauvola adaptive threshold (window 51 px, k = 0.2)
- *BSG*:   HisAnalysis peak-mode threshold on raw blurred grayscale
           (`threshold = peak + offset%`, default offset −8 %)
- Morphological closing (radius 1 white, 3 BSG)
- Connected-components labelling, 8-connectivity
- mm²-based size filter (0.10 / 0.05 mm² minimum, 150 mm² maximum)
- Constant 10 px/mm working resolution after ROI cropping

The only point of divergence from the in-browser tool is `scikit-image`'s
CLAHE implementation, which is functionally equivalent but not bit-identical
to BreadScan's hand-rolled CLAHE. Sauvola's local-adaptive thresholding
absorbs small differences.
