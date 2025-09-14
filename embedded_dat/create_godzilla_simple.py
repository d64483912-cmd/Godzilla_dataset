#!/usr/bin/env python3
"""
Godzilla Medical Dataset Creator - SIMPLIFIED VERSION
Combines processed medical documents and enhanced Nelson chunks
"""

import csv
import json
import sys
from datetime import datetime
from collections import Counter

# Increase CSV field size limit to handle large medical text
csv.field_size_limit(sys.maxsize)

def create_godzilla_dataset():
    print("🦖 Creating GODZILLA Medical Dataset - The Ultimate Medical AI Powerhouse!")
    print("=" * 80)
    
    godzilla_records = []
    stats = {}
    unify_time = datetime.now().isoformat()
    
    # Unified schema for combined dataset
    schema = [
        'id', 'source_dataset', 'text', 'medical_specialty', 'keywords',
        'chunk_token_count', 'word_count', 'confidence_score', 'page_number', 'source_file',
        'book_title', 'chapter_title', 'age_groups', 'clinical_relevance_score',
        'reading_difficulty', 'learning_objectives', 'created_at', 'godzilla_created_at'
    ]
    
    # Process medical documents (548 records)
    print("📊 Processing Multi-Specialty Medical Documents...")
    med_count = 0
    try:
        with open('processed_medical_documents.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for record in reader:
                text = record.get('text', '')[:5000]
                unified_record = {
                    'id': record.get('id', ''),
                    'source_dataset': 'medical_documents',
                    'text': text,
                    'medical_specialty': record.get('medical_specialty', 'general'),
                    'keywords': record.get('keywords', ''),
                    'chunk_token_count': record.get('chunk_token_count', '0'),
                    'word_count': len(text.split()),
                    'confidence_score': record.get('confidence_score', '0.5'),
                    'page_number': record.get('page_number', ''),
                    'source_file': record.get('source_file', ''),
                    'book_title': record.get('source_file', ''),
                    'chapter_title': '',
                    'age_groups': 'all_ages',
                    'clinical_relevance_score': '0.5',
                    'reading_difficulty': 'expert',
                    'learning_objectives': 'Apply medical knowledge in clinical practice',
                    'created_at': record.get('created_at', ''),
                    'godzilla_created_at': unify_time
                }
                godzilla_records.append(unified_record)
                med_count += 1
        print(f"✅ Processed {med_count} medical document records")
    except Exception as e:
        print(f"Error processing medical docs: {e}")
    
    # Process Nelson enhanced dataset (9,068 records)  
    print("🩺 Processing Enhanced Nelson Pediatric Dataset...")
    nelson_count = 0
    try:
        with open('nelson_chunks_enhanced.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for record in reader:
                text = record.get('chunk_text', '')
                if not text:
                    text = record.get('text', '')
                truncated = text[:5000]
                unified_record = {
                    'id': record.get('id', ''),
                    'source_dataset': 'nelson_enhanced',
                    'text': truncated,
                    'medical_specialty': 'pediatrics',
                    'keywords': record.get('keywords', ''),
                    'chunk_token_count': record.get('chunk_token_count', '0'),
                    'word_count': len(truncated.split()),
                    'confidence_score': record.get('confidence_score', '0.5'),
                    'page_number': record.get('page_number', ''),
                    'source_file': record.get('book_title', 'Nelson Textbook of Pediatrics'),
                    'book_title': record.get('book_title', 'Nelson Textbook of Pediatrics'),
                    'chapter_title': record.get('chapter_title', ''),
                    'age_groups': record.get('age_groups', 'all_ages'),
                    'clinical_relevance_score': record.get('clinical_relevance_score', '0.5'),
                    'reading_difficulty': record.get('reading_difficulty', 'expert'),
                    'learning_objectives': record.get('learning_objectives', 'Apply pediatric knowledge'),
                    'created_at': record.get('created_at', ''),
                    'godzilla_created_at': unify_time
                }
                godzilla_records.append(unified_record)
                nelson_count += 1
        print(f"✅ Processed {nelson_count} Nelson enhanced records")
    except Exception as e:
        print(f"Error processing Nelson data: {e}")
    
    # Calculate statistics
    total_records = len(godzilla_records)
    print(f"\n📈 Dataset Statistics:")
    print(f"   Total Records: {total_records:,}")
    print(f"   Medical Documents: {med_count:,}")
    print(f"   Nelson Enhanced: {nelson_count:,}")
    
    # Quality distribution
    quality_scores = []
    for record in godzilla_records:
        try:
            score = float(record['confidence_score'])
            quality_scores.append(score)
        except:
            quality_scores.append(0.5)
    
    avg_quality = sum(quality_scores) / len(quality_scores)
    high_quality = sum(1 for score in quality_scores if score >= 0.7)
    
    print(f"   Average Quality Score: {avg_quality:.3f}")
    print(f"   High Quality Records (≥0.7): {high_quality:,} ({high_quality/total_records*100:.1f}%)")
    
    # Specialty distribution
    specialties = Counter(record['medical_specialty'] for record in godzilla_records)
    print(f"\n🏥 Medical Specialty Distribution:")
    for specialty, count in specialties.most_common(10):
        print(f"   {specialty}: {count:,} records")
    
    # Sort by quality score (highest first)
    print("\n📊 Sorting by quality score...")
    godzilla_records.sort(key=lambda x: float(x['confidence_score']), reverse=True)
    
    # Write the Godzilla dataset
    output_file = 'godzilla_medical_dataset.csv'
    print(f"\n💾 Writing Godzilla dataset to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=schema)
        writer.writeheader()
        writer.writerows(godzilla_records)
    
    # Write statistics
    stats = {
        'total_records': total_records,
        'medical_documents': med_count,
        'nelson_enhanced': nelson_count,
        'avg_quality_score': avg_quality,
        'high_quality_records': high_quality,
        'quality_rate_percent': high_quality/total_records*100,
        'specialty_distribution': dict(specialties),
        'created_at': datetime.now().isoformat()
    }
    
    with open('godzilla_medical_dataset_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("\n" + "🦖" * 20)
    print("GODZILLA MEDICAL DATASET CREATION COMPLETE!")
    print("🦖" * 20)
    print(f"\n🎉 SUCCESS! Created ultimate medical dataset with {total_records:,} records")
    print(f"📁 Output File: {output_file}")
    print(f"📊 Statistics File: godzilla_medical_dataset_stats.json")
    print(f"📈 Quality Rate: {high_quality/total_records*100:.1f}% high-quality records")
    print(f"🏥 Coverage: {len(specialties)} medical specialties")
    print("\n🚀 GODZILLA IS READY TO DOMINATE MEDICAL AI! 🦖")
    
    return output_file

if __name__ == '__main__':
    create_godzilla_dataset()