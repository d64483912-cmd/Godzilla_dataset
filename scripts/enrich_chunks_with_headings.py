#!/usr/bin/env python3
import csv
import os

root = '/project/workspace/d64483912-cmd/studious-lamp-dataset'
chunks_path = f'{root}/nelson_chunks.csv'
map_path = f'{root}/extracted_txt/normalized/page_heading_map.csv'
backup_path = f'{root}/nelson_chunks_original.csv'
out_path = f'{root}/nelson_chunks_enriched.csv'

# Load mapping: key by pdf_page
mapping = {}
with open(map_path, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        try:
            pdf_page = int(row['pdf_page'])
        except Exception:
            continue
        mapping[pdf_page] = {
            'part_roman': row.get('part_roman') or '',
            'part_title': row.get('part_title') or '',
            'chapter_number': row.get('chapter_number') or '',
            'chapter_title': row.get('chapter_title') or '',
        }

# Enrich chunks
with open(chunks_path, newline='', encoding='utf-8') as inp, open(out_path, 'w', newline='', encoding='utf-8') as out:
    r = csv.DictReader(inp)
    fieldnames = r.fieldnames
    w = csv.DictWriter(out, fieldnames=fieldnames)
    w.writeheader()
    for row in r:
        try:
            page = int(row['page_number'])
        except Exception:
            w.writerow(row)
            continue
        info = mapping.get(page, {})
        pr = info.get('part_roman','')
        pt = info.get('part_title','')
        cn = info.get('chapter_number','')
        ct = info.get('chapter_title','')
        # update titles when present
        if ct:
            row['chapter_title'] = ct
        if cn or ct:
            prefix = f"Chapter {cn}".strip()
            if ct:
                row['section_title'] = f"{prefix} — {ct}" if prefix else ct
            elif prefix:
                row['section_title'] = prefix
        # heading path
        path_parts = []
        if pr or pt:
            if pr and pt:
                path_parts.append(f"Part {pr}: {pt}")
            elif pt:
                path_parts.append(pt)
            elif pr:
                path_parts.append(f"Part {pr}")
        if cn or ct:
            if cn and ct:
                path_parts.append(f"Chapter {cn}: {ct}")
            elif ct:
                path_parts.append(ct)
            elif cn:
                path_parts.append(f"Chapter {cn}")
        # always end with page
        path_parts.append(f"Page {page}")
        row['section_heading_path'] = ' > '.join([p for p in path_parts if p])
        w.writerow(row)

# Move enriched over original (preserve backup)
if not os.path.exists(backup_path):
    os.replace(chunks_path, backup_path)
os.replace(out_path, chunks_path)
print(chunks_path)
