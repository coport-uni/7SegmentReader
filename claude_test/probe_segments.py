"""Print per-digit segment ratios for a single image to diagnose '?'.

Loads the same strict + hole-fill pipeline used by 7segment_reader,
then prints each digit's bounding box and the ratio of "lit" pixels
in each of the seven segment sample regions. Helps reveal whether a
'?' is caused by a borderline ON_THRESHOLD or by digit fragmentation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib.util

import cv2

spec = importlib.util.spec_from_file_location(
    "reader",
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "7segment_reader.py",
    ),
)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def main():
    path = sys.argv[1]
    bgr = cv2.imread(path)
    score = reader.red_score(bgr)
    strict = (score > 100).astype("uint8")
    strict = reader.fill_small_holes(strict, reader.HOLE_MAX_AREA)
    digits = reader.detect_digit_blobs(strict)
    top, bot = reader.cluster_into_two_rows(digits)
    for label, row in [("V", top), ("A", bot)]:
        print(f"=== {label} row ===")
        for x, y, w, h in row:
            sub = strict[y : y + h, x : x + w]
            ratios = {}
            pat = []
            for seg in ("a", "b", "c", "d", "e", "f", "g"):
                ratio = reader.segment_ratio(
                    sub, reader.SEGMENT_REGIONS[seg], reader.ITALIC_SLANT
                )
                ratios[seg] = ratio
                pat.append(int(ratio >= reader.ON_THRESHOLD))
            digit = reader.SEGMENT_TO_DIGIT.get(tuple(pat), "?")
            ratio_str = " ".join(f"{seg}={r:.2f}" for seg, r in ratios.items())
            print(
                f"  bbox=({x},{y},{w},{h}) wh={w / h:.2f} "
                f"pat={tuple(pat)} -> {digit}\n   {ratio_str}"
            )


if __name__ == "__main__":
    main()
