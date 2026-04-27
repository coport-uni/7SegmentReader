"""Probe mask shape statistics for SegmentTest images.

Goal: pick a hole-fill area threshold that closes hollow segment centers
caused by camera saturation, but preserves the larger segment-g-off
interior of digits like '0' / '8'.
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cv2
import numpy as np


def red_score(bgr):
    b, g, r = cv2.split(bgr)
    return cv2.subtract(r, cv2.max(g, b))


def hole_areas(mask):
    """Areas of background components NOT touching the image border."""
    h, w = mask.shape
    inv = (1 - mask).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    out = []
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        if x == 0 or y == 0 or x + ww == w or y + hh == h:
            continue
        out.append((int(area), int(ww), int(hh)))
    return out


def digit_blob_stats(mask):
    """Heights of foreground components."""
    n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    out = []
    for i in range(1, n):
        x, y, ww, hh, area = stats[i]
        out.append((int(area), int(ww), int(hh)))
    return out


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "SegmentTest/*.jpg"
    files = sorted(glob.glob(pattern))
    print(f"Files: {len(files)}\n")
    for f in files:
        bgr = cv2.imread(f)
        score = red_score(bgr)
        strict = (score > 100).astype(np.uint8)
        digits = digit_blob_stats(strict)
        digits = [d for d in digits if d[2] >= 20]
        holes = hole_areas(strict)
        digits_sorted = sorted(digits, key=lambda d: -d[0])[:8]
        holes_sorted = sorted(holes, key=lambda h: -h[0])[:12]
        print(os.path.basename(f))
        print(f"  digits (area,w,h): {digits_sorted}")
        print(f"  holes  (area,w,h): {holes_sorted}")
        print()


if __name__ == "__main__":
    main()
