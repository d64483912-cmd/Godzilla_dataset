import pandas as pd
import re
import json
from collections import defaultdict
from pathlib import Path

SRC = Path('/project/workspace/d64483912-cmd/Godzilla_dataset/embedded_dat/nelson_chunks_enhanced.csv')
OUT_DIR = Path('/project/workspace/d64483912-cmd/Godzilla_dataset/embedded_dat')
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_CSV = OUT_DIR / 'nelson_gpt_knowledge.csv'
REPORT = OUT_DIR / 'data_quality_report.txt'

RE_PART = re.compile(r'^\s*Part\s+[IVXLCDM]+\s*[:\-–—]?\s*(?:u\s*)?(.+?)\s*$', re.IGNORECASE)
RE_CHAPTER = re.compile(r'^\s*Chapter\s+(\d+)\s*[—\-:]*\s*(.*)$', re.IGNORECASE)
RE_PAGE = re.compile(r'^\s*Page\s*\d+\s*$', re.IGNORECASE)

CATEGORY_KEYWORDS = {
    'Cardiology': {'cardiac','heart','cardiovascular','arrhythmia','endocarditis','cyanotic','murmur','congenital heart','cardiomyopathy','hypertension'},
    'Growth': {'growth','stature','height','weight','z-score','anthropometry'},
    'Development': {'development','milestone','language development','behavior','neurodevelopment'},
    'Infectious Diseases': {'infection','infectious','bacterial','viral','fever','sepsis','meningitis','pneumonia','mycobacterium','tuberculosis','malaria','hiv','influenza','candida','plague','anthrax','tularemia','smallpox','mpox','ebola','rsv','measles','rubella','mumps'},
    'Gastroenterology': {'gastro','liver','hepatic','biliary','hepatitis','bowel','intestine','malabsorption','celiac','ulcer','diarrhea','vomiting'},
    'Neurology': {'neurology','seizure','epilepsy','cerebral','brain','neuromuscular','encephalitis','cerebellar','headache','stroke','dystonia'},
    'Pulmonology': {'lung','pulmonary','asthma','bronchial','respiratory','bronchiolitis','bronchopulmonary','hypoxemia'},
    'Nephrology': {'kidney','renal','nephro','hematuria','proteinuria','glomerular','tubular'},
    'Hematology': {'anemia','hemoglobin','hemostasis','bleeding','hematologic','hemophilia','vwd','leukemia'},
    'Oncology': {'oncology','tumor','cancer','malignancy','sarcoma','lymphoma','neoplasm'},
    'Endocrinology': {'endocrine','thyroid','adrenal','pituitary','diabetes','insulin','puberty','precocity'},
    'Genetics': {'genetic','chromosome','trisomy','genomic','dysmorph','inherit'},
    'Dermatology': {'skin','derm','eczema','dermatitis','rash','lesion'},
    'Immunology': {'immunology','immune','immunodeficiency','antibody','t-cell','b-cell'},
    'Rheumatology': {'arthritis','lupus','vasculitis','rheumatic','autoimmune'},
    'Orthopedics': {'fracture','orthopedic','bone','scoliosis','osteomyelitis'},
    'Pharmacology': {'drug','dose','dosing','pharmacology','toxicology','toxicity','antibiotic','analgesic'},
    'Nutrition': {'nutrition','nutritional','diet','feeding','vitamin','micronutrient'},
    'Emergency Medicine': {'emergency','resuscitation','shock','trauma','toxicant','poisoning','antidote'},
    'Surgery': {'surgery','operative','postoperative','appendicitis','hernia','procedure'},
    'Neonatology': {'neonate','newborn','premature','nicu','apnea','meconium'}
}

STOPWORDS = set('''professor md medicine university hospital childrens children child center centre division department college school associate assistant director chair wisconsin pennsylvania philadelphia boston california ohio colorado chicago new york north carolina washington texas florida alabama indiana illinois michigan arizona oregon utah maryland massachusetts york los angeles seattle denver cincinnati aurora milwaukee philadelphia pennsylvania program research study studies clinic medical health science sciences faculty emeritus chief fellow fellowship adjunct faculty of at and the a an for in on with by from to as jr sr phd mph ms msc do mbbs mbbchir facs faap frcp frcpc frcog fsar msce mscs msp mhs mba mdphd mscphd'''.split())

NON_MED_GENERIC = {
    'medicine','medical','professor','university','hospital','department','division','center','associate','assistant','director','college','school','program','research','study','studies','clinic','health','science','sciences','chair','emeritus','fellow','fellowship','adjunct'
}

CLINICAL_HINTS = [
    'presents with','characterized by','features include','symptoms include','diagnosed by','diagnosis','management','treatment','therapy','indications','contraindications','risk factors','prognosis','complications','caused by','most common','evaluation','screening','prevention'
]

SENT_SPLIT = re.compile(r'(?<=[\.!?])\s+')


def parse_heading_path(path_str: str):
    result = {'chapter': '', 'section': '', 'topic': '', 'subtopic': ''}
    if not isinstance(path_str, str) or not path_str.strip():
        return result
    parts = [p.strip() for p in path_str.split('>') if p.strip()]
    parts = [p for p in parts if not RE_PAGE.match(p)]
    part_title = ''
    chapter_title = ''
    rest = []
    for p in parts:
        mpart = RE_PART.match(p)
        if mpart:
            part_title = mpart.group(1).strip()
            continue
        mchap = RE_CHAPTER.match(p)
        if mchap:
            cand = (mchap.group(2) or '').strip()
            cand = re.sub(r'^u\s+', '', cand).strip()
            chapter_title = cand
            continue
        rest.append(p)
    chap = part_title or chapter_title
    chap = re.sub(r'^u\s+', '', chap).strip()
    result['chapter'] = chap
    if part_title and chapter_title:
        result['section'] = chapter_title
    elif chapter_title:
        result['section'] = chapter_title
    elif part_title:
        result['section'] = part_title
    clean_rest = [re.sub(r'^(Section:|u)\s*', '', r, flags=re.IGNORECASE).strip() for r in rest]
    clean_rest = [r for r in clean_rest if r and r != chapter_title and r != part_title]
    if clean_rest:
        result['topic'] = clean_rest[0]
    if len(clean_rest) > 1:
        result['subtopic'] = clean_rest[1]
    return result


def pick_topic_from_text(text: str, keywords: str):
    if isinstance(keywords, str) and keywords:
        keys = [k.strip() for k in keywords.split(',') if k.strip()]
    else:
        keys = []
    text_l = text.lower() if isinstance(text, str) else ''
    for k in keys:
        kl = k.lower()
        if kl in text_l and kl not in STOPWORDS and kl not in NON_MED_GENERIC and len(kl) > 2:
            return k
    m = re.search(r'(?:[A-Z][a-z]+\s)+(?:[A-Z][a-z]+)', text or '')
    if m:
        return m.group(0).strip()
    return ' '.join((text or '').strip().split()[:3])


def generate_summary(chunk_text: str, learning_obj: str):
    if not isinstance(chunk_text, str) or not chunk_text.strip():
        return ''
    sentences = SENT_SPLIT.split(chunk_text.strip())
    def score(s):
        s_l = s.lower()
        score = 0
        for h in CLINICAL_HINTS:
            if h in s_l:
                score += 3
        if re.search(r'\b(fever|pain|cough|diagnos|treat|manage|therapy|antibiotic|ultrasound|imaging|labs?|criteria|presents)\b', s_l):
            score += 2
        words = len(s.split())
        if 8 <= words <= 35:
            score += 1
        return score
    ranked = sorted(sentences, key=score, reverse=True)
    if ranked:
        first = ranked[0]
        second = ''
        for s in ranked[1:]:
            if s != first and len((first + ' ' + s).split()) <= 60:
                second = s
                break
        summary = (first.strip() + (' ' + second.strip() if second else '')).strip()
        words = summary.split()
        if len(words) > 150:
            summary = ' '.join(words[:150]).rstrip(',;') + '.'
        return summary
    return ' '.join(sentences[:2])[:800]


def map_category(med_concepts_raw: str, chunk_text: str, chapter_name: str):
    scores = defaultdict(int)
    chap_l = (chapter_name or '').lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in chap_l:
                scores[cat] += 2
    if isinstance(med_concepts_raw, str) and med_concepts_raw.strip():
        try:
            mc = json.loads(med_concepts_raw)
            if isinstance(mc, dict):
                for arr in mc.values():
                    if isinstance(arr, list):
                        for term in arr:
                            tl = str(term).lower()
                            for cat, kws in CATEGORY_KEYWORDS.items():
                                for kw in kws:
                                    if kw in tl:
                                        scores[cat] += 3
        except Exception:
            pass
    text_l = (chunk_text or '').lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if re.search(r'\b'+re.escape(kw)+r'\b', text_l):
                scores[cat] += 1
    if not scores:
        fallback_map = {
            'digestive': 'Gastroenterology',
            'cardio': 'Cardiology',
            'infect': 'Infectious Diseases',
            'respir': 'Pulmonology',
            'lung': 'Pulmonology',
            'kidney': 'Nephrology',
            'renal': 'Nephrology',
            'growth': 'Growth',
            'develop': 'Development',
        }
        for k, v in fallback_map.items():
            if k in chap_l:
                return v
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return ''


def clean_keywords(kw_raw: str):
    if not isinstance(kw_raw, str) or not kw_raw.strip():
        return ''
    toks = [t.strip() for t in kw_raw.split(',')]
    clean = []
    seen = set()
    for t in toks:
        tl = t.lower()
        tl = re.sub(r'[^a-z0-9 \-\/\(\)]+', '', tl)
        tl = tl.strip()
        if not tl or tl in STOPWORDS or tl in NON_MED_GENERIC:
            continue
        if len(tl) <= 2:
            continue
        if re.search(r'(itis|osis|emia|oma|pathy|algia|ectomy|virus|bacteria|fever|anemia|ulcer|asthma|hepat|nephro|cardio|neuro|derma|renal|liver|lung|heart|bone|fracture|syndrome|disease|infection|sepsis|shock|cyanosis|diarrhea|vomit|cough|rash|endocarditis|meningitis|pneum|arthritis|diabetes|thyroid|hormone|antibiotic|vaccine|immun)', tl) or ' ' in tl or '-' in tl:
            if tl not in seen:
                seen.add(tl)
                clean.append(tl)
    clean = clean[:10]
    return ','.join(clean)


def build_keywords_from_sources(keywords_raw: str, med_concepts_raw: str, chunk_text: str, section_fields: list[str]):
    # start from cleaned provided keywords
    base = clean_keywords(keywords_raw)
    terms = []
    if base:
        terms.extend(base.split(','))
    # supplement from medical_concepts JSON
    try:
        mc = json.loads(med_concepts_raw) if isinstance(med_concepts_raw, str) and med_concepts_raw else {}
        if isinstance(mc, dict):
            for arr in mc.values():
                if isinstance(arr, list):
                    for t in arr:
                        t = str(t).lower().strip()
                        t = re.sub(r'[^a-z0-9 \-\/\(\)]+', '', t)
                        if len(t) > 2:
                            terms.append(t)
    except Exception:
        pass
    # supplement from text by extracting medical-like words
    text = ' '.join([s for s in section_fields if isinstance(s, str)]) + ' ' + (chunk_text or '')
    cand = re.findall(r'\b([a-zA-Z][a-zA-Z\-]{3,})\b', text)
    for w in cand:
        wl = w.lower()
        if wl in STOPWORDS or wl in NON_MED_GENERIC:
            continue
        if re.search(r'(itis|osis|emia|oma|pathy|ectomy|virus|bacteria|fever|anemia|ulcer|asthma|hepat|nephro|cardio|neuro|derma|renal|liver|lung|heart|bone|fracture|syndrome|disease|infection|sepsis|shock|cyanosis|diarrhea|vomit|cough|rash|endocarditis|meningitis|pneum|arthritis|diabetes|thyroid|hormone|antibiotic|vaccine|immun)', wl):
            terms.append(wl)
    # dedupe and limit
    out = []
    seen = set()
    for t in terms:
        t = t.strip()
        if not t:
            continue
        if t in STOPWORDS or t in NON_MED_GENERIC:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
        if len(out) >= 10:
            break
    return ','.join(out)


def first_nonempty(*vals):
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ''


def main():
    try:
        df = pd.read_csv(SRC, dtype=str, keep_default_na=False)
    except Exception:
        df = pd.read_csv(SRC, dtype=str, keep_default_na=False, engine='python')

    out_rows = []
    for idx, row in df.iterrows():
        shp = row.get('section_heading_path', '')
        parsed = parse_heading_path(shp)
        chapter = parsed.get('chapter','').strip()
        section = parsed.get('section','').strip()
        topic = parsed.get('topic','').strip()
        subtopic = parsed.get('subtopic','').strip()

        if not chapter:
            chapter = first_nonempty(row.get('chapter_title',''), row.get('section_title',''))
        if not section:
            section = first_nonempty(row.get('section_title',''), chapter)

        chunk_text = row.get('chunk_text','')
        keywords_raw = row.get('keywords','')
        med_concepts = row.get('medical_concepts','')
        learning_obj = row.get('learning_objectives','')

        if not topic:
            topic = pick_topic_from_text(chunk_text, keywords_raw)
        if not subtopic:
            lower = chunk_text.lower() if isinstance(chunk_text, str) else ''
            for cand in ['Clinical Features','Diagnosis','Treatment','Management','Epidemiology','Pathophysiology','Complications','Prognosis','Prevention']:
                if cand.lower().split()[0] in lower:
                    subtopic = cand
                    break
            if not subtopic:
                chap_l = (chapter or '').lower()
                if any(k in chap_l for k in ['growth','develop','nutrition']):
                    for pref in ['Assessment','Evaluation','Management']:
                        if pref.lower() in lower:
                            subtopic = pref
                            break
                    if not subtopic:
                        subtopic = 'Assessment'

        content_summary = generate_summary(chunk_text, learning_obj)

        pn = row.get('page_number','')
        try:
            pn_int = int(float(str(pn).strip())) if str(pn).strip() else ''
        except Exception:
            pn_int = ''

        category = map_category(med_concepts, chunk_text, chapter)
        cleaned_kw = clean_keywords(keywords_raw)
        if not cleaned_kw:
            cleaned_kw = build_keywords_from_sources(keywords_raw, med_concepts, chunk_text, [chapter, section, topic, subtopic])

        out_rows.append({
            'chapter': chapter,
            'section': section,
            'topic': topic,
            'subtopic': subtopic,
            'content_summary': content_summary,
            'page_number': pn_int,
            'category': category,
            'keywords': cleaned_kw,
            'chunk_text': chunk_text or ''
        })

    out_df = pd.DataFrame(out_rows, columns=['chapter','section','topic','subtopic','content_summary','page_number','category','keywords','chunk_text'])
    out_df.to_csv(OUT_CSV, index=False)

    report_lines = []
    report_lines.append('Nelson-GPT Knowledge Data Quality Report\n')
    report_lines.append(f'Total rows: {len(out_df)}')
    report_lines.append('\nField population percentages:')
    for col in ['chapter','section','topic','subtopic','content_summary','page_number','category','keywords','chunk_text']:
        nonempty = out_df[col].replace('', pd.NA).notna().sum()
        pct = (nonempty / len(out_df))*100 if len(out_df) else 0
        report_lines.append(f'- {col}: {pct:.2f}% non-empty')

    report_lines.append('\nCategory distribution (top 20):')
    cat_counts = out_df['category'].value_counts(dropna=False).head(20)
    for k, v in cat_counts.items():
        report_lines.append(f'- {k if k else "(empty)"}: {v}')

    def sample_block(title, indices):
        lines = ['\n' + title]
        for i in indices:
            if 0 <= i < len(out_df):
                r = out_df.iloc[i]
                lines.append(f"[{i}] chapter={r['chapter']} | section={r['section']} | topic={r['topic']} | subtopic={r['subtopic']} | page={r['page_number']} | category={r['category']} | keywords={r['keywords']}\nsummary: {r['content_summary'][:300]}\n")
        return lines

    report_lines += sample_block('First 10 rows', list(range(10)))
    mid_start = max(0, len(out_df)//2 - 5)
    report_lines += sample_block('Middle 10 rows', list(range(mid_start, mid_start+10)))
    report_lines += sample_block('Last 10 rows', list(range(max(0, len(out_df)-10), len(out_df))))

    report_lines.append('\nValidations:')
    report_lines.append(f"- schema_columns: {list(out_df.columns)}")
    report_lines.append(f"- rows_match_source: {len(out_df) == len(pd.read_csv(SRC, dtype=str, keep_default_na=False))}")

    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print('Done. Wrote:', OUT_CSV, REPORT)


if __name__ == '__main__':
    main()
