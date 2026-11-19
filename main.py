#!/usr/bin/env python3
"""news-image-20261119: place the finished front-page image at the output path.

The image is a finished JPEG (1024x1024) summing up Thursday 19 November
2026's world news; this program only copies its bytes to /output/entry.png.
Standard library only, no network, deterministic: the same bytes every run.
"""

import os
import sys
from pathlib import Path


PAYLOAD_NAME = "image.jpg"
TARGET_NAME = "entry.png"
JPEG_SOI = b"\xff\xd8\xff"
JPEG_EOI = b"\xff\xd9"
MAX_BYTES = 1_048_576


def locate_payload() -> Path:
    here = Path(__file__).resolve().parent
    candidate = here / PAYLOAD_NAME
    if not candidate.is_file():
        raise SystemExit(f"payload missing: {candidate}")
    return candidate


def confirm_jpeg(payload: Path) -> bytes:
    data = payload.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit(f"payload too large: {len(data)} bytes")
    if not data.startswith(JPEG_SOI):
        raise SystemExit("payload is not a JPEG (bad SOI marker)")
    if not data.endswith(JPEG_EOI):
        raise SystemExit("payload is not a whole JPEG (missing EOI marker)")
    return data


def place_copy(data: bytes) -> Path:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / TARGET_NAME
    target.write_bytes(data)
    return target


def confirm_written(target: Path, expected: bytes) -> None:
    """Read the output back and confirm it matches the payload byte for byte.

    The harness runs this program twice and compares the two outputs; a
    silent partial write would pass unnoticed without this read-back, so the
    program refuses to report success unless what landed on disk is exactly
    the payload it verified above.
    """
    actual = target.read_bytes()
    if actual != expected:
        raise SystemExit("read-back mismatch: output differs from payload")
    if len(actual) > MAX_BYTES:
        raise SystemExit("output exceeds 1 MiB")


def main() -> int:
    payload = locate_payload()
    data = confirm_jpeg(payload)
    target = place_copy(data)
    confirm_written(target, data)
    print(f"wrote {target} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
