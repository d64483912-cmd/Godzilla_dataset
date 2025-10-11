#!/usr/bin/env python3
"""
Simple Medical Instruction Dataset Creator
Creates clean, focused instruction-tuning examples from Godzilla dataset
"""

import json
import random

def clean_medical_text(text, max_length=500):
    """Clean and truncate medical text for instruction training"""
    
    # Remove common artifacts
    text = text.replace('downloaded for mohamed ahmed drmmsgmailcom', '')
    text = text.replace('elsevier inc all rights reserved', '')
    text = text.replace('copyright elsevier', '')
    text = text.replace('visit elsevier ebooks', '')
    
    # Split into sentences and take meaningful ones
    sentences = text.split('. ')
    
    cleaned_sentences = []
    current_length = 0
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 15:  # Skip very short fragments
            continue
        if 'fig ' in sentence.lower() and len(sentence) < 50:  # Skip figure references
            continue
        if 'copyright' in sentence.lower():
            continue
            
        # Add sentence if it fits
        if current_length + len(sentence) <= max_length:
            cleaned_sentences.append(sentence)
            current_length += len(sentence)
        else:
            break
    
    result = '. '.join(cleaned_sentences)
    
    # Ensure it ends properly
    if result and not result.endswith('.'):
        result += '.'
    
    return result.strip()

def create_simple_instructions(record):
    """Create simple instruction-tuning examples"""
    
    instructions = []
    text = record.get('text', '')
    specialty = record.get('medical_specialty', 'pediatrics')
    keywords = record.get('keywords', [])
    
    if len(text) < 50:
        return instructions
    
    # Clean the text
    clean_output = clean_medical_text(text)
    
    if len(clean_output) < 50:  # Skip if cleaning removed too much
        return instructions
    
    # Generate instruction examples
    specialty_name = specialty.replace('_', ' ').title()
    
    # Example 1: General medical question
    inst1 = {
        "instruction": "Provide medical information based on clinical knowledge",
        "input": f"Tell me about {specialty_name} medical topics",
        "output": clean_output
    }
    instructions.append(inst1)
    
    # Example 2: Keyword-based question
    if keywords and len(keywords) > 0:
        main_keyword = [k for k in keywords[:3] if len(k) > 3][0] if [k for k in keywords[:3] if len(k) > 3] else keywords[0]
        
        inst2 = {
            "instruction": "Answer a specific medical question",
            "input": f"What can you tell me about {main_keyword} in medical practice?",
            "output": clean_output
        }
        instructions.append(inst2)
    
    return instructions

def main():
    print("🦖 GODZILLA MEDICAL INSTRUCTION DATASET - SIMPLE FORMAT")
    print("=" * 70)
    
    input_file = "/project/workspace/godzilla_medical_dataset.jsonl"
    output_file = "/project/workspace/godzilla_training_ready.jsonl"
    
    instruction_records = []
    processed = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                instructions = create_simple_instructions(record)
                instruction_records.extend(instructions)
                processed += 1
                
                if processed % 1000 == 0:
                    print(f"✅ Processed {processed:,} → Generated {len(instruction_records):,} instructions")
                    
            except:
                continue
    
    # Shuffle for training
    random.shuffle(instruction_records)
    
    # Write final dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        for instruction in instruction_records:
            f.write(json.dumps(instruction, ensure_ascii=False) + '\n')
    
    print(f"\n🎉 SUCCESS! Training-ready dataset created")
    print(f"📁 File: godzilla_training_ready.jsonl")
    print(f"📊 Total examples: {len(instruction_records):,}")
    
    # Calculate average lengths
    if instruction_records:
        avg_output_len = sum(len(r['output']) for r in instruction_records) / len(instruction_records)
        print(f"📏 Average output length: {avg_output_len:.0f} characters")
    
    # Show samples
    print(f"\n📋 Final Sample Records:")
    print("-" * 50)
    
    for i, sample in enumerate(instruction_records[:2], 1):
        print(f"\n--- Training Example {i} ---")
        print(f"📝 Instruction: {sample['instruction']}")
        print(f"❓ Input: {sample['input']}")
        print(f"📖 Output ({len(sample['output'])} chars): {sample['output'][:300]}...")
    
    return len(instruction_records)

if __name__ == "__main__":
    count = main()
    print(f"\n🦖 Your medical AI training dataset with {count:,} examples is ready!")
    print("📤 Upload 'godzilla_training_ready.jsonl' to your training platform")