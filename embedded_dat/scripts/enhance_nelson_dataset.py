#!/usr/bin/env python3
"""
Nelson Dataset Enhancement Script
Adds additional features and improvements to the existing Nelson pediatric dataset.
"""

import csv
import re
import json
import argparse
from typing import Dict, List, Set
from collections import defaultdict, Counter
import uuid

class NelsonDatasetEnhancer:
    def __init__(self):
        self.medical_concepts = self._load_medical_concepts()
        self.difficulty_levels = {'basic': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
        
    def _load_medical_concepts(self) -> Dict[str, Set[str]]:
        """Define medical concept categories for tagging."""
        return {
            'anatomy': {
                'heart', 'lung', 'liver', 'kidney', 'brain', 'stomach', 'intestine',
                'bone', 'muscle', 'nerve', 'blood', 'vessel', 'organ', 'tissue'
            },
            'pathology': {
                'infection', 'inflammation', 'tumor', 'cancer', 'syndrome', 'disease',
                'disorder', 'malformation', 'deficiency', 'dysfunction', 'failure'
            },
            'pharmacology': {
                'antibiotic', 'vaccine', 'medication', 'drug', 'therapy', 'treatment',
                'dose', 'administration', 'side effect', 'interaction', 'contraindication'
            },
            'diagnostics': {
                'test', 'examination', 'imaging', 'laboratory', 'biopsy', 'screening',
                'diagnosis', 'differential', 'workup', 'evaluation', 'assessment'
            },
            'procedures': {
                'surgery', 'operation', 'procedure', 'intervention', 'resection',
                'repair', 'transplant', 'catheterization', 'intubation', 'monitoring'
            },
            'symptoms': {
                'pain', 'fever', 'rash', 'cough', 'vomiting', 'diarrhea', 'fatigue',
                'headache', 'seizure', 'difficulty', 'swelling', 'bleeding'
            }
        }
    
    def calculate_reading_difficulty(self, text: str) -> str:
        """Estimate reading difficulty level based on text complexity."""
        if not text:
            return 'basic'
        
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 'basic'
        
        # Count complex indicators
        long_words = sum(1 for word in words if len(word) > 7)
        medical_jargon = sum(1 for word in words if any(
            concept in word.lower() for concepts in self.medical_concepts.values()
            for concept in concepts
        ))
        complex_sentences = len(re.findall(r'[.!?]+', text))
        
        # Calculate complexity score
        complexity_score = (
            (long_words / word_count) * 0.4 +
            (medical_jargon / word_count) * 0.4 +
            (len(text) / word_count) * 0.2  # Average word length
        )
        
        # Classify difficulty
        if complexity_score < 0.15:
            return 'basic'
        elif complexity_score < 0.25:
            return 'intermediate'
        elif complexity_score < 0.35:
            return 'advanced'
        else:
            return 'expert'
    
    def extract_medical_concepts(self, text: str) -> Dict[str, List[str]]:
        """Extract medical concepts by category from text."""
        text_lower = text.lower()
        found_concepts = defaultdict(list)
        
        for category, concepts in self.medical_concepts.items():
            for concept in concepts:
                if concept in text_lower:
                    found_concepts[category].append(concept)
        
        return dict(found_concepts)
    
    def generate_learning_objectives(self, text: str, chapter_title: str = '') -> List[str]:
        """Generate learning objectives based on content."""
        objectives = []
        
        # Extract key verbs that indicate learning goals
        learning_verbs = {
            'understand': 'Understand the',
            'identify': 'Identify key',
            'describe': 'Describe the',
            'explain': 'Explain how',
            'recognize': 'Recognize signs of',
            'differentiate': 'Differentiate between',
            'manage': 'Manage patients with',
            'evaluate': 'Evaluate children with'
        }
        
        # Find important concepts in text
        important_concepts = []
        concept_patterns = [
            r'\b([A-Z][a-z]+ (?:syndrome|disease|disorder|condition))\b',
            r'\b((?:acute|chronic) \w+)\b',
            r'\b(\w+(?:itis|osis|pathy|emia|uria))\b',
        ]
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            important_concepts.extend([match for match in matches if len(match) > 3])
        
        # Generate objectives based on found concepts
        concepts_used = set()
        for concept in important_concepts[:3]:  # Limit to top 3
            if concept.lower() not in concepts_used:
                verb = list(learning_verbs.keys())[len(objectives) % len(learning_verbs)]
                objective = f"{learning_verbs[verb]} {concept.lower()}"
                objectives.append(objective)
                concepts_used.add(concept.lower())
        
        # Add chapter-specific objective if available
        if chapter_title and len(objectives) < 3:
            objectives.append(f"Apply knowledge of {chapter_title.lower()} in clinical practice")
        
        return objectives[:3]  # Max 3 objectives
    
    def calculate_clinical_relevance(self, text: str) -> float:
        """Calculate clinical relevance score (0-1)."""
        clinical_indicators = {
            'treatment': 0.15,
            'diagnosis': 0.15,
            'patient': 0.1,
            'clinical': 0.1,
            'therapy': 0.1,
            'management': 0.1,
            'intervention': 0.1,
            'outcome': 0.08,
            'prognosis': 0.08,
            'guidelines': 0.08,
            'evidence': 0.05,
            'recommendation': 0.05
        }
        
        text_lower = text.lower()
        score = 0.0
        
        for indicator, weight in clinical_indicators.items():
            if indicator in text_lower:
                score += weight
        
        # Boost score for practical content
        if any(phrase in text_lower for phrase in [
            'should be', 'must be', 'recommended', 'indicated', 'contraindicated',
            'first-line', 'second-line', 'standard care'
        ]):
            score += 0.1
        
        return min(score, 1.0)
    
    def extract_age_groups(self, text: str) -> List[str]:
        """Extract relevant pediatric age groups from text."""
        age_patterns = {
            'neonate': r'\b(?:neonat|newborn|birth)\b',
            'infant': r'\b(?:infant|baby|babies)\b',
            'toddler': r'\b(?:toddler|1-3 years?|2-3 years?)\b',
            'preschool': r'\b(?:preschool|3-5 years?|4-5 years?)\b',
            'school_age': r'\b(?:school.?age|6-12 years?|elementary)\b',
            'adolescent': r'\b(?:adolescent|teen|teenager|13-18 years?)\b',
            'all_ages': r'\b(?:all ages|pediatric|children|child)\b'
        }
        
        found_groups = []
        text_lower = text.lower()
        
        for group, pattern in age_patterns.items():
            if re.search(pattern, text_lower):
                found_groups.append(group)
        
        return found_groups if found_groups else ['all_ages']
    
    def enhance_dataset(self, input_file: str, output_file: str) -> None:
        """Main enhancement function."""
        print(f"Enhancing Nelson dataset: {input_file}")
        
        enhanced_records = []
        stats = defaultdict(int)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                stats['total_records'] += 1
                
                # Get existing data
                text = row.get('chunk_text', '')
                chapter_title = row.get('chapter_title', '')
                
                # Calculate new features
                medical_concepts = self.extract_medical_concepts(text)
                reading_difficulty = self.calculate_reading_difficulty(text)
                clinical_relevance = self.calculate_clinical_relevance(text)
                age_groups = self.extract_age_groups(text)
                learning_objectives = self.generate_learning_objectives(text, chapter_title)
                
                # Create enhanced record
                enhanced_record = dict(row)  # Copy existing data
                enhanced_record.update({
                    'medical_concepts': json.dumps(medical_concepts),
                    'reading_difficulty': reading_difficulty,
                    'clinical_relevance_score': round(clinical_relevance, 3),
                    'age_groups': ','.join(age_groups),
                    'learning_objectives': '|'.join(learning_objectives),
                    'enhanced_at': '2024-09-12T12:00:00'
                })
                
                enhanced_records.append(enhanced_record)
                
                # Update stats
                stats[f'difficulty_{reading_difficulty}'] += 1
                stats['with_medical_concepts'] += 1 if medical_concepts else 0
                stats['high_clinical_relevance'] += 1 if clinical_relevance > 0.5 else 0
        
        # Write enhanced dataset
        if enhanced_records:
            fieldnames = list(enhanced_records[0].keys())
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enhanced_records)
        
        # Write enhancement statistics
        stats_file = output_file.replace('.csv', '_enhancement_stats.json')
        with open(stats_file, 'w') as f:
            json.dump(dict(stats), f, indent=2)
        
        print(f"\nEnhancement complete!")
        print(f"Enhanced {len(enhanced_records)} records")
        print(f"Output: {output_file}")
        print(f"Statistics: {stats_file}")
        self.print_enhancement_stats(stats)
    
    def print_enhancement_stats(self, stats: Dict):
        """Print enhancement statistics."""
        print("\n=== Enhancement Statistics ===")
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value:,}")


def main():
    parser = argparse.ArgumentParser(description='Enhance Nelson pediatric dataset')
    parser.add_argument('input_file', help='Input Nelson CSV file path')
    parser.add_argument('output_file', help='Enhanced output CSV file path')
    
    args = parser.parse_args()
    
    enhancer = NelsonDatasetEnhancer()
    enhancer.enhance_dataset(args.input_file, args.output_file)


if __name__ == '__main__':
    main()