import pandas as pd
import re
import json
import sys
import argparse
import csv
from typing import List, Dict, Any

# Configuration defaults (overridable via CLI)
INPUT_FILE = '/project/workspace/d64483912-cmd/Godzilla_dataset/embedded_dat/nelson_chunks_enhanced.csv'
OUTPUT_FILE = '/project/workspace/nelson_gpt_knowledge.csv'
BATCH_SIZE = 1000

COMMON_SUBTOPICS = [
    'clinical features', 'diagnosis', 'treatment', 'management', 'epidemiology',
    'complications', 'prevention', 'prognosis', 'pathogenesis', 'screening',
    'evaluation', 'therapy'
]

# ---------- Helper functions ----------

def _split_path(path: str) -> List[str]:
    if not path:
        return []
    cleaned = re.sub(r"\s*>\s*", " > ", str(path))
    parts = [p.strip() for p in cleaned.split('>') if p and p.strip()]
    return parts


def _clean_heading(text: str) -> str:
    if not text:
        return ''
    s = str(text).strip()
    s = re.sub(r'^Chapter\s+\d+:?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^Part\s+[IVXLCDM]+\s*u\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^Page\s+\d+\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^Section\s+\d+\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^u\s+', '', s)  # strip leading bullet-like 'u '
    s = re.sub(r'\s{2,}', ' ', s)
    s = s.strip(' :->\u00bb\u2013\u2014').strip()
    # Replace lone punctuation or very short artifacts with empty
    if re.fullmatch(r'[\W_]+', s) or len(s) <= 1:
        return ''
    return s


def extract_chapter(path: str) -> str:
    if not path:
        return 'General Pediatrics'
    part_match = re.search(r'Part\s+[IVXLCDM]+\s*u\s+(.+?)(?:\s*>|$)', path, flags=re.IGNORECASE)
    if part_match:
        return _clean_heading(part_match.group(1)) or 'General Pediatrics'
    chapter_match = re.search(r'Chapter\s+\d+:?\s+(.+?)(?:\s*>|$)', path, flags=re.IGNORECASE)
    if chapter_match:
        return _clean_heading(chapter_match.group(1)) or 'General Pediatrics'
    parts = _split_path(path)
    if parts:
        return _clean_heading(parts[0]) or 'General Pediatrics'
    return 'General Pediatrics'


def extract_section(path: str) -> str:
    parts = _split_path(path)
    if len(parts) >= 2:
        sec = _clean_heading(parts[1])
        if sec:
            return sec
    if parts:
        first = _clean_heading(parts[0])
        if first:
            return first
    return extract_chapter(path)


def _find_condition_in_text(text: str) -> str:
    if not text:
        return ''
    t = str(text)
    patterns = [
        r'([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){0,3})\s+(disease|syndrome|infection|pneumonia|asthma|diabetes|anemia|seizure|malaria|measles|hepatitis|meningitis|otitis|arthritis|abscess|encephalitis|nephritis|dermatitis|colitis|appendicitis)\b',
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b'
    ]
    for pat in patterns:
        m = re.search(pat, t)
        if m:
            if m.lastindex and m.lastindex >= 2:
                return (m.group(1) + ' ' + m.group(2)).strip()
            return m.group(1).strip()
    return ''


def extract_topic(path: str, chunk_text: str) -> str:
    parts = _split_path(path)
    if len(parts) >= 3:
        third = _clean_heading(parts[2])
        if third and third.lower() in COMMON_SUBTOPICS and len(parts) >= 2:
            cand = _clean_heading(parts[1])
            if cand:
                return cand
        if third:
            return third
    inferred = _find_condition_in_text(chunk_text)
    if inferred:
        return inferred
    return extract_section(path)


def extract_subtopic(path: str) -> str:
    parts = _split_path(path)
    if len(parts) >= 4:
        return _clean_heading(parts[3])
    if len(parts) >= 3:
        third = _clean_heading(parts[2]).lower()
        for c in COMMON_SUBTOPICS:
            if c in third:
                return c.title()
    return ''


def _strip_notices(text: str) -> str:
    if not text:
        return ''
    t = re.sub(r'downloaded\s+for.*?reserved', '', text, flags=re.IGNORECASE | re.DOTALL)
    t = re.sub(r'\(c\)\s*\d{4}.*?(rights reserved\.)?', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*\[[0-9,\s]+\]', '', t)
    t = re.sub(r'\s*\([Ff]ig\.?\s*\d+\)', '', t)
    t = re.sub(r'\s*\([Tt]able\s*\d+\)', '', t)
    return t


def is_front_matter(chunk_text: str, path: str, page_number: int) -> bool:
    if not chunk_text:
        return False
    text = (chunk_text or '').lower()
    path_l = (path or '').lower()
    if any(t in text for t in ['contributors', 'preface', 'acknowledg', 'dedication']) or any(t in path_l for t in ['contributors', 'preface', 'front matter']):
        return True
    deg_count = len(re.findall(r'\b(MD|M\.D\.|PhD|Ph\.D\.|MBBS|FAAP|FACS|MSCE|FRCP|FRACP|DO|MPH|MSc|MBA)\b', chunk_text))
    inst_count = sum(text.count(t) for t in ['university', 'school of medicine', 'hospital', 'department of', 'institute of'])
    clinical_terms = ['diagnosis','treatment','management','syndrome','disease','infection','patient','therapy','prognosis','signs','symptoms']
    clinical_signal = sum(text.count(t) for t in clinical_terms)
    if (deg_count >= 6 or inst_count >= 6) and clinical_signal <= 1 and page_number <= 50:
        return True
    if 'elsevier' in text and page_number <= 10:
        return True
    return False


def generate_summary(chunk_text: str) -> str:
    text = _strip_notices(chunk_text)
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return ''
    sentences = re.split(r'(?<=[.!?])\s+', text)
    clinical_terms = ['diagnosis', 'treatment', 'presents', 'caused by', 'characterized', 'symptoms', 'clinical', 'patient', 'disease', 'syndrome', 'management', 'therapy', 'prevention', 'prognosis']

    clinical_sentences: List[str] = []
    for sent in sentences[:12]:
        s = sent.strip()
        if len(s) < 25:
            continue
        if any(term in s.lower() for term in clinical_terms):
            clinical_sentences.append(s)
            if len(clinical_sentences) >= 2:
                break

    if not clinical_sentences:
        clinical_sentences = [s for s in sentences[:2] if len(s.strip()) > 0]

    summary = ' '.join(clinical_sentences[:2]).strip()
    words = summary.split()
    if len(words) > 150:
        summary = ' '.join(words[:150])
    if summary and summary[-1] not in '.!?':
        summary += '.'
    return summary


def map_category(medical_concepts_str: Any, chunk_text: str, chapter: str) -> str:
    category_mapping: Dict[str, List[str]] = {
        'Cardiology': ['heart', 'cardiac', 'cardiovascular'],
        'Infectious Diseases': ['infection', 'bacterial', 'viral', 'fever', 'sepsis', 'antimicrobial'],
        'Gastroenterology': ['liver', 'gastro', 'digestive', 'intestin', 'hepatic', 'biliary'],
        'Neurology': ['neuro', 'brain', 'seizure', 'epilep', 'mening', 'encephal'],
        'Pulmonology': ['lung', 'pulmonary', 'respiratory', 'asthma', 'bronch', 'pneumon'],
        'Nephrology': ['kidney', 'renal', 'urin', 'neph'],
        'Hematology': ['blood', 'anemia', 'hemato', 'thromb', 'sickle'],
        'Oncology': ['cancer', 'tumor', 'oncol', 'leukem', 'lymphom'],
        'Endocrinology': ['endocrin', 'diabetes', 'hormone', 'thyroid', 'adrenal'],
        'Growth and Development': ['growth', 'development', 'puberty'],
        'Dermatology': ['skin', 'dermat', 'rash', 'eczema'],
        'Immunology': ['immune', 'antibody', 'immunodef', 'allerg'],
        'Orthopedics': ['bone', 'fracture', 'orthoped', 'skeletal'],
        'Pharmacology': ['drug', 'medication', 'pharmac', 'dose'],
        'Nutrition': ['nutrition', 'feeding', 'diet', 'vitamin'],
        'Emergency Medicine': ['emergency', 'trauma', 'acute', 'resusc'],
        'Surgery': ['surgery', 'surgical', 'operative'],
        'Neonatology': ['newborn', 'neonat', 'premature']
    }

    concept_terms: List[str] = []
    try:
        if isinstance(medical_concepts_str, str):
            s = medical_concepts_str.strip()
            if s:
                try:
                    concepts = json.loads(s)
                except json.JSONDecodeError:
                    s2 = s.replace("'", '"')
                    concepts = json.loads(s2)
            else:
                concepts = {}
        elif isinstance(medical_concepts_str, dict):
            concepts = medical_concepts_str
        else:
            concepts = {}
        for v in concepts.values():
            if isinstance(v, list):
                concept_terms.extend([str(x) for x in v])
            elif isinstance(v, str):
                concept_terms.append(v)
    except Exception:
        concept_terms = []

    concept_text = ' '.join(concept_terms).lower()
    text_lower = str(chunk_text).lower()

    scores: Dict[str, int] = {}
    for category, keywords in category_mapping.items():
        text_score = sum(text_lower.count(kw) for kw in keywords)
        concept_score = sum(concept_text.count(kw) for kw in keywords)
        score = text_score + 2 * concept_score
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)

    return chapter or 'General Pediatrics'


def clean_keywords(keywords_str: Any) -> str:
    if keywords_str is None or (isinstance(keywords_str, float) and pd.isna(keywords_str)):
        return ''
    s = str(keywords_str)
    if not s.strip():
        return ''
    stopwords = {
        'professor', 'md', 'medicine', 'university', 'hospital', 'childrens',
        'center', 'college', 'director', 'associate', 'school', 'wisconsin',
        'pennsylvania', 'philadelphia', 'boston', 'california', 'massachusetts',
        'york', 'elsevier', 'textbook', 'his', 'chair', 'department', 'division',
        'editor', 'edition', 'authors', 'chapter', 'part', 'page', 'table', 'figure',
        'contributor', 'contributors', 'preface', 'acknowledgments', 'acknowledgements'
    }
    anatomy_terms = {
        'heart','liver','kidney','brain','lung','skin','bone','blood','intestine','stomach','pancreas','thyroid','adrenal','spleen'
    }
    med_pattern = re.compile(
        r'(itis|osis|emia|algia|pathy|opathy|oma|virus|bacter|fung|fungal|neuro|cardio|hepato|renal|pulmo|dermat|ortho|endocr|immun|gastro|hemat|oncol|sepsis|shock|fever|rash|seizure|asthma|pneumon|arthritis|abscess|colitis|nephritis|dermatitis|otitis|meningit|encephal|diabet|thyroid|adrenal|hormone|anemia|transplant|chemotherapy|antibiotic|antiviral|antifungal|vaccine|immunization|hypertension|hypotension)'
    )

    tokens = [kw.strip() for kw in s.split(',')]
    result: List[str] = []
    seen = set()
    for kw in tokens:
        if not kw:
            continue
        low = kw.lower()
        if low in stopwords:
            continue
        if len(low) < 3 and low not in {'hiv','hbv','hcv','iga','igg','ige'}:
            continue
        if any(ch.isdigit() for ch in low) and '-' not in low:
            if not re.search(r'(mg|mcg|mmhg|%|h1n1|h5n1|g6pd|b12)', low):
                continue
        if ' ' in low and not med_pattern.search(low) and low not in anatomy_terms:
            continue
        if not med_pattern.search(low) and low not in anatomy_terms:
            continue
        if low in seen:
            continue
        seen.add(low)
        result.append(kw)
        if len(result) >= 10:
            break
    return ','.join(result)


def _to_int(value: Any) -> int:
    try:
        if pd.isna(value):
            return 0
    except Exception:
        pass
    try:
        return int(value)
    except Exception:
        try:
            return int(float(str(value).strip()))
        except Exception:
            return 0


def process_row(row: pd.Series) -> Dict[str, Any]:
    try:
        path = str(row.get('section_heading_path', '') or '')
        chunk_text = str(row.get('chunk_text', '') or '')
        page_number = _to_int(row.get('page_number', 0))

        front = is_front_matter(chunk_text, path, page_number)

        chapter = extract_chapter(path)
        if front:
            section = 'Front Matter'
            topic = 'Contributors' if 'contributor' in chunk_text.lower() else 'Front Matter'
            subtopic = ''
            content_summary = 'Contributors and affiliations; non-clinical content.'
            category = 'General Pediatrics'
            keywords = ''
        else:
            section = extract_section(path) or chapter or 'General Pediatrics'
            topic = extract_topic(path, chunk_text) or section
            subtopic = extract_subtopic(path)
            content_summary = generate_summary(chunk_text) or (chunk_text[:150] + '.')
            category = map_category(row.get('medical_concepts', '{}'), chunk_text, chapter)
            keywords = clean_keywords(row.get('keywords', ''))

        return {
            'chapter': chapter,
            'section': section,
            'topic': topic,
            'subtopic': subtopic,
            'content_summary': content_summary,
            'page_number': page_number,
            'category': category,
            'keywords': keywords,
            'chunk_text': chunk_text
        }
    except Exception as e:
        print(f"Error processing row: {e}")
        return {
            'chapter': 'General Pediatrics',
            'section': '',
            'topic': '',
            'subtopic': '',
            'content_summary': (str(row.get('chunk_text', ''))[:150] + '.') if row is not None else '',
            'page_number': 0,
            'category': 'General Pediatrics',
            'keywords': '',
            'chunk_text': str(row.get('chunk_text', '') if row is not None else '')
        }


# ---------- Main processing ----------

def main():
    parser = argparse.ArgumentParser(description='Build nelson_gpt_knowledge.csv from enhanced chunks')
    parser.add_argument('--input', default=INPUT_FILE, help='Path to input CSV')
    parser.add_argument('--output', default=OUTPUT_FILE, help='Path to output CSV')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE, help='Batch size for chunked reading')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of rows processed (for testing)')
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    batch_size = max(1, int(args.batch_size))
    limit = args.limit if args.limit is None or args.limit > 0 else None

    print('Starting nelson_gpt_knowledge.csv generation...')
    print(f'Input: {input_file}')
    print(f'Output: {output_file}')
    print(f'Batch size: {batch_size}')
    if limit is not None:
        print(f'Row limit (testing): {limit}')

    output_rows: List[Dict[str, Any]] = []
    total_processed = 0

    try:
        for chunk_df in pd.read_csv(
            input_file,
            chunksize=batch_size,
            encoding='utf-8',
            quoting=csv.QUOTE_ALL,
            escapechar='\\',
            engine='python',
            on_bad_lines='warn'
        ):
            print(f"\nProcessing batch starting at row {total_processed}...")

            for _, row in chunk_df.iterrows():
                processed_row = process_row(row)
                output_rows.append(processed_row)
                total_processed += 1

                if total_processed % 100 == 0:
                    print(f'  Processed {total_processed} rows...')
                if limit is not None and total_processed >= limit:
                    break

            if limit is not None and total_processed >= limit:
                break

        print(f"\n\u2713 Total rows processed: {total_processed}")

        output_df = pd.DataFrame(output_rows, columns=[
            'chapter','section','topic','subtopic','content_summary','page_number','category','keywords','chunk_text'
        ])

        output_df['page_number'] = output_df['page_number'].astype(int)

        output_df.to_csv(output_file, index=False, encoding='utf-8', quoting=csv.QUOTE_MINIMAL)
        print(f"\u2713 Output written to: {output_file}")

        print("\n=== DATA QUALITY REPORT ===")
        total = len(output_df)
        print(f"Total rows: {total}")
        def pct(n):
            return f"{(n/total*100 if total else 0):.1f}%"
        non_empty_ch = output_df['chapter'].astype(str).str.strip().ne('').sum()
        non_empty_se = output_df['section'].astype(str).str.strip().ne('').sum()
        non_empty_to = output_df['topic'].astype(str).str.strip().ne('').sum()
        non_empty_su = output_df['content_summary'].astype(str).str.strip().ne('').sum()
        non_empty_kw = output_df['keywords'].fillna('').astype(str).str.strip().ne('').sum()
        print(f"Non-empty chapters: {non_empty_ch} ({pct(non_empty_ch)})")
        print(f"Non-empty sections: {non_empty_se} ({pct(non_empty_se)})")
        print(f"Non-empty topics: {non_empty_to} ({pct(non_empty_to)})")
        print(f"Non-empty summaries: {non_empty_su} ({pct(non_empty_su)})")
        print(f"Non-empty keywords: {non_empty_kw} ({pct(non_empty_kw)})")

        print("\nTop 5 categories:")
        try:
            print(output_df['category'].value_counts().head().to_string())
        except Exception:
            print('Category distribution unavailable')

        print("\nSample rows (first 3):")
        try:
            print(output_df.head(3).to_string())
        except Exception:
            print('Unable to print sample rows')

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
