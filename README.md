# 7-Segment Display Reader

Reads voltage and current from a regulated DC power supply that has a two-row red 7-segment display. Given an image, [`7segment_reader.py`](7segment_reader.py) emits the V row and A row both as raw strings (with the decimal point) and as parsed `float` values.

```bash
python 7segment_reader.py SegmentTest/2026-04-27-165316.jpg
# {"V_raw": "41.20", "A_raw": "0.000", "V": 41.2, "A": 0.0}
```

Add `--debug` to dump the intermediate masks and the decoded overlay into `./debug/`.

---

## Pipeline (illustrated on `SegmentTest/2026-04-27-165316.jpg`)

### 1. Input

The display in the photo shows V = 41.20 and A = 0.000. The LED segments are bright enough that the camera saturates their centres, while the room behind the panel adds white reflections.

![input](docs/pipeline/01_input.jpg)

### 2. Red purity score → STRICT mask + small-hole fill

For each pixel the reader computes `red_score = R − max(G, B)`. Pure red is large positive, white room reflections are near zero, and black panel area is zero — so the score isolates the LED light without any explicit colour space conversion.

Thresholding at `score > 100` gives a clean digit mask, but at saturated segment centres `R = G = B ≈ 255` makes `red_score ≈ 0`, so each segment renders as a *hollow ring*. A small-hole fill (`fill_small_holes`, ≤ 200 px enclosed components) seals these saturation voids without touching the genuine off-segment interior of digit 0 (~700–940 px) or the upper/lower halves of digit 8 (~240–340 px).

![strict mask after hole fill](docs/pipeline/02_strict_mask.png)

### 3. LOOSE mask (`score > 60`)

A second, more permissive mask is kept hollow — it is used only for decimal-point detection. Hole-filling here would risk merging the dot with segment c's saturation void.

![loose mask](docs/pipeline/03_loose_mask.png)

### 4. Connected-component blobs and row clustering

8-connectivity components on the strict mask, filtered by `height ≥ 40` and `area ≥ 300`, give exactly the eight digit blobs (the small "C.V" indicator and the V / A row labels are dropped automatically). Sorting their Y-centres and splitting at the largest gap separates the V row from the A row; each row is then sorted left-to-right.

### 5. Italic-aware segment sampling

Each digit bounding box is checked against an aspect-ratio shortcut (`w / h < 0.35` ⇒ `"1"`). Otherwise seven sample regions, one per segment a–g, are tested against the strict mask:

```text
 a (top)            (0.30, 0.00, 0.70, 0.18)
 b (top-right)      (0.78, 0.08, 1.00, 0.45)
 c (bottom-right)   (0.78, 0.55, 1.00, 0.92)
 d (bottom)         (0.30, 0.82, 0.70, 1.00)
 e (bottom-left)    (0.00, 0.55, 0.22, 0.92)
 f (top-left)       (0.00, 0.08, 0.22, 0.45)
 g (middle)         (0.30, 0.42, 0.70, 0.58)
```

The display font has ≈ 14° italic slant (`ITALIC_SLANT = 0.25`), so axis-aligned rectangles would miss the bottom of segment c and let it bleed into segment d:

- **Vertical segments (b, c, e, f)** — each row of the sample region is sheared by `slant × (h/2 − y)`, forming a parallelogram that tracks the slanted vertical stroke.
- **Horizontal segments (a, d, g)** — the bar itself stays horizontal in italic; the entire rectangle is *translated* by the slant computed at the segment's vertical centre. This avoids a segment-c-bottom false positive on segment d (which previously turned `7` into `?`).

A segment is ON when its lit-pixel ratio is at least `ON_THRESHOLD = 0.28`, comfortably below segments that should fire (typically 0.4–1.0) yet above bleed-in (typically ≤ 0.20). The 7-tuple is then looked up in `SEGMENT_TO_DIGIT`; an unknown pattern returns `?`.

### 6. Decimal point

For each digit, a 14 × 10 probe at the lower-right corner counts loose-mask pixels. The row's maximum count is taken to mark the dot-bearing digit, gated by:

- `max ≥ DOT_MIN_ABS (= 12)` — absolute floor (no row-wide hallucination)
- `max ≥ DOT_RATIO_OVER_MEDIAN (= 1.5) × median` — the dot must stand out from the rest of the row

A `.` is then inserted *after* the matching digit. The 1.5× factor is below the obvious 2.0× because italic segment-c tails creep into the other digits' probe windows and inflate the median.

### 7. Final overlay

Green boxes are detected digits with their decoded character; orange boxes are decimal probes with their pixel counts (the starred count marks the dot insertion point). The cyan caption at the top-left echoes the assembled raw strings.

![decoded overlay](docs/pipeline/04_decoded_overlay.png)

---

## Accuracy on the `SegmentTest/` folder

Evaluated against a hand-labelled ground truth via [`claude_test/eval_segmenttest.py`](claude_test/eval_segmenttest.py); per-image results are in [`segmenttest_results.csv`](segmenttest_results.csv).

| Metric | Result |
|---|---|
| V row exact match | 29 / 30 (96.7%) |
| A row exact match | 28 / 30 (93.3%) |
| Both rows | 27 / 30 (90.0%) |

The remaining failures are all italic-segment-c bleed cases on digit 7.

---

## Repository layout

| Path | Purpose |
|---|---|
| [`7segment_reader.py`](7segment_reader.py) | Main reader (CLI + library entry point `read_display`). |
| [`SegmentTest/`](SegmentTest/) | 30 photos of the regulated DC power supply across a sweep of V / A values. |
| [`debug_example/dev_video6_640x480.jpg`](debug_example/dev_video6_640x480.jpg) | The original reference frame the reader was first tuned against. |
| [`docs/pipeline/`](docs/pipeline/) | The four pipeline images embedded above (input + strict + loose + decoded). |
| [`claude_test/`](claude_test/) | Evaluation and probing scripts: `eval_segmenttest.py` (CSV output), `probe_masks.py`, `probe_segments.py`, `probe_decimal.py`. |
| [`segmenttest_results.csv`](segmenttest_results.csv) | Per-image ground truth vs prediction. |
