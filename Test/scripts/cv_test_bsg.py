"""
CV reproducibility test for BreadScan v5.2 — BSG / HisAnalysis path.

Mirrors the BSG/dark branch of the analyser:
  - Crop ROI in original-image px
  - Resample to constant working resolution (10 px/mm)
  - Luminance grayscale
  - Gaussian blur (sigma = 2.0 for BSG)
  - HisAnalysis peak-mode threshold on RAW blurred grayscale (no CLAHE)
      threshold = peak + offset%, default offset = -8% (in 0..255 bin space)
      pixels darker than threshold are classified as gas cells
  - Morphological closing (radius = 3 for BSG)
  - Connected-components labelling (8-connectivity)
  - mm²-based size filter (0.05 mm² min, 150 mm² max)
"""

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_closing, label, generate_binary_structure
import statistics
import sys

IMG_PATH = r"C:\Users\Usuario\Repos\Bread_porosity_scan\Test\IMG_2022.jpg"

PX_PER_MM_ORIG = 16.0    # estimated from the ruler in the image
TARGET_PX_PER_MM = 10.0  # v5.2 constant working resolution

# BSG / HisAnalysis defaults (as set in BreadScan)
SIGMA = 2.0
PEAK_OFFSET_PCT = -8     # -20..+30 in BreadScan; -8 detects only pixels darker than peak
MORPH_R = 3
MIN_AREA_MM2 = 0.05
MAX_AREA_MM2 = 150.0


def hisanalysis_threshold(gray_blurred: np.ndarray, offset_pct: int) -> tuple[float, int, int]:
    """Replicates the JS hisAnalysisPeakMode() function.
    Returns (t_norm, peak_bin, thresh_bin)."""
    # Histogram on 0..255 bin grayscale
    g255 = (gray_blurred * 255.0).clip(0, 255).astype(np.uint8)
    hist = np.bincount(g255.ravel(), minlength=256)
    peak_bin = int(np.argmax(hist))
    # offset_pct is interpreted in BreadScan as "% of range" → 256 bins × pct/100
    offset_bins = int(round(offset_pct * 2.56))
    thresh_bin = max(0, min(255, peak_bin + offset_bins))
    t_norm = thresh_bin / 255.0
    return t_norm, peak_bin, thresh_bin


def bsg_pipeline(roi_rgb_uint8: np.ndarray, px_per_mm: float) -> dict:
    rgb = roi_rgb_uint8.astype(np.float32) / 255.0
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    blurred = gaussian_filter(gray, sigma=SIGMA)

    t_norm, peak_bin, thresh_bin = hisanalysis_threshold(blurred, PEAK_OFFSET_PCT)
    binary = blurred < t_norm

    if MORPH_R > 0:
        struct = generate_binary_structure(2, 2)
        binary = binary_closing(binary, structure=struct, iterations=MORPH_R)

    structure_8 = generate_binary_structure(2, 2)
    lab, n = label(binary, structure=structure_8)

    if n == 0:
        return dict(void_fraction_pct=0.0, cell_count=0,
                    cell_density_per_cm2=0.0, mean_cell_area_mm2=0.0,
                    peak_bin=peak_bin, thresh_bin=thresh_bin)

    counts = np.bincount(lab.ravel())
    counts[0] = 0
    area_px = counts[1:]

    px2_per_mm2 = px_per_mm * px_per_mm
    min_px = MIN_AREA_MM2 * px2_per_mm2
    max_px = MAX_AREA_MM2 * px2_per_mm2
    valid_mask = (area_px >= min_px) & (area_px <= max_px)
    valid_areas = area_px[valid_mask]

    total_px = binary.size
    pore_px = float(valid_areas.sum())
    void_frac = pore_px / total_px

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
        peak_bin=peak_bin,
        thresh_bin=thresh_bin,
    )


def crop_and_resample(image: np.ndarray, x_mm: float, y_mm: float,
                      w_mm: float, h_mm: float, px_per_mm_orig: float) -> np.ndarray:
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
    print(f"Image: {W}×{H} px  ({W/PX_PER_MM_ORIG:.1f}×{H/PX_PER_MM_ORIG:.1f} mm at {PX_PER_MM_ORIG} px/mm)\n")

    # Crumb area on IMG_2022 (BSG sample 9): roughly x in [30, 110] mm,
    # y in [60, 200] mm. Centre ROIs around (70, 130) mm.
    base_x_mm, base_y_mm = 50.0, 110.0
    rois = [
        ("R1: base 40×40",         base_x_mm,          base_y_mm,          40.0, 40.0),
        ("R2: shift +3,−2",        base_x_mm + 3.0,    base_y_mm - 2.0,    40.0, 40.0),
        ("R3: shift −2,+3",        base_x_mm - 2.0,    base_y_mm + 3.0,    40.0, 40.0),
        ("R4: 38×42 -1,+0",        base_x_mm - 1.0,    base_y_mm,          38.0, 42.0),
        ("R5: 42×38 +1,+1",        base_x_mm + 1.0,    base_y_mm + 1.0,    42.0, 38.0),
    ]

    results = []
    print(f"{'ROI':<22}{'VF %':>10}{'Cells':>8}{'Cells/cm²':>14}{'Mean mm²':>12}{'Peak':>8}{'Thr':>6}")
    print("-" * 80)
    for name, xm, ym, wm, hm in rois:
        roi = crop_and_resample(img, xm, ym, wm, hm, PX_PER_MM_ORIG)
        m = bsg_pipeline(roi, TARGET_PX_PER_MM)
        results.append(m)
        print(f"{name:<22}"
              f"{m['void_fraction_pct']:>10.2f}"
              f"{m['cell_count']:>8d}"
              f"{m['cell_density_per_cm2']:>14.2f}"
              f"{m['mean_cell_area_mm2']:>12.4f}"
              f"{m['peak_bin']:>8d}"
              f"{m['thresh_bin']:>6d}")

    print("-" * 80)
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
