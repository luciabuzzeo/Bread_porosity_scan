"""
CV reproducibility test for BreadScan v5.2 (white-bread pipeline).

Replicates the BreadScan pipeline in Python and runs it on a single image
with several slightly different ROIs (varying position, size and aspect)
to quantify how much variation a manual ROI selection introduces under
the v5.2 scale-invariant pipeline.

Pipeline mirrored from bread_porosity_analyzer.html:
  - Crop ROI in original-image px
  - Resample to constant working resolution (default 10 px/mm)
  - Luminance grayscale (0.299R + 0.587G + 0.114B)
  - Gaussian blur (sigma = 1.0 for white)
  - CLAHE (clip = 2.0, tile = 32 px)
  - Sauvola adaptive threshold (window = 51, k = 0.2)
  - Morphological closing (radius = 1 for white)
  - Connected-components labelling (8-connectivity)
  - mm²-based size filter (0.10 mm² min, 150 mm² max)
"""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_closing, label, generate_binary_structure
from skimage.exposure import equalize_adapthist
from skimage.filters import threshold_sauvola
import statistics
import sys

IMG_PATH = r"C:\Users\Usuario\Repos\Bread_porosity_scan\Test\IMG_2005.jpg"

# Calibration estimated from the ruler visible in IMG_2005.jpg.
# The ruler shows 1-6 cm (50 mm); visual measurement of the pixel span
# gives ~16 px/mm at the original 3024×4032 resolution.
PX_PER_MM_ORIG = 16.0

# v5.2 working resolution (constant after reRenderROI).
TARGET_PX_PER_MM = 10.0

# Pipeline parameters (white-bread defaults).
SIGMA = 1.0
CLAHE_CLIP = 2.0          # skimage uses 0..1 normalised clip
SAUVOLA_W = 51
SAUVOLA_K = 0.2
MORPH_R = 1
MIN_AREA_MM2 = 0.10
MAX_AREA_MM2 = 150.0


def crumb_only_pipeline(roi_rgb_uint8: np.ndarray, px_per_mm: float) -> dict:
    """Replicate the BreadScan analysis on a single ROI; return metrics."""
    rgb = roi_rgb_uint8.astype(np.float32) / 255.0
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

    blurred = gaussian_filter(gray, sigma=SIGMA)

    # CLAHE on the blurred grayscale; skimage's clip_limit is normalised in [0, 1].
    clip = max(0.005, min(1.0, CLAHE_CLIP / 40.0))
    enhanced = equalize_adapthist(blurred, clip_limit=clip, kernel_size=32)

    # Sauvola adaptive threshold on the enhanced image (white-bread path).
    t_local = threshold_sauvola(enhanced, window_size=SAUVOLA_W, k=SAUVOLA_K)
    binary = enhanced < t_local

    # Morphological closing with 4-connectivity structuring element radius=1.
    if MORPH_R > 0:
        struct = generate_binary_structure(2, 2)
        binary = binary_closing(binary, structure=struct, iterations=MORPH_R)

    # Connected-components labelling, 8-connectivity.
    structure_8 = generate_binary_structure(2, 2)
    lab, n = label(binary, structure=structure_8)

    if n == 0:
        return dict(void_fraction_pct=0.0, cell_count=0,
                    cell_density_per_cm2=0.0, mean_cell_area_mm2=0.0,
                    valid_cells=0)

    # Per-blob area in pixels.
    counts = np.bincount(lab.ravel())
    counts[0] = 0  # background
    area_px = counts[1:]

    # mm² filter at the working resolution.
    px2_per_mm2 = px_per_mm * px_per_mm
    min_px = MIN_AREA_MM2 * px2_per_mm2
    max_px = MAX_AREA_MM2 * px2_per_mm2
    valid_mask = (area_px >= min_px) & (area_px <= max_px)
    valid_areas = area_px[valid_mask]

    total_px = binary.size
    pore_px = float(valid_areas.sum())
    void_frac = pore_px / total_px

    # Cells per cm² (= per 100 mm²).
    if valid_areas.size:
        total_mm2 = total_px / px2_per_mm2
        density = valid_areas.size / (total_mm2 / 100.0)
        mean_area_mm2 = (pore_px / valid_areas.size) / px2_per_mm2
    else:
        density = 0.0
        mean_area_mm2 = 0.0

    return dict(
        void_fraction_pct=void_frac * 100,
        cell_count=int(valid_areas.size),
        cell_density_per_cm2=density,
        mean_cell_area_mm2=mean_area_mm2,
    )


def crop_and_resample(image: np.ndarray, x_mm: float, y_mm: float,
                      w_mm: float, h_mm: float, px_per_mm_orig: float) -> np.ndarray:
    """Crop a ROI specified in mm and resample to TARGET_PX_PER_MM."""
    x0 = int(round(x_mm * px_per_mm_orig))
    y0 = int(round(y_mm * px_per_mm_orig))
    x1 = int(round((x_mm + w_mm) * px_per_mm_orig))
    y1 = int(round((y_mm + h_mm) * px_per_mm_orig))
    crop = image[y0:y1, x0:x1, :]
    nw = max(8, int(round(w_mm * TARGET_PX_PER_MM)))
    nh = max(8, int(round(h_mm * TARGET_PX_PER_MM)))
    pil = Image.fromarray(crop).resize((nw, nh), Image.BILINEAR)
    return np.asarray(pil)


def cv_pct(values):
    if not values or statistics.mean(values) == 0:
        return float("nan")
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return sd / statistics.mean(values) * 100.0


def main():
    img = np.asarray(Image.open(IMG_PATH).convert("RGB"))
    H, W, _ = img.shape
    H_mm = H / PX_PER_MM_ORIG
    W_mm = W / PX_PER_MM_ORIG
    print(f"Image: {W}×{H} px  ({W_mm:.1f}×{H_mm:.1f} mm at {PX_PER_MM_ORIG} px/mm)\n")

    # Crumb is in the upper-left ~40% of the frame (avoiding crust, ruler, label).
    # ROI variations mimic a human operator drawing similar-but-not-identical
    # rectangles on three separate sessions.
    base_x_mm, base_y_mm = 30.0, 110.0   # top-left of base ROI in mm
    base_w_mm, base_h_mm = 40.0, 40.0

    rois = [
        ("R1: base 40×40",         base_x_mm,          base_y_mm,          40.0, 40.0),
        ("R2: shift +3,−2",        base_x_mm + 3.0,    base_y_mm - 2.0,    40.0, 40.0),
        ("R3: shift −2,+3",        base_x_mm - 2.0,    base_y_mm + 3.0,    40.0, 40.0),
        ("R4: 38×42 -1,+0",        base_x_mm - 1.0,    base_y_mm,          38.0, 42.0),
        ("R5: 42×38 +1,+1",        base_x_mm + 1.0,    base_y_mm + 1.0,    42.0, 38.0),
    ]

    results = []
    print(f"{'ROI':<22}{'VF %':>10}{'Cells':>8}{'Cells/cm²':>14}{'Mean mm²':>12}")
    print("-" * 66)
    for name, xm, ym, wm, hm in rois:
        roi = crop_and_resample(img, xm, ym, wm, hm, PX_PER_MM_ORIG)
        m = crumb_only_pipeline(roi, TARGET_PX_PER_MM)
        results.append(m)
        print(f"{name:<22}"
              f"{m['void_fraction_pct']:>10.2f}"
              f"{m['cell_count']:>8d}"
              f"{m['cell_density_per_cm2']:>14.2f}"
              f"{m['mean_cell_area_mm2']:>12.4f}")

    print("-" * 66)
    print("Summary across the 5 ROIs:")
    for key, label_ in [
        ("void_fraction_pct",      "  Void Fraction (%)     "),
        ("cell_count",             "  Cell Count            "),
        ("cell_density_per_cm2",   "  Cell Density (cm⁻²)   "),
        ("mean_cell_area_mm2",     "  Mean Cell Area (mm²) ")]:
        vals = [r[key] for r in results]
        mean = statistics.mean(vals)
        sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
        cv = cv_pct(vals)
        print(f"{label_}  mean={mean:>10.4f}  sd={sd:>10.4f}  CV={cv:>6.2f} %")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
