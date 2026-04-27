# claude_test/

Throwaway debug scripts and one-off experiments. See CLAUDE.md §3 / §8.

| File | Purpose | Outcome |
|------|---------|---------|
| `probe_masks.py` | Dump strict-mask digit blob and hole area stats across SegmentTest images. Used to pick the hole-fill / morphology thresholds for the robust `7segment_reader.py` upgrade. | Informed kernel and area selection. |
| `eval_segmenttest.py` | Run `7segment_reader.py` against every SegmentTest image and compare the predicted V/A strings to a hard-coded ground-truth table. Prints per-image rows and an overall correctness rate. Pass `--csv PATH` to also dump the table as CSV. | Used to verify the robustness target. |
| `probe_segments.py` | For one image, print each detected digit's bounding box plus the seven segment-region "lit" ratios. Diagnoses why a digit decodes to '?' (borderline ON ratio vs blob fragmentation). | Used while tuning ON_THRESHOLD / sample regions. |
| `probe_decimal.py` | Print each digit's decimal-probe pixel count and the assemble_row gating thresholds (max, median, min_abs, ratio_floor). Diagnoses why an expected decimal point is missing in the decoded string. | Used while tuning DOT_MIN_ABS / DOT_RATIO_OVER_MEDIAN. |
