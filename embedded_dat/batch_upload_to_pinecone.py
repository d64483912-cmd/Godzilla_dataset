#!/usr/bin/env python3
"""
Batch Upload to Pinecone - Process dataset in smaller chunks to avoid memory issues
"""

import csv
import os
import json
import time
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

def batch_upload_to_pinecone(batch_size=100, max_text_length=8000):
    """Upload dataset to Pinecone in batches"""
    
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("❌ Please set PINECONE_API_KEY environment variable")
        return False
    
    print("🦖" * 20)
    print("GODZILLA MEDICAL DATASET → PINECONE BATCH UPLOAD")
    print("🦖" * 20)
    
    start_time = datetime.now()
    
    # Initialize Pinecone
    print("🔌 Initializing Pinecone connection...")
    pc = Pinecone(api_key=api_key)
    print("✅ Pinecone connection established")
    
    # Load embedding model
    print("🤖 Loading embedding model: all-MiniLM-L6-v2")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Embedding model loaded successfully")
    
    # Setup index
    index_name = "godzilla-medical"
    print(f"📊 Setting up Pinecone index: {index_name}")
    
    existing_indexes = pc.list_indexes()
    index_names = [idx.name for idx in existing_indexes]
    
    if index_name not in index_names:
        print("🆕 Creating new index...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        
        # Wait for index to be ready
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    else:
        print("✅ Index already exists, connecting...")
    
    index = pc.Index(index_name)
    
    # Get initial stats
    initial_stats = index.describe_index_stats()
    print(f"📈 Index stats: {initial_stats['total_vector_count']} vectors, {initial_stats.get('dimension', 384)} dimensions")
    
    # Load dataset
    print("📖 Loading Godzilla dataset from godzilla_medical_dataset.csv...")
    records = []
    with open('godzilla_medical_dataset.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    
    total_records = len(records)
    print(f"✅ Loaded {total_records:,} records from dataset")
    
    # Process in batches
    print(f"🔧 Processing in batches of {batch_size} records...")
    
    uploaded_count = 0
    failed_count = 0
    
    for batch_start in range(0, total_records, batch_size):
        batch_end = min(batch_start + batch_size, total_records)
        batch_records = records[batch_start:batch_end]
        
        print(f"📦 Processing batch {batch_start//batch_size + 1}/{(total_records + batch_size - 1)//batch_size} ({batch_start+1}-{batch_end}/{total_records})")
        
        try:
            # Prepare texts for this batch
            texts = []
            for record in batch_records:
                combined_text = f"{record.get('text', '')} {record.get('medical_specialty', '')} {record.get('keywords', '')}"
                texts.append(combined_text[:max_text_length])
            
            # Create embeddings for this batch
            print(f"  🧠 Creating embeddings for {len(texts)} texts...")
            embeddings = model.encode(texts, convert_to_tensor=False, show_progress_bar=False)
            
            # Prepare vectors
            vectors = []
            for i, record in enumerate(batch_records):
                vector = {
                    'id': f"godzilla_{batch_start + i}_{record.get('id', '')}",
                    'values': embeddings[i].tolist(),
                    'metadata': {
                        'medical_specialty': record.get('medical_specialty', ''),
                        'confidence_score': float(record.get('confidence_score', 0.5)),
                        'text_preview': record.get('text', '')[:200],
                        'source_dataset': record.get('source_dataset', ''),
                        'keywords': record.get('keywords', ''),
                        'batch_number': batch_start // batch_size + 1
                    }
                }
                vectors.append(vector)
            
            # Upload vectors to Pinecone
            print(f"  🚀 Uploading {len(vectors)} vectors to Pinecone...")
            index.upsert(vectors=vectors)
            
            uploaded_count += len(vectors)
            print(f"  ✅ Batch uploaded successfully! Total uploaded: {uploaded_count:,}/{total_records:,}")
            
            # Small delay to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error processing batch {batch_start//batch_size + 1}: {e}")
            failed_count += len(batch_records)
            continue
    
    # Final verification
    print(f"\n🔍 Verifying upload...")
    time.sleep(5)  # Wait for Pinecone to update stats
    
    final_stats = index.describe_index_stats()
    final_count = final_stats['total_vector_count']
    
    print(f"📊 Final index stats: {final_count:,} vectors")
    
    # Test search
    print(f"🔍 Testing search functionality...")
    try:
        query = "pediatric heart conditions treatment"
        query_embedding = model.encode([query]).tolist()[0]
        
        results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )
        
        print(f"📋 Search Results for '{query}':")
        for i, match in enumerate(results['matches'], 1):
            print(f"  {i}. Score: {match['score']:.3f}")
            print(f"     Specialty: {match['metadata']['medical_specialty']}")
            print(f"     Text: {match['metadata']['text_preview'][:100]}...")
            print()
    
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    # Generate report
    end_time = datetime.now()
    duration = end_time - start_time
    
    report = {
        'upload_completed': True,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': duration.total_seconds(),
        'total_records': total_records,
        'vectors_uploaded': uploaded_count,
        'vectors_failed': failed_count,
        'success_rate': (uploaded_count / total_records) * 100 if total_records > 0 else 0,
        'final_vector_count': final_count,
        'index_name': index_name,
        'embedding_model': 'all-MiniLM-L6-v2',
        'batch_size': batch_size,
        'max_text_length': max_text_length
    }
    
    with open('pinecone_batch_upload_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n🎉 UPLOAD COMPLETED!")
    print(f"📊 Total Records: {total_records:,}")
    print(f"🚀 Vectors Uploaded: {uploaded_count:,}")
    print(f"❌ Failed: {failed_count:,}")
    print(f"📈 Success Rate: {report['success_rate']:.1f}%")
    print(f"⏱️ Duration: {duration.total_seconds():.1f} seconds")
    print(f"📋 Report saved to: pinecone_batch_upload_report.json")
    
    return uploaded_count > 0

if __name__ == "__main__":
    success = batch_upload_to_pinecone(batch_size=100)
    if success:
        print("✅ Batch upload completed successfully!")
    else:
        print("❌ Batch upload failed!")
