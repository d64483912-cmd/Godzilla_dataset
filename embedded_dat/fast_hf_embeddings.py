#!/usr/bin/env python3
"""
FAST Hugging Face Medical Embeddings Implementation
Optimized for speed while maintaining quality
"""

import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class FastMedicalEmbeddings:
    def __init__(self):
        """Initialize with optimized sentence-transformers model"""
        self.model = None
        self.embeddings = None
        self.metadata = None
        
        print("🤗 Fast Hugging Face Medical Embeddings")
        print("⚡ Optimized for speed and quality")
    
    def load_model(self, model_name="all-MiniLM-L6-v2"):
        """Load optimized sentence-transformers model"""
        print(f"📥 Loading model: {model_name}")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            print(f"✅ Model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def load_dataset(self, csv_path="godzilla_medical_dataset.csv"):
        """Load and prepare dataset"""
        print(f"📖 Loading dataset from {csv_path}...")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df)} records")
            
            # Prepare texts and metadata
            texts = []
            metadata = []
            
            for idx, row in df.iterrows():
                # Combine text fields for better embeddings
                combined_text = f"{row.get('text', '')} {row.get('medical_specialty', '')} {row.get('keywords', '')}"
                texts.append(combined_text[:4000])  # Reasonable length limit
                
                # Store metadata
                metadata.append({
                    'id': row.get('id', f'record_{idx}'),
                    'medical_specialty': row.get('medical_specialty', ''),
                    'confidence_score': float(row.get('confidence_score', 0.5)),
                    'source_dataset': row.get('source_dataset', ''),
                    'keywords': row.get('keywords', ''),
                    'text_preview': row.get('text', '')[:200],
                    'full_text': row.get('text', '')
                })
            
            self.metadata = metadata
            return texts
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return None
    
    def create_embeddings(self, csv_path="godzilla_medical_dataset.csv"):
        """Create embeddings quickly"""
        print("🦖" * 20)
        print("FAST GODZILLA MEDICAL EMBEDDINGS")
        print("🦖" * 20)
        
        start_time = datetime.now()
        
        # Load model
        if not self.load_model():
            return False
        
        # Load dataset
        texts = self.load_dataset(csv_path)
        if texts is None:
            return False
        
        # Generate embeddings (fast batch processing)
        print(f"⚡ Creating embeddings for {len(texts)} texts...")
        print("🚀 Using optimized batch processing...")
        
        self.embeddings = self.model.encode(
            texts,
            batch_size=64,  # Larger batch size for speed
            show_progress_bar=True,
            convert_to_tensor=False,
            normalize_embeddings=True  # Better for cosine similarity
        )
        
        print(f"✅ Generated {len(self.embeddings)} embeddings!")
        
        # Save everything
        self.save_embeddings()
        
        # Generate report
        end_time = datetime.now()
        duration = end_time - start_time
        
        report = {
            'model_name': self.model_name,
            'total_records': len(texts),
            'embedding_dimension': self.embeddings.shape[1],
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'storage_size_mb': self.embeddings.nbytes / (1024 * 1024),
            'embeddings_per_second': len(texts) / duration.total_seconds()
        }
        
        with open('fast_embeddings_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n🎉 EMBEDDINGS COMPLETED!")
        print(f"📊 Records: {len(texts):,}")
        print(f"🧠 Model: {self.model_name}")
        print(f"📐 Dimensions: {self.embeddings.shape[1]}")
        print(f"💾 Size: {report['storage_size_mb']:.1f} MB")
        print(f"⏱️ Duration: {duration.total_seconds():.1f} seconds")
        print(f"⚡ Speed: {report['embeddings_per_second']:.1f} embeddings/second")
        
        return True
    
    def save_embeddings(self):
        """Save embeddings and metadata"""
        print(f"💾 Saving embeddings and metadata...")
        
        # Save embeddings
        np.save('fast_medical_embeddings.npy', self.embeddings)
        
        # Save metadata
        with open('fast_medical_metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save complete package
        with open('fast_medical_complete.pkl', 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'metadata': self.metadata,
                'model_name': self.model_name
            }, f)
        
        print(f"✅ Saved to:")
        print(f"  - fast_medical_embeddings.npy")
        print(f"  - fast_medical_metadata.json")
        print(f"  - fast_medical_complete.pkl")
    
    def load_embeddings(self):
        """Load saved embeddings"""
        try:
            self.embeddings = np.load('fast_medical_embeddings.npy')
            with open('fast_medical_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            print(f"✅ Loaded {len(self.embeddings)} embeddings")
            return True
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return False
    
    def search(self, query, top_k=5):
        """Fast semantic search"""
        if self.embeddings is None:
            if not self.load_embeddings():
                print("❌ No embeddings found!")
                return []
        
        if self.model is None:
            if not self.load_model():
                return []
        
        print(f"🔍 Searching: '{query}'")
        
        # Generate query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)
        
        # Calculate similarities (fast with normalized embeddings)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            results.append({
                'rank': i + 1,
                'similarity': float(similarities[idx]),
                'metadata': self.metadata[idx]
            })
        
        return results
    
    def print_results(self, results):
        """Pretty print search results"""
        print(f"\n📋 SEARCH RESULTS:")
        print("=" * 80)
        
        for result in results:
            print(f"\n🏥 #{result['rank']} | Score: {result['similarity']:.3f}")
            print(f"📝 Specialty: {result['metadata']['medical_specialty']}")
            print(f"🔑 Keywords: {result['metadata']['keywords']}")
            print(f"📄 Text: {result['metadata']['text_preview']}...")
            print("-" * 80)

def main():
    """Main implementation"""
    embedder = FastMedicalEmbeddings()
    
    # Create embeddings
    print("🚀 Starting fast embedding creation...")
    success = embedder.create_embeddings()
    
    if success:
        # Test search
        print(f"\n🔍 Testing search functionality...")
        
        test_queries = [
            "pediatric heart conditions",
            "diabetes treatment",
            "respiratory infections"
        ]
        
        for query in test_queries:
            results = embedder.search(query, top_k=3)
            embedder.print_results(results)
        
        print(f"\n🎯 SUCCESS! Your medical search system is ready!")
        print(f"💰 Total cost: $0")
        print(f"⚡ Fast and efficient!")

if __name__ == "__main__":
    main()
