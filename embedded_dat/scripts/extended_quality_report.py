import pandas as pd
import re
from pathlib import Path
from collections import Counter

ROOT = Path('/project/workspace/d64483912-cmd/Godzilla_dataset/embedded_dat')
SRC = ROOT / 'nelson_gpt_knowledge.csv'
OUT_TXT = ROOT / 'extended_quality_report.txt'
OUT_CAT_CHAP = ROOT / 'category_vs_chapter.csv'
OUT_KEYWORDS = ROOT / 'keyword_vocab.csv'
OUT_NULLS = ROOT / 'null_patterns_by_chapter.csv'

# Load
df = pd.read_csv(SRC, dtype=str, keep_default_na=False)

# Normalize helper
def is_empty(v: str):
    return (not isinstance(v, str)) or (v.strip() == '')

# Keyword expansion
kw_series = df['keywords'].fillna('').astype(str)
all_kw = []
kw_counts = []
for s in kw_series:
    toks = [t.strip() for t in s.split(',') if t.strip()]
    kw_counts.append(len(toks))
    all_kw.extend(toks)

kw_freq = Counter(all_kw)
kw_df = pd.DataFrame({'keyword': list(kw_freq.keys()), 'count': list(kw_freq.values())})
kw_df.sort_values('count', ascending=False, inplace=True)

# Confusion matrix: chapter vs category
chap = df['chapter'].fillna('').astype(str)
cat = df['category'].fillna('').astype(str)
ct = pd.crosstab(chap, cat)
# Save full matrix
ct.to_csv(OUT_CAT_CHAP)

# Null patterns by chapter (top N chapters)
cols_check = ['topic','subtopic','content_summary','category','keywords']
agg = []
for ch, g in df.groupby('chapter'):
    n = len(g)
    rec = {'chapter': ch, 'rows': n}
    for c in cols_check:
        nonempty = g[c].replace('', pd.NA).notna().sum()
        rec[f'{c}_nonempty_pct'] = round(100.0*nonempty/n, 2)
    # avg summary length, avg keywords count
    rec['avg_summary_words'] = round(g['content_summary'].apply(lambda x: len(str(x).split()) if str(x).strip() else 0).mean(), 2)
    rec['avg_keywords'] = round(g['keywords'].apply(lambda x: len([t for t in str(x).split(',') if t.strip()]) ).mean(), 2)
    agg.append(rec)
nulls_df = pd.DataFrame(agg).sort_values('rows', ascending=False)
nulls_df.to_csv(OUT_NULLS, index=False)

# Generic terms analysis (potential stoplist additions)
GENERIC_CANDIDATES = set(['disease','disorders','treatment','management','diagnosis','medicine','clinical','medical','therapy','pain','symptoms'])
found_generic = {k:v for k,v in kw_freq.items() if k in GENERIC_CANDIDATES}

# Detect suspicious chapters
page_like = df['chapter'].str.match(r'^Page\s*\d+$', na=False)
page_like_count = int(page_like.sum())

# Top chapters and categories
top_chapters = df['chapter'].value_counts().head(30)
top_categories = df['category'].value_counts().head(30)

# Chapters with lowest subtopic fill rate (min 50 rows)
low_subtopic = nulls_df[nulls_df['rows']>=50].sort_values('subtopic_nonempty_pct').head(20)

# Build text report
lines = []
lines.append('Extended Quality Report for nelson_gpt_knowledge.csv\n')
lines.append(f'Total rows: {len(df)}')
lines.append('')

# Keyword stats
lines.append('Keyword Vocabulary Analysis:')
lines.append(f'- Unique keywords: {kw_df.shape[0]}')
lines.append(f'- Avg keywords per row: {sum(kw_counts)/len(kw_counts):.2f}')
lines.append(f'- Median keywords per row: {pd.Series(kw_counts).median():.0f}')
lines.append(f'- Rows with >=8 keywords: {(sum(1 for k in kw_counts if k>=8)/len(kw_counts))*100:.2f}%')
lines.append('- Top 50 keywords:')
for _, r in kw_df.head(50).iterrows():
    lines.append(f"  • {r['keyword']}: {int(r['count'])}")
lines.append('- Potentially generic keywords present and their counts:')
for k, v in sorted(found_generic.items(), key=lambda x: -x[1]):
    lines.append(f'  • {k}: {v}')
lines.append('')

# Confusion matrix summary
lines.append('Confusion Matrix (Category vs Chapter):')
lines.append(f'- Full matrix saved to: {OUT_CAT_CHAP}')
lines.append('- Top 15 chapters by rows:')
for ch, cnt in top_chapters.head(15).items():
    lines.append(f'  • {ch}: {cnt}')
lines.append('- Top 15 categories by rows:')
for ca, cnt in top_categories.head(15).items():
    lines.append(f'  • {ca if ca else "(empty)"}: {cnt}')
lines.append('')

# Null patterns by chapter
lines.append('Null/Fill Patterns by Chapter:')
lines.append(f'- Full table saved to: {OUT_NULLS}')
lines.append(f'- Chapters with lowest subtopic fill rate (>=50 rows):')
for _, r in low_subtopic.iterrows():
    lines.append(f"  • {r['chapter']}: rows={int(r['rows'])}, subtopic_nonempty={r['subtopic_nonempty_pct']}%")
lines.append('')

# Suspicious chapters
lines.append('Suspicious chapter labels:')
lines.append(f"- Rows with chapter like 'Page N': {page_like_count}")
if page_like_count>0:
    lines.append('  Suggest mapping early pages to the nearest section/chapter if available, or mark as Front Matter.')
lines.append('')

# Save report
with open(OUT_TXT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Wrote:', OUT_TXT, OUT_CAT_CHAP, OUT_KEYWORDS, OUT_NULLS)
