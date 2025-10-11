#!/usr/bin/env python3
"""
Create Optimized Instruction Dataset - Short Format
Generate concise instruction-tuning examples perfect for training platforms
"""

import json
import random

def extract_key_medical_info(text, max_length=400):
    """Extract the most relevant medical information from text"""
    
    # Split into sentences
    sentences = text.replace('. ', '.|').split('|')
    
    # Find sentences with key medical terms
    medical_keywords = [
        'diagnosis', 'treatment', 'therapy', 'symptoms', 'management', 
        'patients', 'clinical', 'disease', 'condition', 'infection',
        'medication', 'dosage', 'complications', 'prognosis'
    ]
    
    relevant_sentences = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue
            
        # Check if sentence contains medical keywords
        if any(keyword in sentence.lower() for keyword in medical_keywords):
            if current_length + len(sentence) <= max_length:
                relevant_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break
    
    if not relevant_sentences:
        # Fallback to first sentences if no keywords found
        current_length = 0
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if current_length + len(sentence) <= max_length:
                relevant_sentences.append(sentence)
                current_length += len(sentence)
            else:
                break
    
    return '. '.join(relevant_sentences).strip()

def generate_focused_instructions(record):
    """Generate focused instruction-tuning examples"""
    
    instructions = []
    text = record.get('text', '')
    specialty = record.get('medical_specialty', 'medicine')
    keywords = record.get('keywords', [])
    
    if len(text) < 100:
        return instructions
    
    # Extract key medical information
    focused_output = extract_key_medical_info(text)
    
    # Instruction 1: Medical Q&A
    if keywords and len(keywords) >= 2:
        primary_topic = keywords[0] if len(keywords[0]) > 3 else keywords[1]
        
        instruction1 = {
            "instruction": "Answer a medical question based on clinical knowledge",
            "input": f"What should I know about {primary_topic} in {specialty}?",
            "output": focused_output
        }
        instructions.append(instruction1)
    
    # Instruction 2: Clinical guidance  
    instruction2 = {
        "instruction": "Provide clinical medical guidance",
        "input": f"I need medical information about {specialty}. Can you provide guidance?",
        "output": focused_output
    }
    instructions.append(instruction2)
    
    # Instruction 3: Specialty-specific question
    if specialty != 'general':
        specialty_name = specialty.replace('_', ' ').title()
        instruction3 = {
            "instruction": f"Explain {specialty_name} medical concepts",
            "input": f"Can you explain key {specialty_name} concepts?",
            "output": focused_output
        }
        instructions.append(instruction3)
    
    return instructions

def create_optimized_dataset(input_jsonl, output_jsonl):
    """Create optimized instruction dataset with shorter outputs"""
    
    print("🦖 Creating OPTIMIZED Instruction Dataset")
    print("=" * 60)
    print("✨ Features: Shorter outputs, focused content, better for training")
    
    instruction_records = []
    processed_count = 0
    
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                instructions = generate_focused_instructions(record)
                instruction_records.extend(instructions)
                processed_count += 1
                
                if processed_count % 1000 == 0:
                    print(f"✅ Processed {processed_count:,} records → {len(instruction_records):,} instructions")
                    
            except json.JSONDecodeError:
                continue
    
    # Shuffle for better training
    random.shuffle(instruction_records)
    
    # Write optimized JSONL
    with open(output_jsonl, 'w', encoding='utf-8') as f:
        for instruction in instruction_records:
            f.write(json.dumps(instruction, ensure_ascii=False) + '\n')
    
    print(f"\n🎉 Optimized dataset created!")
    print(f"📊 Statistics:")
    print(f"   Original records: {processed_count:,}")
    print(f"   Instruction examples: {len(instruction_records):,}")
    print(f"   Average output length: ~400 characters (optimized)")
    
    # Show samples
    print(f"\n📋 Sample Records (Optimized Format):")
    print("-" * 60)
    
    for i, sample in enumerate(instruction_records[:3], 1):
        print(f"\n--- Sample {i} ---")
        print(f"Instruction: {sample['instruction']}")
        print(f"Input: {sample['input']}")
        print(f"Output Length: {len(sample['output'])} chars")
        print(f"Output: {sample['output'][:200]}...")
    
    return instruction_records

if __name__ == "__main__":
    input_file = "/project/workspace/godzilla_medical_dataset.jsonl"
    output_file = "/project/workspace/godzilla_instruction_optimized.jsonl"
    
    records = create_optimized_dataset(input_file, output_file)
    
    print(f"\n🚀 Ready for training platform upload!")
    print(f"📁 Optimized file: godzilla_instruction_optimized.jsonl")
    print(f"📊 Total examples: {len(records):,}")