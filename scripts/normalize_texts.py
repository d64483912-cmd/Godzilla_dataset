#!/usr/bin/env python3
import argparse
import json
import os
import sys
import unicodedata
from typing import Dict, Any


def analyze(text: str) -> Dict[str, Any]:
    metrics = {
        "char_count": len(text),
        "line_count": text.count("\n") + 1 if text else 0,
        "cr_count": text.count("\r"),
        "ff_count": text.count("\f"),
        "has_bom": False,  # filled earlier
        "replacement_char_count": text.count("\uFFFD"),
        "trailing_ws_lines": 0,
        "empty_run_max": 0,
        "control_chars_count": 0,
    }
    # trailing whitespace
    trailing = 0
    empty_run_max = 0
    current_empty = 0
    for line in text.split("\n"):
        if line.endswith(" ") or line.endswith("\t"):
            trailing += 1
        if line.strip() == "":
            current_empty += 1
            if current_empty > empty_run_max:
                empty_run_max = current_empty
        else:
            current_empty = 0
    metrics["trailing_ws_lines"] = trailing
    metrics["empty_run_max"] = empty_run_max
    # count C0 control chars except tab/newline/carriage return/form feed
    controls = 0
    for ch in text:
        o = ord(ch)
        if o < 32 and ch not in ("\n", "\r", "\t", "\f"):
            controls += 1
    metrics["control_chars_count"] = controls
    return metrics


def clean_text(data: bytes) -> Dict[str, Any]:
    has_bom = data.startswith(b"\xef\xbb\xbf")
    if has_bom:
        data = data[3:]
    try:
        raw_text = data.decode("utf-8", errors="replace")
    except Exception:
        raw_text = data.decode("utf-8", errors="replace")

    pre_metrics = analyze(raw_text)
    pre_metrics["has_bom"] = has_bom

    text = raw_text
    applied = {"removed_bom": has_bom, "normalized_unicode_nfc": True, "cr_to_lf": False, "ff_to_newline": False, "stripped_trailing_ws": False, "collapsed_blank_lines": False, "removed_controls": False, "ensured_newline_eof": False}

    # Normalize Unicode
    text = unicodedata.normalize("NFC", text)

    # Normalize line endings: CRLF and CR -> LF
    if "\r" in text:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        applied["cr_to_lf"] = True

    # Replace form feed (page breaks) with single newline
    if "\f" in text:
        text = text.replace("\f", "\n")
        applied["ff_to_newline"] = True

    # Remove other C0 control characters except tab and newline
    before_len = len(text)
    text = "".join(ch for ch in text if not (ord(ch) < 32 and ch not in ("\n", "\t")))
    applied["removed_controls"] = (len(text) != before_len)

    # Strip trailing whitespace per line
    lines = text.split("\n")
    stripped_any = False
    for i, line in enumerate(lines):
        new_line = line.rstrip(" \t")
        if new_line != line:
            stripped_any = True
        lines[i] = new_line
    applied["stripped_trailing_ws"] = stripped_any

    # Collapse multiple blank lines to a single blank line, and trim leading/trailing blanks
    collapsed = []
    prev_blank = False
    for line in lines:
        is_blank = (line.strip() == "")
        if is_blank:
            if not prev_blank:
                collapsed.append("")
            prev_blank = True
        else:
            collapsed.append(line)
            prev_blank = False
    # Trim leading/trailing blank lines
    while collapsed and collapsed[0] == "":
        collapsed.pop(0)
    while collapsed and collapsed[-1] == "":
        collapsed.pop()
    applied["collapsed_blank_lines"] = (len(collapsed) != len(lines))

    cleaned = "\n".join(collapsed)

    # Ensure file ends with a single newline
    if not cleaned.endswith("\n"):
        cleaned = cleaned + "\n"
        applied["ensured_newline_eof"] = True

    post_metrics = analyze(cleaned)
    post_metrics["has_bom"] = False

    return {
        "applied": applied,
        "pre_metrics": pre_metrics,
        "post_metrics": post_metrics,
        "cleaned_text": cleaned,
    }


def main():
    p = argparse.ArgumentParser(description="Normalize and clean text files safely")
    p.add_argument("files", nargs="+", help="Input text files")
    p.add_argument("--outdir", required=True, help="Output directory for cleaned files")
    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    report = []
    for f in args.files:
        with open(f, "rb") as fh:
            data = fh.read()
        result = clean_text(data)
        out_path = os.path.join(args.outdir, os.path.basename(f).replace(".txt", "_normalized.txt"))
        with open(out_path, "w", encoding="utf-8", newline="\n") as oh:
            oh.write(result["cleaned_text"])
        entry = {
            "input": f,
            "output": out_path,
            "applied": result["applied"],
            "pre_metrics": result["pre_metrics"],
            "post_metrics": result["post_metrics"],
        }
        report.append(entry)

    # write report next to outputs
    report_path = os.path.join(args.outdir, "clean_report.json")
    with open(report_path, "w", encoding="utf-8") as rh:
        json.dump(report, rh, indent=2, ensure_ascii=False)

    print(report_path)


if __name__ == "__main__":
    sys.exit(main())
