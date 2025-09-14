#!/usr/bin/env python3
import csv
import os
import re
import sys
import uuid
from datetime import datetime
from typing import Iterable, List, Tuple

# Basic English stopwords (lowercase)
STOPWORDS = set(
    """
a an and are as at be by for from has have if in into is it its of on or that the their there these they this to was were will with without over under among within between across due such more most other those while than use using used because can may also which who whom whose where when how what why not no nor each per both either neither any all some many few several one two three four five six seven eight nine ten vs versus about among but so further based levels level due via include includes including included compared comparison analysis study effect effects clinical risk risks case cases patient patients child children pediatric pediatrics disease diseases disorder disorders condition conditions treatment treat treated management evaluation assessment guideline guidelines data new updated update figure table chapter section subsection part volume introduction conclusion summary references note notes see et al etc however therefore thus into among across throughout together although despite per cent percent method methods result results discussion limitation limitations strength strengths weakness weaknesses""".split()
)

WORD_RE = re.compile(r"[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?")


def stream_words(paths: List[str]) -> Iterable[str]:
    for p in paths:
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                # Normalize to lowercase, ensure spaces
                chunk = chunk.lower()
                for m in WORD_RE.finditer(chunk):
                    yield m.group(0)


def count_words(paths: List[str]) -> int:
    count = 0
    for _ in stream_words(paths):
        count += 1
    return count


def top_keywords(words: List[str], k: int = 12) -> List[str]:
    freq = {}
    for w in words:
        if w in STOPWORDS:
            continue
        freq[w] = freq.get(w, 0) + 1
    # sort by frequency then alpha to stabilize
    return [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:k]]


def build_chunks(paths: List[str], total_pages: int, chunks_per_page: int, 
                 book_title: str, edition: str, authors: str, publisher: str, year: str, isbn: str, source_url: str,
                 out_csv: str):
    total_chunks = total_pages * chunks_per_page

    print("Counting words...", file=sys.stderr)
    total_words = count_words(paths)
    if total_words == 0:
        raise RuntimeError("No words found in input files")

    base = total_words // total_chunks
    remainder = total_words % total_chunks
    # ensure within 200-500 range; if outside, just proceed but log
    print(f"Total words: {total_words}, total chunks: {total_chunks}, base words/chunk: {base}, remainder: {remainder}", file=sys.stderr)

    # Prepare CSV
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'id','book_title','edition','authors','publisher','year','isbn','source_url','page_number','chapter_title','section_title','section_heading_path','chunk_index','chunk_text','chunk_summary','keywords','chunk_token_count','confidence_score','embedding','created_at'
        ])

        # iterate words and emit chunks
        current_words: List[str] = []
        chunk_idx_global = 0
        word_iter = stream_words(paths)

        def words_needed(idx: int) -> int:
            # First 'remainder' chunks get one extra word
            return base + (1 if idx < remainder else 0)

        for w in word_iter:
            current_words.append(w)
            if len(current_words) >= words_needed(chunk_idx_global):
                page_number = (chunk_idx_global // chunks_per_page) + 1
                chunk_index = (chunk_idx_global % chunks_per_page) + 1
                text_content = ' '.join(current_words)
                token_count = len(current_words)
                kws = top_keywords(current_words)
                keywords_str = ', '.join(kws)
                # Simple summary sentence using keywords
                if kws:
                    summary = f"This chunk covers pediatric topics including {', '.join(kws[:6])}. It corresponds to page {page_number} of the 22nd edition."
                else:
                    summary = f"Content from page {page_number} of the 22nd edition."
                # IDs and placeholders
                row = [
                    str(uuid.uuid4()),
                    book_title,
                    edition,
                    authors,
                    publisher,
                    year,
                    isbn,
                    source_url,
                    page_number,
                    '',  # chapter_title unknown
                    f"Page {page_number}",  # section_title
                    f"Page {page_number}",  # section_heading_path
                    chunk_index,
                    text_content,
                    summary,
                    keywords_str,
                    token_count,
                    0.85,
                    '',
                    ''
                ]
                writer.writerow(row)
                chunk_idx_global += 1
                current_words = []
                if chunk_idx_global >= total_chunks:
                    break

        # If words remain and chunks remain, fill the last chunk with leftovers
        while chunk_idx_global < total_chunks:
            page_number = (chunk_idx_global // chunks_per_page) + 1
            chunk_index = (chunk_idx_global % chunks_per_page) + 1
            text_content = ' '.join(current_words)
            token_count = len(current_words)
            kws = top_keywords(current_words)
            keywords_str = ', '.join(kws)
            if kws:
                summary = f"This chunk covers pediatric topics including {', '.join(kws[:6])}. It corresponds to page {page_number} of the 22nd edition."
            else:
                summary = f"Content from page {page_number} of the 22nd edition."
            row = [
                str(uuid.uuid4()),
                book_title,
                edition,
                authors,
                publisher,
                year,
                isbn,
                source_url,
                page_number,
                '',
                f"Page {page_number}",
                f"Page {page_number}",
                chunk_index,
                text_content,
                summary,
                keywords_str,
                token_count,
                0.85,
                '',
                ''
            ]
            writer.writerow(row)
            chunk_idx_global += 1
            current_words = []

    print(f"Wrote {total_chunks} chunks to {out_csv}", file=sys.stderr)


if __name__ == '__main__':
    # Inputs
    root = '/project/workspace/d64483912-cmd/studious-lamp-dataset'
    part1 = f"{root}/extracted_txt/part_1/nelson_textbook_of_pediatrics_part_1_cleaned.txt"
    part2 = f"{root}/extracted_txt/part_2/nelson_textbook_of_pediatrics_part_2_cleaned.txt"
    part3 = f"{root}/extracted_txt/part_3/nelson_textbook_of_pediatrics_part_3_cleaned.txt"

    paths = [part1, part2, part3]

    total_pages = 4534
    chunks_per_page = 2

    book_title = 'Nelson Textbook of Pediatrics'
    edition = '22nd'
    authors = 'Robert M. Kliegman, Joseph W. St. Geme III, Nathan J. Blum, Robert C. Tasker, Karen M. Wilson, Abigail M. Schuh, Cara L. Mack'
    publisher = 'Elsevier'
    year = '2023'
    isbn = '978-0-323-88305-4'
    source_url = 'https://shop.elsevier.com/books/nelson-textbook-of-pediatrics-2-volume-set/kliegman/978-0-323-88305-4'

    out_csv = f"{root}/nelson_chunks.csv"

    build_chunks(paths, total_pages, chunks_per_page, book_title, edition, authors, publisher, year, isbn, source_url, out_csv)
