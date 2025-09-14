#!/usr/bin/env python3
import argparse
import json
import os
from typing import Any, Dict
from pypdf import PdfReader


def check_pdf(path: str, sample_pages: int = 2, sample_lines: int = 40) -> Dict[str, Any]:
    size_bytes = os.path.getsize(path)
    res: Dict[str, Any] = {
        "path": path,
        "size_bytes": size_bytes,
        "page_count": None,
        "metadata": {},
        "text_extractable": False,
        "sample_text": "",
    }
    reader = PdfReader(path)
    res["page_count"] = len(reader.pages)
    meta = reader.metadata or {}
    # Pdf metadata keys like '/Title' map to attributes like title in pypdf
    cleaned_meta = {}
    for k, v in meta.items():
        try:
            cleaned_meta[str(k).lstrip('/')] = str(v)
        except Exception:
            cleaned_meta[str(k).lstrip('/')] = repr(v)
    res["metadata"] = cleaned_meta

    # Extract sample text
    sample_chunks = []
    pages_to_try = min(sample_pages, len(reader.pages))
    for i in range(pages_to_try):
        try:
            t = reader.pages[i].extract_text() or ""
        except Exception:
            t = ""
        sample_chunks.append(t)
    sample_text = "\n".join(sample_chunks)
    # Normalize line endings
    sample_text = sample_text.replace("\r\n", "\n").replace("\r", "\n")
    # Keep first N lines
    if sample_text:
        lines = sample_text.split("\n")
        sample_text = "\n".join(lines[:sample_lines]).strip()
    res["sample_text"] = sample_text
    res["text_extractable"] = len(sample_text.strip()) > 0
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="Path to the PDF file")
    ap.add_argument("--out-json", help="Where to write JSON report", required=True)
    ap.add_argument("--sample-out", help="Where to write sample text", required=True)
    args = ap.parse_args()

    report = check_pdf(args.pdf)
    os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    os.makedirs(os.path.dirname(args.sample_out), exist_ok=True)
    with open(args.sample_out, "w", encoding="utf-8") as f:
        f.write(report.get("sample_text", ""))

    print(args.out_json)


if __name__ == "__main__":
    main()
