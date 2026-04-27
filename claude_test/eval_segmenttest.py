"""Evaluate 7segment_reader against the SegmentTest folder ground truth.

Reports per-image V/A predictions and overall correctness rate.
A row is considered correct only when the raw string equals truth
(both digits and decimal-point position).

Pass `--csv <path>` to also dump the per-image table as CSV.
"""

import argparse
import csv
import json
import os
import subprocess
import sys

GROUND_TRUTH = {
    "2026-04-27-165239.jpg": ("00.07", "0.000"),
    "2026-04-27-165309.jpg": ("05.96", "0.000"),
    "2026-04-27-165311.jpg": ("16.50", "0.000"),
    "2026-04-27-165313.jpg": ("25.89", "0.001"),
    "2026-04-27-165314.jpg": ("33.65", "0.000"),
    "2026-04-27-165316.jpg": ("41.20", "0.000"),
    "2026-04-27-165318.jpg": ("48.47", "0.000"),
    "2026-04-27-165320.jpg": ("55.91", "0.000"),
    "2026-04-27-165324.jpg": ("55.91", "0.698"),
    "2026-04-27-165326.jpg": ("55.91", "1.349"),
    "2026-04-27-165328.jpg": ("55.91", "2.279"),
    "2026-04-27-165329.jpg": ("55.91", "3.070"),
    "2026-04-27-165331.jpg": ("55.91", "3.905"),
    "2026-04-27-165333.jpg": ("55.91", "4.660"),
    "2026-04-27-165339.jpg": ("53.21", "4.665"),
    "2026-04-27-165341.jpg": ("45.98", "4.665"),
    "2026-04-27-165342.jpg": ("41.79", "4.665"),
    "2026-04-27-165344.jpg": ("33.28", "4.665"),
    "2026-04-27-165345.jpg": ("28.31", "4.665"),
    "2026-04-27-165347.jpg": ("22.88", "4.665"),
    "2026-04-27-165348.jpg": ("18.58", "4.665"),
    "2026-04-27-165350.jpg": ("15.67", "4.665"),
    "2026-04-27-165351.jpg": ("03.34", "4.665"),
    "2026-04-27-165352.jpg": ("00.07", "4.665"),
    "2026-04-27-165355.jpg": ("00.07", "3.830"),
    "2026-04-27-165356.jpg": ("00.07", "3.586"),
    "2026-04-27-165358.jpg": ("00.07", "2.916"),
    "2026-04-27-165359.jpg": ("00.07", "2.483"),
    "2026-04-27-165401.jpg": ("00.07", "1.536"),
    "2026-04-27-165403.jpg": ("00.07", "0.466"),
    "2026-04-27-165404.jpg": ("00.07", "0.000"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        metavar="PATH",
        help="also write per-image table to PATH as CSV",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(root, "SegmentTest")
    reader = os.path.join(root, "7segment_reader.py")
    py = sys.executable
    correct_v = correct_a = correct_both = 0
    total = len(GROUND_TRUTH)
    rows = []
    skipped = 0
    for fname in sorted(GROUND_TRUTH):
        truth_v, truth_a = GROUND_TRUTH[fname]
        path = os.path.join(folder, fname)
        if not os.path.exists(path):
            skipped += 1
            rows.append(
                (fname, truth_v, "MISSING", False, truth_a, "MISSING", False)
            )
            continue
        proc = subprocess.run(
            [py, reader, path], capture_output=True, text=True
        )
        try:
            data = json.loads(proc.stdout)
            pv, pa = data["V_raw"], data["A_raw"]
        except json.JSONDecodeError:
            pv, pa = "ERR", "ERR"
        v_ok = pv == truth_v
        a_ok = pa == truth_a
        correct_v += v_ok
        correct_a += a_ok
        correct_both += v_ok and a_ok
        rows.append((fname, truth_v, pv, v_ok, truth_a, pa, a_ok))
    total -= skipped

    print(
        f"{'file':32s}  {'V_truth':>7s} {'V_pred':>7s} V?  "
        f"{'A_truth':>7s} {'A_pred':>7s} A?"
    )
    for r in rows:
        f, tv, pv, vk, ta, pa, ak = r
        print(
            f"{f:32s}  {tv:>7s} {pv:>7s} "
            f"{'OK' if vk else 'X ':>2s}  "
            f"{ta:>7s} {pa:>7s} {'OK' if ak else 'X ':>2s}"
        )
    print()
    print(f"V correct: {correct_v}/{total} ({100 * correct_v / total:.1f}%)")
    print(f"A correct: {correct_a}/{total} ({100 * correct_a / total:.1f}%)")
    print(
        f"Both:      {correct_both}/{total} ({100 * correct_both / total:.1f}%)"
    )

    if args.csv:
        with open(args.csv, "w", newline="") as fp:
            writer = csv.writer(fp)
            writer.writerow(
                [
                    "file",
                    "V_truth",
                    "V_pred",
                    "V_correct",
                    "A_truth",
                    "A_pred",
                    "A_correct",
                ]
            )
            for f, tv, pv, vk, ta, pa, ak in rows:
                writer.writerow([f, tv, pv, int(vk), ta, pa, int(ak)])
        print(f"\nCSV written to {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
