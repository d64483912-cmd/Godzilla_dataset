#!/usr/bin/env python3
"""
Godzilla Medical Dataset CSV to JSONL Converter
Converts the comprehensive medical dataset from CSV format to JSONL for ML training
"""

import csv
import json
import sys
from pathlib import Path

# Increase CSV field size limit for large medical text
csv.field_size_limit(sys.maxsize)

def convert_csv_to_jsonl(csv_file_path, jsonl_file_path):
    """
    Convert CSV file to JSONL format
    
    Args:
        csv_file_path (str): Path to input CSV file
        jsonl_file_path (str): Path to output JSONL file
    """
    
    records_processed = 0
    
    print(f"🦖 Converting Godzilla Medical Dataset to JSONL format...")
    print(f"📁 Input:  {csv_file_path}")
    print(f"📁 Output: {jsonl_file_path}")
    print("-" * 80)
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            # Use DictReader to automatically handle headers
            reader = csv.DictReader(csv_file)
            
            with open(jsonl_file_path, 'w', encoding='utf-8') as jsonl_file:
                for row in reader:
                    # Convert CSV row to JSON object
                    json_record = {}
                    
                    for key, value in row.items():
                        # Handle different data types appropriately
                        if key in ['chunk_token_count', 'word_count', 'page_number']:
                            # Convert to integer if possible
                            try:
                                json_record[key] = int(value) if value and value.strip() else 0
                            except ValueError:
                                json_record[key] = 0
                                
                        elif key in ['confidence_score', 'clinical_relevance_score']:
                            # Convert to float if possible  
                            try:
                                json_record[key] = float(value) if value and value.strip() else 0.0
                            except ValueError:
                                json_record[key] = 0.0
                                
                        elif key == 'keywords':
                            # Convert keywords to array
                            if value and value.strip():
                                # Split by comma and clean up
                                keywords_list = [kw.strip() for kw in value.split(',')]
                                json_record[key] = keywords_list
                            else:
                                json_record[key] = []
                                
                        else:
                            # Keep as string, handle empty values
                            json_record[key] = value.strip() if value else ""
                    
                    # Add metadata for ML training
                    json_record['dataset_version'] = '1.0'
                    json_record['record_type'] = 'medical_knowledge'
                    
                    # Calculate text length for filtering
                    text_content = json_record.get('text', '')
                    json_record['text_length'] = len(text_content)
                    json_record['word_count_calculated'] = len(text_content.split())
                    
                    # Add training labels based on medical specialty
                    specialty = json_record.get('medical_specialty', '').lower()
                    json_record['training_category'] = specialty if specialty else 'general_medicine'
                    
                    # Write JSON object as single line
                    jsonl_file.write(json.dumps(json_record, ensure_ascii=False) + '\n')
                    records_processed += 1
                    
                    # Progress indicator
                    if records_processed % 1000 == 0:
                        print(f"✅ Processed {records_processed:,} records...")
    
    except FileNotFoundError:
        print(f"❌ Error: Could not find input file {csv_file_path}")
        return False
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        return False
    
    print("-" * 80)
    print(f"🎉 Conversion completed successfully!")
    print(f"📊 Total records processed: {records_processed:,}")
    print(f"💾 Output file: {jsonl_file_path}")
    
    # Calculate file sizes
    try:
        csv_size = Path(csv_file_path).stat().st_size / (1024 * 1024)  # MB
        jsonl_size = Path(jsonl_file_path).stat().st_size / (1024 * 1024)  # MB
        
        print(f"📈 File sizes:")
        print(f"   CSV:  {csv_size:.2f} MB")
        print(f"   JSONL: {jsonl_size:.2f} MB")
        print(f"   Compression ratio: {(jsonl_size/csv_size)*100:.1f}%")
        
    except Exception as e:
        print(f"⚠️  Could not calculate file sizes: {e}")
    
    return True

def validate_jsonl_file(jsonl_file_path, sample_size=5):
    """
    Validate the JSONL file and show samples
    
    Args:
        jsonl_file_path (str): Path to JSONL file to validate
        sample_size (int): Number of sample records to display
    """
    
    print(f"\n🔍 Validating JSONL file: {jsonl_file_path}")
    print("-" * 80)
    
    try:
        valid_records = 0
        sample_records = []
        
        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Try to parse each line as JSON
                    record = json.loads(line.strip())
                    valid_records += 1
                    
                    # Collect samples
                    if len(sample_records) < sample_size:
                        sample_records.append(record)
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON on line {line_num}: {e}")
                    return False
        
        print(f"✅ Validation successful!")
        print(f"📊 Valid JSON records: {valid_records:,}")
        
        # Show sample records
        print(f"\n📋 Sample records (first {len(sample_records)}):")
        for i, record in enumerate(sample_records, 1):
            print(f"\n--- Sample Record {i} ---")
            print(f"ID: {record.get('id', 'N/A')}")
            print(f"Source: {record.get('source_dataset', 'N/A')}")
            print(f"Specialty: {record.get('medical_specialty', 'N/A')}")
            print(f"Keywords: {record.get('keywords', [])[:3]}..." if len(record.get('keywords', [])) > 3 else f"Keywords: {record.get('keywords', [])}")
            print(f"Text preview: {record.get('text', '')[:100]}...")
            print(f"Confidence: {record.get('confidence_score', 0)}")
            print(f"Text length: {record.get('text_length', 0)} chars")
            
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find JSONL file {jsonl_file_path}")
        return False
    except Exception as e:
        print(f"❌ Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    # File paths
    csv_input = "/project/workspace/DrZeepeads/Godzilla-dataset-/embedded_dat/godzilla_medical_dataset.csv"
    jsonl_output = "/project/workspace/godzilla_medical_dataset.jsonl"
    
    # Convert CSV to JSONL
    success = convert_csv_to_jsonl(csv_input, jsonl_output)
    
    if success:
        # Validate the output
        validate_jsonl_file(jsonl_output, sample_size=3)
    
    print("\n🦖 Godzilla JSONL conversion complete!")