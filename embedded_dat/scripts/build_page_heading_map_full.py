#!/usr/bin/env python3
import csv
import re
from pypdf import PdfReader

PDF = '/project/workspace/d64483912-cmd/studious-lamp-dataset/source_pdfs/nelson-source-1.pdf'
OUT = '/project/workspace/d64483912-cmd/studious-lamp-dataset/extracted_txt/normalized/page_heading_map.csv'

PART_LINE_WITH_NUM = re.compile(r"^\s*(\d{1,4})\s+Part\s+([IVX]+)\s*[^A-Za-z0-9]?\s*(.+)$", re.IGNORECASE)
CHAPTER_LINE_TRAILNUM = re.compile(r"^\s*Chapter\s+(\d+)\s*[^A-Za-z0-9]?\s*(.+?)\s+(\d{1,4})\s*$", re.IGNORECASE)
PART_ANY = re.compile(r"\bPart\s+([IVX]+)\s*[^A-Za-z0-9]?\s*(.+)$", re.IGNORECASE)
CHAPTER_ANY = re.compile(r"\bChapter\s+(\d+)\s*[^A-Za-z0-9]?\s*(.+)$", re.IGNORECASE)
TRAILING_PAGE = re.compile(r"(\d{1,4})\s*$")

reader = PdfReader(PDF)
current_part = (None, None)
current_chapter = (None, None)
last_book_page = None

with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['book_page','pdf_page','part_roman','part_title','chapter_number','chapter_title'])
    w.writeheader()
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or '')
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        book_page = None
        part = None; part_title = None
        chapter_num = None; chapter_title = None

        # strict header patterns
        for ln in lines:
            m = PART_LINE_WITH_NUM.match(ln)
            if m:
                book_page = int(m.group(1))
                part = m.group(2)
                part_title = m.group(3)
                current_part = (part, part_title)
                break
        if book_page is None:
            for ln in lines:
                m = CHAPTER_LINE_TRAILNUM.match(ln)
                if m:
                    chapter_num = m.group(1)
                    chapter_title = re.sub(r"\s+\d{1,4}\s*$", "", m.group(2)).strip()
                    book_page = int(m.group(3))
                    current_chapter = (chapter_num, chapter_title)
                    break
        # update context anywhere on page (does not set page number)
        if part is None or part_title is None:
            for ln in lines:
                m = PART_ANY.search(ln)
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
                    chapter_title = re.sub(r"\s+\d{1,4}\s*$", "", m.group(2)).strip()
                    current_chapter = (chapter_num, chapter_title)
                    break

        # inherit context
        if part is None and part_title is None:
            part, part_title = current_part
        if chapter_num is None and chapter_title is None:
            chapter_num, chapter_title = current_chapter

        # fall back for page number: increment previous if known
        if book_page is None:
            if last_book_page is not None:
                book_page = last_book_page + 1
            else:
                book_page = 0
        last_book_page = book_page

        w.writerow({
            'book_page': book_page,
            'pdf_page': i,
            'part_roman': part,
            'part_title': part_title,
            'chapter_number': chapter_num,
            'chapter_title': chapter_title,
        })

print(OUT)
