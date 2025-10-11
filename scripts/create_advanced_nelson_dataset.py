#!/usr/bin/env python3
"""
Advanced Nelson Textbook Instruction Dataset Creator
Smart chunking for large continuous medical text files
"""

import json
import re
import random
import os

def advanced_text_chunker(text, target_chunk_size=1200):
    """
    Advanced text chunking that handles continuous medical text
    """
    
    chunks = []
    
    # First, try to find natural break points
    # Look for chapter/section indicators
    chapter_splits = re.split(r'(?i)(?:chapter\s+\d+|part\s+[ivx]+)', text)
    
    if len(chapter_splits) > 5:  # If we found good chapter breaks
        print(f"   Found {len(chapter_splits)} chapter sections")
        
        for section in chapter_splits:
            if len(section.strip()) > 200:  # Only process substantial sections
                section_chunks = split_by_size(section.strip(), target_chunk_size)
                chunks.extend(section_chunks)
    else:
        # Fallback: split by size with smart boundaries
        chunks = split_by_size(text, target_chunk_size)
    
    return chunks

def split_by_size(text, target_size=1200):
    """Split text into chunks of approximately target_size"""
    
    chunks = []
    words = text.split()
    
    current_chunk_words = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        
        if current_length + word_length > target_size and current_chunk_words:
            # Save current chunk
            chunk_text = ' '.join(current_chunk_words)
            if len(chunk_text) > 100:  # Only save substantial chunks
                chunks.append(chunk_text)
            
            # Start new chunk
            current_chunk_words = [word]
            current_length = word_length
        else:
            current_chunk_words.append(word)
            current_length += word_length
    
    # Add final chunk
    if current_chunk_words:
        final_chunk = ' '.join(current_chunk_words)
        if len(final_chunk) > 100:
            chunks.append(final_chunk)
    
    return chunks

def extract_medical_topics(text):
    """Extract likely medical topics from text"""
    
    # Common medical patterns
    patterns = [
        r'\b[A-Z][a-z]+ (?:syndrome|disease|disorder|condition)\b',
        r'\b(?:acute|chronic) [a-z]+ [a-z]+\b',
        r'\b[a-z]+ (?:infection|inflammation|injury)\b'
    ]
    
    topics = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        topics.extend(matches[:3])  # Limit to prevent too many
    
    return list(set(topics))[:5]  # Remove duplicates, limit to 5

def create_diverse_instructions(chunk, part_name, chunk_index):
    """Create diverse instruction formats from a medical text chunk"""
    
    instructions = []
    
    # Clean the chunk
    clean_chunk = chunk.strip()
    if len(clean_chunk) < 100:
        return instructions
    
    # Limit output length for training efficiency
    output_text = clean_chunk[:800] if len(clean_chunk) > 800 else clean_chunk
    
    # Extract topics for more specific instructions
    topics = extract_medical_topics(clean_chunk)
    
    # Instruction 1: General medical knowledge
    inst1 = {
        "instruction": "Provide pediatric medical information",
        "input": "Share relevant medical knowledge from pediatric practice",
        "output": output_text
    }
    instructions.append(inst1)
    
    # Instruction 2: Educational content
    inst2 = {
        "instruction": "Explain medical concepts for healthcare professionals",
        "input": "What are important concepts in pediatric medicine?",
        "output": output_text
    }
    instructions.append(inst2)
    
    # Instruction 3: Topic-specific (if topics found)
    if topics:
        topic = topics[0]
        inst3 = {
            "instruction": "Answer a specific medical question",
            "input": f"What should I know about {topic.lower()}?",
            "output": output_text
        }
        instructions.append(inst3)
    
    # Instruction 4: Clinical guidance
    if any(word in clean_chunk.lower() for word in ['patient', 'treatment', 'diagnosis', 'therapy']):
        inst4 = {
            "instruction": "Provide clinical guidance based on medical literature",
            "input": "I need clinical guidance for patient care",
            "output": output_text
        }
        instructions.append(inst4)
    
    # Add metadata
    for inst in instructions:
        inst['chunk_id'] = f"{part_name}_chunk_{chunk_index}"
        inst['source'] = "Nelson Textbook of Pediatrics 22nd Edition"
        inst['content_type'] = "medical_textbook"
    
    return instructions

def main():
    print("🦖 ADVANCED NELSON INSTRUCTION DATASET CREATOR")
    print("=" * 70)
    
    all_instructions = []
    total_text_processed = 0
    
    # Process all three parts
    for part_num in [1, 2, 3]:
        file_path = f"/project/workspace/nelson_textbook_of_pediatrics_part_{part_num}_cleaned.txt"
        
        print(f"\n📚 Processing Nelson Part {part_num}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"   📏 File size: {len(content):,} characters")
            total_text_processed += len(content)
            
            # Advanced chunking
            chunks = advanced_text_chunker(content, target_chunk_size=1500)
            print(f"   ✂️  Generated: {len(chunks)} chunks")
            
            # Create instructions from chunks
            part_instructions = []
            for i, chunk in enumerate(chunks):
                chunk_instructions = create_diverse_instructions(chunk, f"nelson_part_{part_num}", i)
                part_instructions.extend(chunk_instructions)
            
            print(f"   🎯 Created: {len(part_instructions):,} instruction examples")
            all_instructions.extend(part_instructions)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🔀 Shuffling {len(all_instructions):,} examples for optimal training...")
    random.shuffle(all_instructions)
    
    # Write the complete dataset
    output_file = "/project/workspace/nelson_complete_training_dataset.jsonl"
    
    print(f"💾 Writing complete dataset to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for instruction in all_instructions:
            f.write(json.dumps(instruction, ensure_ascii=False) + '\n')
    
    # Final statistics
    print(f"\n🎉 COMPREHENSIVE DATASET CREATED!")
    print(f"📊 Final Statistics:")
    print(f"   📖 Source text processed: {total_text_processed:,} characters ({total_text_processed/(1024*1024):.1f} MB)")
    print(f"   🎯 Training examples created: {len(all_instructions):,}")
    print(f"   📏 Average output length: {sum(len(inst['output']) for inst in all_instructions)//len(all_instructions):.0f} characters")
    
    print(f"   💾 Output file size: {os.path.getsize(output_file) / (1024 * 1024):.1f} MB")
    
    # Show sample records
    print(f"\n📋 Sample Instruction Records:")
    print("-" * 60)
    
    for i, sample in enumerate(all_instructions[:3], 1):
        print(f"\n--- Training Example {i} ---")
        print(f"📝 Instruction: {sample['instruction']}")
        print(f"❓ Input: {sample['input']}")
        print(f"📖 Output ({len(sample['output'])} chars): {sample['output'][:250]}...")
        print(f"🏷️  Source: {sample.get('chunk_id', 'N/A')}")
    
    print(f"\n🚀 READY FOR TRAINING PLATFORM!")
    print(f"📤 Upload: nelson_complete_training_dataset.jsonl")
    print(f"🎓 {len(all_instructions):,} medical instruction examples ready!")

if __name__ == "__main__":
    main()