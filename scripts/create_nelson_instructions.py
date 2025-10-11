#!/usr/bin/env python3
"""
Nelson Textbook to Instruction Dataset Creator
Converts clean Nelson textbook files into high-quality instruction-tuning format
"""

import json
import re
import random
from pathlib import Path

def smart_text_chunker(text, chunk_size=800, overlap=100):
    """
    Intelligently chunk text at sentence boundaries
    
    Args:
        text: Input text to chunk
        chunk_size: Target chunk size in characters
        overlap: Characters to overlap between chunks
    """
    
    chunks = []
    
    # Split into sentences (look for period followed by space and capital letter)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:  # Skip very short fragments
            continue
            
        # Check if adding this sentence would exceed chunk size
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            # Save current chunk
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from end of current chunk
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + " " + sentence
            else:
                current_chunk = sentence
        else:
            # Add sentence to current chunk
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def generate_medical_instruction_examples(text_chunk, part_number):
    """Generate diverse instruction-tuning examples from medical text"""
    
    instructions = []
    
    if len(text_chunk) < 100:
        return instructions
    
    # Extract key medical terms
    medical_terms = re.findall(r'\b(?:diagnosis|treatment|therapy|symptom|patient|disease|condition|syndrome|infection|medication|dosage)\w*\b', text_chunk.lower())
    
    # Clean output text
    clean_output = text_chunk[:600] if len(text_chunk) > 600 else text_chunk
    
    # Instruction type 1: General medical knowledge
    inst1 = {
        "instruction": "Provide medical knowledge from pediatric textbook",
        "input": "Share important pediatric medical information",
        "output": clean_output
    }
    instructions.append(inst1)
    
    # Instruction type 2: Clinical guidance
    inst2 = {
        "instruction": "Answer a pediatric medical question",
        "input": "What should a pediatrician know about clinical practice?",
        "output": clean_output
    }
    instructions.append(inst2)
    
    # Instruction type 3: Medical education
    if any(term in text_chunk.lower() for term in ['diagnosis', 'treatment', 'management']):
        inst3 = {
            "instruction": "Explain medical concepts for healthcare education",
            "input": "Explain key medical concepts from pediatric medicine",
            "output": clean_output
        }
        instructions.append(inst3)
    
    # Instruction type 4: Specific medical topic (if keywords found)
    if medical_terms:
        main_term = medical_terms[0] if medical_terms else "medical condition"
        inst4 = {
            "instruction": "Provide detailed medical information",
            "input": f"Tell me about {main_term} in pediatric medicine",
            "output": clean_output
        }
        instructions.append(inst4)
    
    # Add part metadata
    for inst in instructions:
        inst['source_part'] = f"nelson_part_{part_number}"
        inst['text_length'] = len(clean_output)
        inst['medical_source'] = "Nelson Textbook of Pediatrics 22nd Edition"
    
    return instructions

def process_nelson_files():
    """Process all three Nelson textbook parts"""
    
    print("🦖 CREATING COMPREHENSIVE NELSON INSTRUCTION DATASET")
    print("=" * 80)
    
    all_instructions = []
    
    # Process each part
    for part_num in [1, 2, 3]:
        file_path = f"/project/workspace/nelson_textbook_of_pediatrics_part_{part_num}_cleaned.txt"
        
        print(f"\n📖 Processing Part {part_num}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"   File size: {len(content):,} characters")
            
            # Chunk the text intelligently
            chunks = smart_text_chunker(content, chunk_size=1000, overlap=150)
            print(f"   Generated chunks: {len(chunks):,}")
            
            # Generate instructions from each chunk
            part_instructions = []
            for chunk in chunks:
                chunk_instructions = generate_medical_instruction_examples(chunk, part_num)
                part_instructions.extend(chunk_instructions)
            
            print(f"   Created instructions: {len(part_instructions):,}")
            all_instructions.extend(part_instructions)
            
        except FileNotFoundError:
            print(f"   ⚠️  File not found: {file_path}")
        except Exception as e:
            print(f"   ❌ Error processing part {part_num}: {e}")
    
    # Shuffle for better training distribution
    random.shuffle(all_instructions)
    
    # Write final dataset
    output_file = "/project/workspace/nelson_complete_instruction_dataset.jsonl"
    
    print(f"\n💾 Writing final dataset...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for instruction in all_instructions:
            f.write(json.dumps(instruction, ensure_ascii=False) + '\n')
    
    # Calculate statistics
    total_examples = len(all_instructions)
    avg_output_length = sum(len(inst['output']) for inst in all_instructions) / total_examples if total_examples > 0 else 0
    
    print(f"\n🎉 DATASET CREATION COMPLETE!")
    print(f"📊 Final Statistics:")
    print(f"   Total instruction examples: {total_examples:,}")
    print(f"   Average output length: {avg_output_length:.0f} characters")
    print(f"   File size: {Path(output_file).stat().st_size / (1024*1024):.1f} MB")
    
    # Show samples
    print(f"\n📋 Sample Training Examples:")
    print("-" * 60)
    
    for i, sample in enumerate(all_instructions[:3], 1):
        print(f"\n--- Example {i} ---")
        print(f"Instruction: {sample['instruction']}")
        print(f"Input: {sample['input']}")
        print(f"Output ({len(sample['output'])} chars): {sample['output'][:200]}...")
        print(f"Source: {sample['source_part']}")
    
    return total_examples

def validate_instruction_format(file_path, check_count=50):
    """Validate the instruction format for training platform"""
    
    print(f"\n🔍 Validating instruction format...")
    
    valid_count = 0
    total_checked = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if total_checked >= check_count:
                break
                
            try:
                record = json.loads(line.strip())
                
                # Check required fields
                required_fields = ['instruction', 'input', 'output']
                if all(field in record for field in required_fields):
                    if all(isinstance(record[field], str) and len(record[field]) > 10 
                          for field in required_fields):
                        valid_count += 1
                
                total_checked += 1
                
            except json.JSONDecodeError:
                total_checked += 1
    
    success_rate = (valid_count / total_checked) * 100 if total_checked > 0 else 0
    print(f"✅ Validation: {success_rate:.1f}% valid format ({valid_count}/{total_checked})")
    
    return success_rate > 90

if __name__ == "__main__":
    # Process the Nelson textbook files
    total_examples = process_nelson_files()
    
    # Validate the output format
    output_file = "/project/workspace/nelson_complete_instruction_dataset.jsonl"
    is_valid = validate_instruction_format(output_file)
    
    if is_valid:
        print(f"\n🚀 SUCCESS! Your Nelson instruction dataset is ready!")
        print(f"📁 Upload file: nelson_complete_instruction_dataset.jsonl")
        print(f"📊 Training examples: {total_examples:,}")
        print(f"🎯 Perfect for medical AI training platforms!")
    else:
        print(f"\n⚠️  Validation failed - please check the output format")
    
    print(f"\n🦖 Nelson Textbook → Instruction Dataset conversion complete!")