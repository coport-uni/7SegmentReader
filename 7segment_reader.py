"""Read a 7-segment LED display (DC power supply: V row + A row) from an image.

Pipeline:
  1. red_score = R - max(G, B)        # red purity, ignores white glare
  2. STRICT mask (red_score > 100)    # clean digit blobs (no inter-digit bleed)
  3. Fill small enclosed holes        # heal hollow segment centers caused
                                      # by camera saturation, while preserving
                                      # genuine digit interiors of 0/8/9/etc.
  4. Filter blobs by min height -> drop indicator/lens noise
  5. Cluster digit blobs into 2 rows by Y center
  6. Per digit bbox: sample 7 segment regions on filled STRICT mask -> on/off
                     pattern -> digit lookup table
  7. LOOSE mask (red_score > 60); for each digit count its below-baseline
     bottom-right probe pixels. The digit with max probe count in the row
     (significantly above median) has a trailing decimal point.
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

SEGMENT_TO_DIGIT = {
    (1, 1, 1, 1, 1, 1, 0): 0,
    (0, 1, 1, 0, 0, 0, 0): 1,
    (1, 1, 0, 1, 1, 0, 1): 2,
    (1, 1, 1, 1, 0, 0, 1): 3,
    (0, 1, 1, 0, 0, 1, 1): 4,
    (1, 0, 1, 1, 0, 1, 1): 5,
    (1, 0, 1, 1, 1, 1, 1): 6,
    (1, 1, 1, 0, 0, 0, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9,
}

# Sample regions within each digit bbox, as (x0, y0, x1, y1) ratios.
SEGMENT_REGIONS = {
    "a": (0.30, 0.00, 0.70, 0.18),
    "b": (0.78, 0.08, 1.00, 0.45),
    "c": (0.78, 0.55, 1.00, 0.92),
    "d": (0.30, 0.82, 0.70, 1.00),
    "e": (0.00, 0.55, 0.22, 0.92),
    "f": (0.00, 0.08, 0.22, 0.45),
    "g": (0.30, 0.42, 0.70, 0.58),
}

# A segment is considered "lit" when at least this fraction of its sample
# region intersects the strict mask. The threshold is set well below the
# 50/50 mark so that segments partially clipped by minor mis-alignment of
# the slant model still register, while remaining comfortably above the
# spurious bleed-in (typically <= 0.20) seen in OFF segments.
ON_THRESHOLD = 0.28
DIGIT_MIN_HEIGHT = 40
DIGIT_MIN_AREA = 300

# Italic slant of the LED font: tan(angle) of the vertical strokes.
# Top-of-digit pixels are shifted to the right by SLANT * (h / 2);
# bottom-of-digit pixels are shifted left by the same amount. The
# segment sample regions follow this shear so vertical segments such
# as b, c, e, f stay inside their region across the full digit height.
ITALIC_SLANT = 0.25

# Bright LED segments saturate the camera (R=G=B=255) so the strict
# red-purity mask renders each segment as a hollow ring with a small
# interior hole (~80-150 px). The genuine off-segment voids inside a
# digit (digit 0's centre ~700-940 px; digit 8's two halves ~240-340 px)
# are larger. Fill enclosed holes below this threshold.
HOLE_MAX_AREA = 200

# Decimal-point detection: probe a small window at the digit's lower-right
# corner extending below the baseline.
DOT_PROBE_X_LEFT_INSET = 10  # probe spans [right - X, right + 4] horizontally
DOT_PROBE_X_RIGHT_PAD = 4
DOT_PROBE_Y_TOP_INSET = 2
DOT_PROBE_Y_BOTTOM_PAD = 8
DOT_MIN_ABS = 12  # absolute pixel-count floor
# The dot-bearing digit's probe must exceed this multiple of the row median.
# Keep below 2.0 so that italic segment-c tails creeping into other digits'
# probe windows -- which raise the median by a few pixels -- do not gate
# out a clearly-present dot whose probe count is 1.5-1.9x the median.
DOT_RATIO_OVER_MEDIAN = 1.5


def red_score(bgr: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(bgr)
    return cv2.subtract(r, cv2.max(g, b))


def fill_small_holes(mask: np.ndarray, max_area: int) -> np.ndarray:
    """Seal enclosed background components below max_area in a binary mask.

    Camera saturation at the bright centre of each LED segment turns the
    strict red-purity mask into a hollow ring with a small interior hole.
    Filling those small holes restores the segment to a solid blob, while
    larger enclosed voids -- for example the segment-g-off region of digit
    0 or the upper/lower halves of digit 8 -- are preserved so segment
    sampling continues to distinguish them.

    Args:
        mask: 0/1 uint8 binary image.
        max_area: Maximum area (in pixels) of a hole that should be filled.

    Returns:
        A new 0/1 uint8 mask with qualifying holes set to 1.
    """
    h, w = mask.shape
    inverted = (1 - mask).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(
        inverted, connectivity=4
    )
    out = mask.copy()
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        # Skip the outer background, which always touches the image border.
        if x == 0 or y == 0 or x + ww == w or y + hh == h:
            continue
        if area <= max_area:
            out[labels == i] = 1
    return out


def detect_digit_blobs(strict: np.ndarray) -> list[tuple[int, int, int, int]]:
    n, _, stats, _ = cv2.connectedComponentsWithStats(strict, connectivity=8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if h >= DIGIT_MIN_HEIGHT and area >= DIGIT_MIN_AREA:
            out.append((int(x), int(y), int(w), int(h)))
    return out


def cluster_into_two_rows(
    digits: list[tuple[int, int, int, int]],
) -> tuple[list[tuple[int, int, int, int]], list[tuple[int, int, int, int]]]:
    if len(digits) < 2:
        raise RuntimeError(f"Need at least 2 digit blobs, got {len(digits)}")
    centers = sorted((d[1] + d[3] / 2, d) for d in digits)
    ys = [c for c, _ in centers]
    gaps = [(ys[i + 1] - ys[i], i) for i in range(len(ys) - 1)]
    gap_size, gap_idx = max(gaps)
    split_y = ys[gap_idx] + gap_size / 2
    top = sorted([d for c, d in centers if c < split_y], key=lambda d: d[0])
    bot = sorted([d for c, d in centers if c >= split_y], key=lambda d: d[0])
    return top, bot


def segment_ratio(
    sub: np.ndarray,
    region: tuple[float, float, float, float],
    slant: float,
) -> float:
    """Fraction of strict-mask pixels inside an italic-corrected region.

    Vertical segments (b, c, e, f) are sheared per row so each row
    follows the italic vertical stroke. Horizontal segments (a, d, g)
    are wider than they are tall; the bar itself stays horizontal in
    italic fonts and is only translated, so the whole sample rectangle
    is shifted by the slant computed at the region's vertical centre.
    Per-row shearing of a horizontal sample would push its right edge
    into adjacent segments and trigger false positives (e.g. digit 4
    picking up segment b through region a).
    """
    h, w = sub.shape
    x0r, y0r, x1r, y1r = region
    y0 = max(0, int(y0r * h))
    y1 = min(h, max(int(y1r * h), y0 + 1))
    is_horizontal = (x1r - x0r) > (y1r - y0r)
    if is_horizontal:
        y_center_norm = (y0r + y1r) / 2
        shift_norm = slant * (0.5 - y_center_norm)
        sx0 = max(0, int((x0r + shift_norm) * w))
        sx1 = min(w, max(int((x1r + shift_norm) * w), sx0 + 1))
        if sx0 >= sx1:
            return 0.0
        region_pixels = sub[y0:y1, sx0:sx1]
        if region_pixels.size == 0:
            return 0.0
        return float((region_pixels > 0).sum()) / region_pixels.size
    on = 0
    total = 0
    for y in range(y0, y1):
        shift = slant * (h / 2 - y)
        sx0 = int(x0r * w + shift)
        sx1 = int(x1r * w + shift)
        sx0 = max(0, sx0)
        sx1 = min(w, max(sx1, sx0 + 1))
        if sx0 >= sx1:
            continue
        row = sub[y, sx0:sx1]
        on += int((row > 0).sum())
        total += sx1 - sx0
    return on / total if total > 0 else 0.0


def decode_digit(strict: np.ndarray, x: int, y: int, w: int, h: int) -> str:
    if w < h * 0.35:
        return "1"
    sub = strict[y : y + h, x : x + w]
    pattern: list[int] = []
    for seg in ("a", "b", "c", "d", "e", "f", "g"):
        ratio = segment_ratio(sub, SEGMENT_REGIONS[seg], ITALIC_SLANT)
        pattern.append(int(ratio >= ON_THRESHOLD))
    digit = SEGMENT_TO_DIGIT.get(tuple(pattern))
    return str(digit) if digit is not None else "?"


def decimal_probe(
    loose: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
) -> tuple[int, tuple[int, int, int, int]]:
    img_h, img_w = loose.shape
    px0 = max(x + w - DOT_PROBE_X_LEFT_INSET, 0)
    px1 = min(x + w + DOT_PROBE_X_RIGHT_PAD, img_w)
    py0 = max(y + h - DOT_PROBE_Y_TOP_INSET, 0)
    py1 = min(y + h + DOT_PROBE_Y_BOTTOM_PAD, img_h)
    if px0 >= px1 or py0 >= py1:
        return 0, (px0, py0, 0, 0)
    region = loose[py0:py1, px0:px1]
    return int((region > 0).sum()), (px0, py0, px1 - px0, py1 - py0)


def assemble_row(
    digits: list[tuple[int, int, int, int]],
    strict: np.ndarray,
    loose: np.ndarray,
) -> tuple[str, list]:
    """Decode digits L->R; insert '.' after the digit whose decimal probe
    score is the row's clear maximum (and above absolute floor)."""
    chars: list[str] = []
    debug: list[tuple] = []
    probes: list[tuple[int, tuple[int, int, int, int]]] = []
    for x, y, w, h in digits:
        token = decode_digit(strict, x, y, w, h)
        chars.append(token)
        debug.append(("digit", (x, y, w, h), token))
        probes.append(decimal_probe(loose, x, y, w, h))

    counts = [p[0] for p in probes]
    if counts:
        max_count = max(counts)
        median = sorted(counts)[len(counts) // 2]
        ratio_floor = DOT_RATIO_OVER_MEDIAN * max(median, 1)
        if max_count >= DOT_MIN_ABS and max_count >= ratio_floor:
            dot_idx = counts.index(max_count)
            for i, (cnt, box) in enumerate(probes):
                marker = "*" if i == dot_idx else ""
                debug.append(("probe", box, f"{cnt}{marker}"))
            # insert dot after the digit at dot_idx
            chars.insert(dot_idx + 1, ".")
            return "".join(chars), debug
    for cnt, box in probes:
        debug.append(("probe", box, str(cnt)))
    return "".join(chars), debug


def parse_value(s: str) -> float | None:
    if not s or "?" in s or s in (".", ".."):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def read_display(image_path: str, debug: bool = False) -> dict:
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise FileNotFoundError(image_path)

    score = red_score(bgr)
    strict = (score > 100).astype(np.uint8)
    strict = fill_small_holes(strict, HOLE_MAX_AREA)
    loose = (score > 60).astype(np.uint8)

    digits_all = detect_digit_blobs(strict)
    if not digits_all:
        raise RuntimeError("No digit-sized red blobs found")
    top_digits, bot_digits = cluster_into_two_rows(digits_all)

    v_str, v_dbg = assemble_row(top_digits, strict, loose)
    a_str, a_dbg = assemble_row(bot_digits, strict, loose)

    if debug:
        os.makedirs("debug", exist_ok=True)
        cv2.imwrite("debug/01_strict.png", strict * 255)
        cv2.imwrite("debug/02_loose.png", loose * 255)
        _draw_overlay(bgr, v_dbg, a_dbg, v_str, a_str, "debug/03_decoded.png")

    return {
        "V_raw": v_str,
        "A_raw": a_str,
        "V": parse_value(v_str),
        "A": parse_value(a_str),
    }


def _draw_overlay(bgr, v_dbg, a_dbg, v_str, a_str, path):
    vis = bgr.copy()
    for kind, box, label in v_dbg + a_dbg:
        x, y, w, h = box
        if kind == "digit":
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 1)
            cv2.putText(
                vis,
                label,
                (x, y - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )
        else:
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 200, 255), 1)
            cv2.putText(
                vis,
                label,
                (x, y + h + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 200, 255),
                1,
                cv2.LINE_AA,
            )
    cv2.putText(
        vis,
        f"V: {v_str}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        vis,
        f"A: {a_str}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
        cv2.LINE_AA,
    )
    cv2.imwrite(path, vis)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("image")
    p.add_argument(
        "--debug",
        action="store_true",
        help="dump intermediate stages to ./debug/",
    )
    args = p.parse_args()
    try:
        result = read_display(args.image, debug=args.debug)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["V"] is not None and result["A"] is not None else 1


if __name__ == "__main__":
    sys.exit(main())
