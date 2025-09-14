#!/usr/bin/env python3
"""
Medical Documents Dataset Processor
Cleans and enhances the raw medical documents dataset with comprehensive preprocessing.
"""

import csv
import re
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
import argparse
import json

# Patterns for cleaning and detection
COPYRIGHT_PATTERN = re.compile(
    r'Downloaded for .+? at .+? from .+? by .+? on .+?\. For personal use only\. No other uses without permission\. Copyright .+?',
    re.IGNORECASE | re.DOTALL
)

PAGE_ARTIFACT_PATTERNS = [
    re.compile(r'^\s*Page\s+\d+\s*$', re.IGNORECASE),
    re.compile(r'^\s*Chapter\s+\d+\s*$', re.IGNORECASE),
    re.compile(r'^\s*Fig\.\s*\d+(\.\d+)*\s', re.IGNORECASE),
    re.compile(r'^\s*Table\s+\d+(\.\d+)*\s', re.IGNORECASE),
    re.compile(r'^\s*\d+\s*$'),  # Pure page numbers
    re.compile(r'^\s*[a-z]\s*$'),  # Single lowercase letters
    re.compile(r'^\s*[^\w\s]*\s*$'),  # Only punctuation
]

REFERENCE_PATTERN = re.compile(r'\b\d{4};\d+:', re.IGNORECASE)

# Medical stopwords to exclude from keyword extraction
MEDICAL_STOPWORDS = set([
    'patient', 'patients', 'disease', 'treatment', 'clinical', 'medical', 'condition',
    'diagnosis', 'therapy', 'symptoms', 'syndrome', 'disorders', 'health', 'care',
    'study', 'studies', 'cases', 'case', 'report', 'reports', 'review', 'analysis'
])

GENERAL_STOPWORDS = set([
    'the', 'of', 'and', 'in', 'to', 'for', 'with', 'by', 'from', 'at', 'on', 'as',
    'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'must', 'shall', 'this', 'that', 'these',
    'those', 'a', 'an', 'or', 'but', 'if', 'when', 'where', 'how', 'what', 'who',
    'which', 'than', 'more', 'most', 'less', 'very', 'also', 'not', 'no', 'only',
    'such', 'other', 'same', 'new', 'first', 'last', 'next', 'each', 'every', 'all',
    'some', 'any', 'many', 'much', 'few', 'several', 'both', 'either', 'neither'
])

ALL_STOPWORDS = MEDICAL_STOPWORDS | GENERAL_STOPWORDS


class MedicalDocumentProcessor:
    def __init__(self):
        self.stats = {
            'total_records': 0,
            'cleaned_records': 0,
            'merged_fragments': 0,
            'removed_artifacts': 0,
            'removed_copyright': 0,
            'empty_removed': 0,
            'duplicates_removed': 0
        }
        
    def clean_text(self, text: str) -> str:
        """Clean individual text content."""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove copyright notices
        original_text = text
        text = COPYRIGHT_PATTERN.sub('', text)
        if text != original_text:
            self.stats['removed_copyright'] += 1
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common artifacts
        text = re.sub(r'\b\d+\s*\.\s*\d+\s*\.\s*\d+\s*\b', '', text)  # Version numbers like "1.2.3"
        text = re.sub(r'\b[A-Z]{2,}\s*\d+\b', '', text)  # Codes like "ICD10"
        
        return text.strip()
    
    def is_artifact_record(self, text: str) -> bool:
        """Check if record is primarily page artifacts."""
        if not text or len(text.strip()) < 5:
            return True
            
        for pattern in PAGE_ARTIFACT_PATTERNS:
            if pattern.match(text.strip()):
                return True
                
        # Check for pure reference entries
        if REFERENCE_PATTERN.search(text) and len(text) < 100:
            return True
            
        # Check for table cell fragments (numbers, short entries)
        if len(text.split()) <= 2 and not any(c.isalpha() for c in text if c != ' '):
            return True
            
        return False
    
    def extract_keywords(self, text: str, k: int = 8) -> List[str]:
        """Extract meaningful keywords from text."""
        if not text:
            return []
            
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text.lower())
        
        # Count frequency, excluding stopwords
        freq = defaultdict(int)
        for word in words:
            if len(word) >= 3 and word not in ALL_STOPWORDS:
                freq[word] += 1
        
        # Return top keywords
        return [word for word, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:k]]
    
    def categorize_by_content(self, text: str) -> str:
        """Categorize medical content by specialty."""
        text_lower = text.lower()
        
        # Define specialty patterns
        specialties = {
            'cardiology': ['heart', 'cardiac', 'cardiovascular', 'coronary', 'artery', 'valve'],
            'neurology': ['brain', 'neurolog', 'seizure', 'stroke', 'cerebral', 'neural'],
            'pediatrics': ['child', 'pediatric', 'infant', 'neonatal', 'growth', 'development'],
            'urology': ['kidney', 'renal', 'urine', 'bladder', 'urinary', 'nephro'],
            'endocrinology': ['hormone', 'diabetes', 'thyroid', 'endocrine', 'insulin'],
            'dermatology': ['skin', 'rash', 'derma', 'lesion', 'cutaneous'],
            'gastroenterology': ['stomach', 'intestine', 'liver', 'digestive', 'gastro'],
            'pulmonology': ['lung', 'respiratory', 'asthma', 'pneumonia', 'breathing'],
            'rheumatology': ['arthritis', 'joint', 'rheumatic', 'autoimmune', 'inflammation'],
            'oncology': ['cancer', 'tumor', 'malignant', 'oncology', 'chemotherapy'],
            'immunology': ['immune', 'allergy', 'antibody', 'immunologic', 'hypersensitivity'],
            'psychiatry': ['depression', 'anxiety', 'psychiatric', 'mental', 'behavioral'],
            'orthopedics': ['bone', 'fracture', 'orthopedic', 'musculoskeletal', 'joint'],
            'emergency': ['emergency', 'trauma', 'acute', 'critical', 'resuscitation'],
            'genetics': ['genetic', 'chromosome', 'hereditary', 'mutation', 'genomic']
        }
        
        specialty_scores = {}
        for specialty, keywords in specialties.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                specialty_scores[specialty] = score
        
        if specialty_scores:
            return max(specialty_scores, key=specialty_scores.get)
        return 'general'
    
    def merge_fragments(self, records: List[Dict]) -> List[Dict]:
        """Merge text fragments that belong together."""
        merged_records = []
        current_group = []
        
        for record in records:
            text = record.get('text', '').strip()
            source = record.get('source_file', '')
            page = record.get('page_number', '')
            
            # Skip if empty or artifact
            if not text or self.is_artifact_record(text):
                self.stats['removed_artifacts'] += 1
                continue
            
            # Check if this should be merged with previous
            should_merge = False
            if current_group:
                last_record = current_group[-1]
                last_text = last_record.get('text', '')
                
                # Merge criteria
                same_source = last_record.get('source_file') == source
                adjacent_page = abs(int(page or 0) - int(last_record.get('page_number', 0) or 0)) <= 1
                text_continues = (
                    last_text.endswith(('-', 'the ', 'and ', 'of ', 'in ', 'to ', 'with ')) or
                    not last_text.endswith('.') or
                    text.startswith(('ing ', 'ed ', 'er ', 'tion ', 'ly '))
                )
                short_fragment = len(text.split()) < 20
                
                should_merge = same_source and (adjacent_page or text_continues or short_fragment)
            
            if should_merge and current_group:
                # Merge with last record in group
                last_record = current_group[-1]
                merged_text = last_record['text'] + ' ' + text
                last_record['text'] = merged_text
                last_record['chunk_token_count'] = len(merged_text.split())
                self.stats['merged_fragments'] += 1
            else:
                # Start new record or group
                if current_group and len(current_group) >= 1:
                    # Finalize current group
                    for group_record in current_group:
                        merged_records.append(group_record)
                    current_group = []
                
                # Create new record
                cleaned_record = {
                    'id': str(uuid.uuid4()),
                    'text': text,
                    'page_number': page,
                    'source_file': source,
                    'chunk_token_count': len(text.split()),
                    'medical_specialty': self.categorize_by_content(text),
                    'keywords': ', '.join(self.extract_keywords(text)),
                    'confidence_score': self.calculate_confidence(text),
                    'created_at': datetime.now().isoformat()
                }
                current_group = [cleaned_record]
        
        # Add remaining group
        if current_group:
            merged_records.extend(current_group)
        
        return merged_records
    
    def calculate_confidence(self, text: str) -> float:
        """Calculate confidence score for text quality."""
        if not text:
            return 0.0
        
        score = 0.5  # Base score
        
        # Length bonus
        word_count = len(text.split())
        if word_count >= 50:
            score += 0.2
        elif word_count >= 20:
            score += 0.1
        
        # Completeness bonus
        if text.endswith('.') or text.endswith('?') or text.endswith('!'):
            score += 0.1
        
        # Medical content bonus
        medical_terms = ['patient', 'treatment', 'diagnosis', 'symptoms', 'therapy', 'clinical']
        medical_score = sum(1 for term in medical_terms if term.lower() in text.lower())
        score += min(medical_score * 0.05, 0.15)
        
        # Penalize artifacts
        if any(pattern.search(text) for pattern in PAGE_ARTIFACT_PATTERNS):
            score -= 0.2
        
        return min(max(score, 0.0), 1.0)
    
    def remove_duplicates(self, records: List[Dict]) -> List[Dict]:
        """Remove duplicate records based on text similarity."""
        seen_texts = set()
        unique_records = []
        
        for record in records:
            text = record.get('text', '').strip().lower()
            # Create a signature of the text
            text_signature = re.sub(r'\W+', '', text)[:200]  # First 200 characters, alphanumeric only
            
            if text_signature not in seen_texts:
                seen_texts.add(text_signature)
                unique_records.append(record)
            else:
                self.stats['duplicates_removed'] += 1
        
        return unique_records
    
    def process_dataset(self, input_file: str, output_file: str) -> None:
        """Main processing function."""
        print(f"Processing medical documents dataset: {input_file}")
        
        raw_records = []
        
        # Read input CSV
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.stats['total_records'] += 1
                raw_records.append({
                    'text': self.clean_text(row.get('text', '')),
                    'page_number': row.get('page_number', ''),
                    'source_file': row.get('source_file', '')
                })
        
        print(f"Read {len(raw_records)} raw records")
        
        # Process records
        merged_records = self.merge_fragments(raw_records)
        print(f"After merging fragments: {len(merged_records)} records")
        
        unique_records = self.remove_duplicates(merged_records)
        print(f"After removing duplicates: {len(unique_records)} records")
        
        # Filter out low-quality records
        quality_records = [r for r in unique_records if r['confidence_score'] >= 0.3]
        print(f"After quality filtering: {len(quality_records)} records")
        
        self.stats['cleaned_records'] = len(quality_records)
        
        # Write output CSV
        fieldnames = [
            'id', 'text', 'page_number', 'source_file', 'medical_specialty',
            'keywords', 'chunk_token_count', 'confidence_score', 'created_at'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(quality_records)
        
        # Write processing statistics
        stats_file = output_file.replace('.csv', '_processing_stats.json')
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"\nProcessing complete!")
        print(f"Output file: {output_file}")
        print(f"Statistics: {stats_file}")
        self.print_stats()
    
    def print_stats(self):
        """Print processing statistics."""
        print("\n=== Processing Statistics ===")
        for key, value in self.stats.items():
            print(f"{key.replace('_', ' ').title()}: {value:,}")
        
        if self.stats['total_records'] > 0:
            retention_rate = (self.stats['cleaned_records'] / self.stats['total_records']) * 100
            print(f"Retention Rate: {retention_rate:.1f}%")


def main():
    parser = argparse.ArgumentParser(description='Process medical documents dataset')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('output_file', help='Output CSV file path')
    parser.add_argument('--min-confidence', type=float, default=0.3,
                       help='Minimum confidence score for records (default: 0.3)')
    
    args = parser.parse_args()
    
    processor = MedicalDocumentProcessor()
    processor.process_dataset(args.input_file, args.output_file)


if __name__ == '__main__':
    main()