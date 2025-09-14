#!/usr/bin/env python3
import csv
import re
from typing import Dict, Tuple, Optional
from pypdf import PdfReader

PART_LINE_WITH_NUM = re.compile(r"^\s*(\d{1,4})\s+Part\s+([IVXLCDM]+)\s*[^A-Za-z0-9]?\s*(.+)$", re.IGNORECASE)
PART_ANYWHERE = re.compile(r"Part\s+([IVXLCDM]+)\s*[^A-Za-z0-9]?\s*(.+)$", re.IGNORECASE)
CHAPTER_LINE_TRAILNUM = re.compile(r"^\s*Chapter\s+(\d+)\s*[^A-Za-z0-9]?\s*(.+?)\s+(\d{1,4})\s*$", re.IGNORECASE)
CHAPTER_ANY = re.compile(r"Chapter\s+(\d+)\s*[^A-Za-z0-9]?\s*(.+)$", re.IGNORECASE)
LEADING_NUM = re.compile(r"^\s*(\d{1,4})\b")


def build_map(pdf_path: str, out_csv: str) -> None:
    reader = PdfReader(pdf_path)
    current_part: Tuple[Optional[str], Optional[str]] = (None, None)
    current_chapter: Tuple[Optional[str], Optional[str]] = (None, None)

    page_map: Dict[int, Dict[str, Optional[str]]] = {}

    for i, page in enumerate(reader.pages, start=1):
        t = (page.extract_text() or '')
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        book_page = None
        part = None
        part_title = None
        chapter_num = None
        chapter_title = None

        for ln in lines:
            m = PART_LINE_WITH_NUM.match(ln)
            if m:
                book_page = int(m.group(1))
                part = m.group(2)
                part_title = m.group(3)
                current_part = (part, part_title)
                break
        if book_page is None:
            # detect chapter line with trailing number (header form)
            for ln in lines:
                m = CHAPTER_LINE_TRAILNUM.match(ln)
                if m:
                    chapter_num = m.group(1)
                    chapter_title = m.group(2)
                    book_page = int(m.group(3))
                    current_chapter = (chapter_num, chapter_title)
                    break
        # fallback: leading number at line start
        if book_page is None:
            for ln in lines:
                m = LEADING_NUM.match(ln)
                if m:
                    book_page = int(m.group(1))
                    break
        # capture part/chapter context anywhere in page
        if part is None or part_title is None:
            for ln in lines:
                m = PART_ANYWHERE.search(ln)
                if m:
                    part = m.group(1)
                    part_title = m.group(2)
                    current_part = (part, part_title)
                    break
        if chapter_num is None or chapter_title is None:
            for ln in lines:
                m = CHAPTER_ANY.search(ln)
                if m:
                    chapter_num = m.group(1)
                    # avoid overly long titles by stripping trailing numbers
                    ch_title = re.sub(r"\s+\d{1,4}\s*$", "", m.group(2)).strip()
                    chapter_title = ch_title
                    current_chapter = (chapter_num, chapter_title)
                    break

        # use context from previous pages
        if part is None and part_title is None:
            part, part_title = current_part
        if chapter_num is None and chapter_title is None:
            chapter_num, chapter_title = current_chapter

        if book_page is None:
            # approximate by incrementing from previous if available
            if page_map:
                prev = max(page_map.keys())
                book_page = prev + 1
            else:
                # unknown at very beginning
                book_page = 0

        page_map[book_page] = {
            'pdf_page': i,
            'part_roman': part,
            'part_title': part_title,
            'chapter_number': chapter_num,
            'chapter_title': chapter_title,
        }

    # fill gaps if any
    if page_map:
        minp, maxp = min(page_map.keys()), max(page_map.keys())
        last = None
        for p in range(minp, maxp+1):
            if p in page_map:
                last = page_map[p]
            else:
                if last is None:
                    continue
                page_map[p] = dict(last)
                page_map[p]['pdf_page'] = None

    # write csv ordered by page
    rows = []
    for p in sorted(page_map.keys()):
        rows.append({
            'book_page': p,
            'pdf_page': page_map[p]['pdf_page'],
            'part_roman': page_map[p]['part_roman'],
            'part_title': page_map[p]['part_title'],
            'chapter_number': page_map[p]['chapter_number'],
            'chapter_title': page_map[p]['chapter_title'],
        })

    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['book_page','pdf_page','part_roman','part_title','chapter_number','chapter_title'])
        w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    pdf = '/project/workspace/d64483912-cmd/studious-lamp-dataset/source_pdfs/nelson-source-1.pdf'
    out = '/project/workspace/d64483912-cmd/studious-lamp-dataset/extracted_txt/normalized/page_heading_map.csv'
    build_map(pdf, out)
    print(out)
