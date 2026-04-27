"""Capture one sample frame from every /dev/video* device.

Each saved file is named after its device path so you can eyeball the
images and identify which physical camera maps to which device node.
"""

import glob
import os
import sys
import time

import cv2

OUTPUT_DIR = "camera_samples"
WARMUP_FRAMES = 5


def device_index(path: str) -> int:
    return int(os.path.basename(path).removeprefix("video"))


def safe_name(path: str) -> str:
    return path.replace("/", "_").lstrip("_")


def capture_one(path: str) -> tuple[bool, str]:
    idx = device_index(path)
    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
    if not cap.isOpened():
        return False, "open failed"

    try:
        frame = None
        for _ in range(WARMUP_FRAMES):
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.05)
                continue
        if frame is None:
            return False, "no frame"

        h, w = frame.shape[:2]
        out = os.path.join(OUTPUT_DIR, f"{safe_name(path)}_{w}x{h}.jpg")
        if not cv2.imwrite(out, frame):
            return False, "imwrite failed"
        return True, out
    finally:
        cap.release()


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    devices = sorted(glob.glob("/dev/video*"), key=device_index)
    if not devices:
        print("No /dev/video* devices found.", file=sys.stderr)
        return 1

    results: list[tuple[str, bool, str]] = []
    for dev in devices:
        ok, info = capture_one(dev)
        results.append((dev, ok, info))
        marker = "OK " if ok else "SKIP"
        print(f"{marker} {dev:14s} {info}")

    saved = sum(1 for _, ok, _ in results if ok)
    print(f"\nSaved {saved}/{len(results)} samples to ./{OUTPUT_DIR}/")
    return 0 if saved else 2


if __name__ == "__main__":
    sys.exit(main())
