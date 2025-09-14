#!/usr/bin/env python3
"""
Test Pinecone Upload - Upload just a few records to test the connection
"""

import csv
import os
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

def test_pinecone_upload():
    """Test upload with just 5 records"""
    
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("❌ Please set PINECONE_API_KEY environment variable")
        return
    
    print("🦖 TESTING PINECONE CONNECTION")
    print("=" * 40)
    
    # Initialize Pinecone
    print("🔌 Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)
    
    # Load embedding model
    print("🤖 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Create or get index
    index_name = "godzilla-medical-test"
    print(f"📊 Setting up test index: {index_name}")
    
    existing_indexes = pc.list_indexes()
    index_names = [idx.name for idx in existing_indexes]
    
    if index_name not in index_names:
        print("🆕 Creating test index...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        
        # Wait for index to be ready
        import time
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
    
    index = pc.Index(index_name)
    
    # Load first 5 records from dataset
    print("📖 Loading test records...")
    records = []
    with open('godzilla_medical_dataset.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 5:  # Only take first 5 records
                break
            records.append(row)
    
    print(f"✅ Loaded {len(records)} test records")
    
    # Create embeddings
    print("🧠 Creating embeddings...")
    texts = []
    for record in records:
        combined_text = f"{record.get('text', '')} {record.get('medical_specialty', '')} {record.get('keywords', '')}"
        texts.append(combined_text[:8000])
    
    embeddings = model.encode(texts, convert_to_tensor=False)
    
    # Prepare vectors
    print("🔧 Preparing vectors...")
    vectors = []
    for i, record in enumerate(records):
        vector = {
            'id': f"test_{i}_{record.get('id', '')}",
            'values': embeddings[i].tolist(),
            'metadata': {
                'medical_specialty': record.get('medical_specialty', ''),
                'confidence_score': float(record.get('confidence_score', 0.5)),
                'text_preview': record.get('text', '')[:200],
                'source_dataset': record.get('source_dataset', ''),
                'test_upload': True
            }
        }
        vectors.append(vector)
    
    # Upload vectors
    print("🚀 Uploading test vectors...")
    index.upsert(vectors=vectors)
    
    # Test search
    print("🔍 Testing search...")
    query = "pediatric heart conditions"
    query_embedding = model.encode([query]).tolist()[0]
    
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True
    )
    
    print(f"📊 Search Results:")
    for i, match in enumerate(results['matches'], 1):
        print(f"  {i}. Score: {match['score']:.3f}")
        print(f"     Specialty: {match['metadata']['medical_specialty']}")
        print(f"     Text: {match['metadata']['text_preview'][:100]}...")
        print()
    
    # Get index stats
    stats = index.describe_index_stats()
    print(f"📈 Index Stats: {stats['total_vector_count']} vectors")
    
    print("✅ TEST SUCCESSFUL! Pinecone connection and upload working correctly.")
    print("🚀 Ready for full dataset upload!")
    
    return True

if __name__ == "__main__":
    test_pinecone_upload()
