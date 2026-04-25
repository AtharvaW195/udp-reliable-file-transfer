#!/usr/bin/env python3
"""Compare two files byte-by-byte for transfer verification."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two files")
    parser.add_argument("file_a")
    parser.add_argument("file_b")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path_a = Path(args.file_a)
    path_b = Path(args.file_b)

    data_a = path_a.read_bytes()
    data_b = path_b.read_bytes()

    if data_a == data_b:
        print("MATCH")
        return

    print("DIFFER")
    print(f"Size A = {len(data_a)}, Size B = {len(data_b)}")


if __name__ == "__main__":
    main()
