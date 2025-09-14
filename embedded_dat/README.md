# Studious Lamp Dataset

This repository contains processing pipelines and combined datasets for medical AI research, including a unified "GODZILLA" medical dataset built from an enhanced Nelson pediatric corpus and a cleaned multi‑specialty medical documents corpus.

## Contents
- GODZILLA_DATASET_README.md — Dataset card for the unified GODZILLA dataset
- README_IMPROVEMENTS.md — Processing/enhancement overview and metrics
- NELSON_IMPROVEMENT_SUGGESTIONS.md — Roadmap for advanced enhancements
- scripts/ — Processing and enhancement scripts
  - process_medical_documents.py
  - enhance_nelson_dataset.py
  - other helpers for Nelson extraction/normalization
- create_godzilla_simple.py — Combines sources into `godzilla_medical_dataset.csv`
- processed_medical_documents.csv (+ stats)
- nelson_chunks_enhanced.csv (+ enhancement stats)
- godzilla_medical_dataset.csv (+ stats)

## GODZILLA dataset
See the dedicated dataset README for schema, statistics, and usage:
- GODZILLA_DATASET_README.md

## Reproducing datasets
1) Process medical documents (input depends on your source CSV):
```
python3 scripts/process_medical_documents.py input_raw.csv processed_medical_documents.csv
```
2) Enhance Nelson dataset (using your base Nelson chunks):
```
python3 scripts/enhance_nelson_dataset.py nelson_chunks.csv nelson_chunks_enhanced.csv
```
3) Build unified GODZILLA dataset:
```
python3 create_godzilla_simple.py
```
Outputs:
- godzilla_medical_dataset.csv
- godzilla_medical_dataset_stats.json

## Schema notes
- word_count: Number of words in `text` after truncation to 5,000 characters.
- chunk_token_count: Legacy length field carried from source datasets; in many cases equals word count. It is not a true tokenizer token count.
- godzilla_created_at: Unification timestamp added to each record when the GODZILLA dataset is generated.

## Repository structure (abridged)
```
.
├── README.md
├── GODZILLA_DATASET_README.md
├── README_IMPROVEMENTS.md
├── NELSON_IMPROVEMENT_SUGGESTIONS.md
├── create_godzilla_simple.py
├── scripts/
│   ├── process_medical_documents.py
│   ├── enhance_nelson_dataset.py
│   └── ...
├── processed_medical_documents.csv
├── processed_medical_documents_processing_stats.json
├── nelson_chunks_enhanced.csv
├── nelson_chunks_enhanced_enhancement_stats.json
├── godzilla_medical_dataset.csv
└── godzilla_medical_dataset_stats.json
```
