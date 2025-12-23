"""Helpers to prepare OpenAI fine-tune datasets and example commands.

This script DOES NOT call the OpenAI API. It formats training examples
into the JSONL structure expected by hosted fine-tune endpoints and
prints example CLI commands the operator can run with their keys.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def format_pair(prompt: str, completion: str) -> dict:
    return {"prompt": prompt, "completion": completion}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="infile", required=True)
    p.add_argument("--out", dest="outfile", required=True)
    args = p.parse_args()

    src = Path(args.infile)
    dst = Path(args.outfile)
    items = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        # Expect tab-separated prompt \t completion
        if "\t" not in line:
            continue
        pr, co = line.split("\t", 1)
        items.append(format_pair(pr, co))

    with dst.open("w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")

    print("Wrote", dst)
    print()
    print("Example openai CLI: ")
    print("openai api fine_tunes.create -t {} -m <base-model>".format(dst))


if __name__ == "__main__":
    main()
