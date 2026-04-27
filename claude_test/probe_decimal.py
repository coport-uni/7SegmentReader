"""Print per-digit decimal probe counts for one image.

Helps diagnose missing decimal points (e.g., "0466" instead of "0.466"):
the assemble_row inserts a dot only if the maximum probe count is both
above DOT_MIN_ABS and DOT_RATIO_OVER_MEDIAN times the median. When the
dot is barely detected, those gates suppress it.
"""

import importlib.util
import os
import sys

import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
spec = importlib.util.spec_from_file_location(
    "reader", os.path.join(ROOT, "7segment_reader.py")
)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def main():
    path = sys.argv[1]
    bgr = cv2.imread(path)
    score = reader.red_score(bgr)
    strict = (score > 100).astype("uint8")
    strict = reader.fill_small_holes(strict, reader.HOLE_MAX_AREA)
    loose = (score > 60).astype("uint8")
    digits = reader.detect_digit_blobs(strict)
    top, bot = reader.cluster_into_two_rows(digits)
    for label, row in [("V", top), ("A", bot)]:
        print(f"=== {label} row ===")
        probes = [reader.decimal_probe(loose, *d) for d in row]
        counts = [p[0] for p in probes]
        for d, (cnt, box) in zip(row, probes):
            print(
                f"  digit bbox=({d[0]},{d[1]},{d[2]},{d[3]}) "
                f"probe={cnt} probe_box={box}"
            )
        if counts:
            mx = max(counts)
            med = sorted(counts)[len(counts) // 2]
            floor = reader.DOT_RATIO_OVER_MEDIAN * max(med, 1)
            print(
                f"  max={mx} median={med} "
                f"min_abs={reader.DOT_MIN_ABS} "
                f"ratio_floor={floor}"
            )


if __name__ == "__main__":
    main()
