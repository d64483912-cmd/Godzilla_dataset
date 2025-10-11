#!/usr/bin/env python3
"""
Convert Godzilla Medical Dataset to Instruction-Tuning Format
Transforms medical knowledge into instruction/input/output format for training platforms
"""

import json
import random
from typing import List, Dict

def generate_medical_instructions(record: Dict) -> List[Dict]:
    """
    Generate multiple instruction-tuning examples from a single medical record
    
    Args:
        record: Single medical record from Godzilla dataset
        
    Returns:
        List of instruction-tuning formatted records
    """
    
    instructions = []
    text = record.get('text', '')
    specialty = record.get('medical_specialty', 'medicine')
    keywords = record.get('keywords', [])
    age_groups = record.get('age_groups', 'all_ages')
    
    if len(text) < 100:  # Skip very short texts
        return instructions
    
    # Instruction type 1: General medical question about the content
    if keywords:
        main_keywords = keywords[:3]  # Use top 3 keywords
        keyword_text = ', '.join(main_keywords)
        
        instruction1 = {
            "instruction": f"Provide medical information about {keyword_text} in {specialty}",
            "input": f"What should medical professionals know about {keyword_text}?",
            "output": text[:2000]  # Limit output length
        }
        instructions.append(instruction1)
    
    # Instruction type 2: Age-specific question
    if age_groups != 'all_ages':
        age_specific = age_groups.replace('_', ' ').replace(',all_ages', '')
        instruction2 = {
            "instruction": f"Explain {specialty} considerations for {age_specific} patients",
            "input": f"What are important {specialty} considerations when treating {age_specific} patients?",
            "output": text[:2000]
        }
        instructions.append(instruction2)
    
    # Instruction type 3: Specialty-specific question
    specialty_formatted = specialty.replace('_', ' ').title()
    instruction3 = {
        "instruction": f"Provide {specialty_formatted} medical guidance",
        "input": f"I need clinical information about {specialty_formatted}. Can you help?",
        "output": text[:2000]
    }
    instructions.append(instruction3)
    
    # Instruction type 4: Keyword-based clinical question
    if len(keywords) >= 2:
        clinical_keywords = [kw for kw in keywords[:5] if len(kw) > 3][:2]
        if len(clinical_keywords) >= 2:
            instruction4 = {
                "instruction": "Answer a clinical question based on medical evidence",
                "input": f"What is the relationship between {clinical_keywords[0]} and {clinical_keywords[1]} in clinical practice?",
                "output": text[:2000]
            }
            instructions.append(instruction4)
    
    # Instruction type 5: Diagnostic/treatment guidance
    if any(word in text.lower() for word in ['diagnosis', 'treatment', 'therapy', 'management']):
        instruction5 = {
            "instruction": "Provide diagnostic and treatment guidance",
            "input": f"What are the key diagnostic and treatment considerations in {specialty}?",
            "output": text[:2000]
        }
        instructions.append(instruction5)
    
    return instructions

def convert_to_instruction_format(input_jsonl: str, output_jsonl: str, max_records: int = None):
    """
    Convert Godzilla medical dataset to instruction-tuning format
    
    Args:
        input_jsonl: Path to input JSONL file
        output_jsonl: Path to output instruction-format JSONL file
        max_records: Maximum number of records to process (None for all)
    """
    
    print("🦖 Converting Godzilla Dataset to Instruction-Tuning Format")
    print("=" * 70)
    
    instruction_records = []
    processed_count = 0
    
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            if max_records and processed_count >= max_records:
                break
                
            try:
                record = json.loads(line.strip())
                
                # Generate instruction examples from this record
                instructions = generate_medical_instructions(record)
                instruction_records.extend(instructions)
                
                processed_count += 1
                
                if processed_count % 1000 == 0:
                    print(f"✅ Processed {processed_count:,} records → {len(instruction_records):,} instructions")
                    
            except json.JSONDecodeError:
                print(f"⚠️  Skipped invalid JSON line")
                continue
    
    # Shuffle the instruction records for better training
    random.shuffle(instruction_records)
    
    # Write instruction-format JSONL
    print(f"\n💾 Writing {len(instruction_records):,} instruction records to {output_jsonl}")
    
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for instruction in instruction_records:
            f.write(json.dumps(instruction, ensure_ascii=False) + '\n')
    
    print("🎉 Conversion Complete!")
    print(f"📊 Statistics:")
    print(f"   Original records: {processed_count:,}")
    print(f"   Instruction examples: {len(instruction_records):,}")
    print(f"   Expansion ratio: {len(instruction_records)/processed_count:.1f}x")
    
    return instruction_records

def create_sample_preview(instruction_records: List[Dict], num_samples: int = 3):
    """Show sample instruction records"""
    
    print(f"\n📋 Sample Instruction Records:")
    print("-" * 70)
    
    for i, sample in enumerate(instruction_records[:num_samples], 1):
        print(f"\n--- Sample {i} ---")
        print(f"Instruction: {sample['instruction']}")
        print(f"Input: {sample['input']}")
        print(f"Output: {sample['output'][:200]}...")
        
def validate_instruction_format(jsonl_file: str, num_check: int = 100):
    """Validate the instruction format"""
    
    print(f"\n🔍 Validating instruction format...")
    
    valid_count = 0
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_check:
                break
                
            try:
                record = json.loads(line.strip())
                
                # Check required fields
                if all(key in record for key in ['instruction', 'input', 'output']):
                    if all(isinstance(record[key], str) and len(record[key]) > 0 
                          for key in ['instruction', 'input', 'output']):
                        valid_count += 1
                
            except json.JSONDecodeError:
                pass
    
    success_rate = (valid_count / min(num_check, i + 1)) * 100
    print(f"✅ Validation complete: {success_rate:.1f}% valid records")
    
    return success_rate > 95

if __name__ == "__main__":
    # File paths
    input_file = "/project/workspace/godzilla_medical_dataset.jsonl"
    output_file = "/project/workspace/godzilla_instruction_dataset.jsonl"
    
    # Convert to instruction format
    instruction_records = convert_to_instruction_format(input_file, output_file)
    
    # Show samples
    create_sample_preview(instruction_records)
    
    # Validate format
    validate_instruction_format(output_file)
    
    print(f"\n🦖 Your Godzilla instruction dataset is ready for training!")
    print(f"📁 File: godzilla_instruction_dataset.jsonl")
    print(f"📊 Records: {len(instruction_records):,} instruction examples")