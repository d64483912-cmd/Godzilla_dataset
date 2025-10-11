#!/usr/bin/env python3
"""
Godzilla JSONL Dataset Analysis
Provides detailed statistics and insights about the JSONL medical dataset
"""

import json
import pandas as pd
from collections import Counter
import numpy as np

def analyze_jsonl_dataset(jsonl_file_path):
    """Analyze the JSONL dataset and provide comprehensive statistics"""
    
    print("🦖 GODZILLA MEDICAL DATASET - JSONL ANALYSIS")
    print("=" * 80)
    
    # Load all records
    records = []
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line.strip()))
    
    df = pd.DataFrame(records)
    
    print(f"📊 DATASET OVERVIEW")
    print(f"   Total Records: {len(records):,}")
    print(f"   Total Fields: {len(df.columns)}")
    print(f"   Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
    
    print(f"\n📋 SOURCE DISTRIBUTION")
    source_counts = df['source_dataset'].value_counts()
    for source, count in source_counts.items():
        percentage = (count / len(records)) * 100
        print(f"   {source}: {count:,} records ({percentage:.1f}%)")
    
    print(f"\n🏥 MEDICAL SPECIALTIES (Top 15)")
    specialty_counts = df['medical_specialty'].value_counts().head(15)
    for specialty, count in specialty_counts.items():
        percentage = (count / len(records)) * 100
        print(f"   {specialty}: {count:,} records ({percentage:.1f}%)")
    
    print(f"\n📈 QUALITY METRICS")
    confidence_scores = df['confidence_score'].astype(float)
    print(f"   Average Confidence: {confidence_scores.mean():.3f}")
    print(f"   Median Confidence: {confidence_scores.median():.3f}")
    print(f"   Min Confidence: {confidence_scores.min():.3f}")
    print(f"   Max Confidence: {confidence_scores.max():.3f}")
    
    high_quality = len(df[df['confidence_score'] >= 0.8])
    print(f"   High Quality (≥0.8): {high_quality:,} ({high_quality/len(records)*100:.1f}%)")
    
    print(f"\n📝 TEXT ANALYTICS")
    text_lengths = df['text_length'].astype(int)
    word_counts = df['word_count_calculated'].astype(int)
    
    print(f"   Average Text Length: {text_lengths.mean():.0f} characters")
    print(f"   Median Text Length: {text_lengths.median():.0f} characters")
    print(f"   Average Word Count: {word_counts.mean():.0f} words")
    print(f"   Median Word Count: {word_counts.median():.0f} words")
    
    # Text length distribution
    short_texts = len(df[df['text_length'] < 1000])
    medium_texts = len(df[(df['text_length'] >= 1000) & (df['text_length'] < 3000)])
    long_texts = len(df[df['text_length'] >= 3000])
    
    print(f"   Short texts (<1K chars): {short_texts:,} ({short_texts/len(records)*100:.1f}%)")
    print(f"   Medium texts (1K-3K chars): {medium_texts:,} ({medium_texts/len(records)*100:.1f}%)")
    print(f"   Long texts (≥3K chars): {long_texts:,} ({long_texts/len(records)*100:.1f}%)")
    
    print(f"\n🎯 TRAINING CATEGORIES")
    training_cats = df['training_category'].value_counts().head(10)
    for category, count in training_cats.items():
        percentage = (count / len(records)) * 100
        print(f"   {category}: {count:,} records ({percentage:.1f}%)")
    
    print(f"\n📚 READING DIFFICULTY")
    difficulty_counts = df['reading_difficulty'].value_counts()
    for difficulty, count in difficulty_counts.items():
        percentage = (count / len(records)) * 100
        print(f"   {difficulty}: {count:,} records ({percentage:.1f}%)")
    
    print(f"\n👥 AGE GROUPS")
    age_groups = df['age_groups'].value_counts()
    for age_group, count in age_groups.items():
        percentage = (count / len(records)) * 100
        print(f"   {age_group}: {count:,} records ({percentage:.1f}%)")
    
    print(f"\n🔍 TOP KEYWORDS")
    all_keywords = []
    for keywords_list in df['keywords']:
        if isinstance(keywords_list, list):
            all_keywords.extend(keywords_list)
    
    keyword_counts = Counter(all_keywords)
    print(f"   Total Unique Keywords: {len(keyword_counts):,}")
    print(f"   Top 15 Keywords:")
    for keyword, count in keyword_counts.most_common(15):
        print(f"     '{keyword}': {count:,} occurrences")
    
    print(f"\n📖 SOURCE FILES (Top 10)")
    source_files = df['source_file'].value_counts().head(10)
    for source_file, count in source_files.items():
        percentage = (count / len(records)) * 100
        print(f"   {source_file}: {count:,} records ({percentage:.1f}%)")
    
    print(f"\n⭐ RECOMMENDATIONS FOR ML TRAINING")
    print(f"   • Use confidence_score ≥ 0.8 for high-quality training ({high_quality:,} records)")
    print(f"   • Filter by medical_specialty for specialized models")
    print(f"   • Use keywords array for multi-label classification")
    print(f"   • Consider text_length for batch sizing (avg: {text_lengths.mean():.0f} chars)")
    print(f"   • Pediatrics dominance (96.4%) - consider for domain adaptation")
    
    return df

if __name__ == "__main__":
    # Analyze the JSONL dataset
    jsonl_file = "/project/workspace/godzilla_medical_dataset.jsonl"
    df = analyze_jsonl_dataset(jsonl_file)
    
    print(f"\n🦖 Analysis complete! Dataset ready for machine learning applications.")