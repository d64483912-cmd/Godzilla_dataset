#!/usr/bin/env python3
"""
Godzilla Medical Dataset Pinecone Uploader
Uploads the comprehensive medical dataset to Pinecone vector database
"""

import csv
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
import hashlib

# Try to import required libraries
try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("❌ Pinecone library not found. Installing...")
    os.system("pip install pinecone")
    from pinecone import Pinecone, ServerlessSpec

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ SentenceTransformers library not found. Installing...")
    os.system("pip install sentence-transformers")
    from sentence_transformers import SentenceTransformer

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

class GodzillaPineconeUploader:
    def __init__(self, api_key: str = None, environment: str = "us-east-1-aws"):
        """
        Initialize the Pinecone uploader
        
        Args:
            api_key: Pinecone API key (if None, will look for PINECONE_API_KEY env var)
            environment: Pinecone environment
        """
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment
        self.pc = None
        self.index = None
        self.model = None
        
        if not self.api_key:
            raise ValueError("❌ Pinecone API key required. Set PINECONE_API_KEY environment variable or pass api_key parameter")
    
    def initialize_pinecone(self):
        """Initialize Pinecone connection"""
        print("🔌 Initializing Pinecone connection...")
        try:
            self.pc = Pinecone(api_key=self.api_key)
            print("✅ Pinecone connection established")
        except Exception as e:
            print(f"❌ Failed to connect to Pinecone: {e}")
            raise
    
    def initialize_embedding_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the sentence transformer model for embeddings"""
        print(f"🤖 Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            print("✅ Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
    
    def create_or_get_index(self, index_name: str = "godzilla-medical", dimension: int = 384):
        """Create or get existing Pinecone index"""
        print(f"📊 Setting up Pinecone index: {index_name}")
        
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if index_name in index_names:
                print(f"✅ Index '{index_name}' already exists, connecting...")
                self.index = self.pc.Index(index_name)
            else:
                print(f"🆕 Creating new index '{index_name}'...")
                self.pc.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=self.environment.split('-')[0] + "-" + self.environment.split('-')[1] + "-" + self.environment.split('-')[2]
                    )
                )
                print("⏳ Waiting for index to be ready...")
                # Wait for index to be ready
                import time
                while not self.pc.describe_index(index_name).status['ready']:
                    time.sleep(1)
                
                self.index = self.pc.Index(index_name)
                print("✅ Index created and ready!")
            
            # Get index stats
            stats = self.index.describe_index_stats()
            print(f"📈 Index stats: {stats['total_vector_count']} vectors, {stats['dimension']} dimensions")
            
        except Exception as e:
            print(f"❌ Failed to setup index: {e}")
            raise
    
    def load_godzilla_dataset(self, csv_file: str = "godzilla_medical_dataset.csv") -> List[Dict]:
        """Load the Godzilla medical dataset from CSV"""
        print(f"📖 Loading Godzilla dataset from {csv_file}...")
        
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"❌ Dataset file not found: {csv_file}")
        
        records = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    records.append(row)
            
            print(f"✅ Loaded {len(records):,} records from dataset")
            return records
            
        except Exception as e:
            print(f"❌ Failed to load dataset: {e}")
            raise
    
    def create_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        print(f"🧠 Creating embeddings for {len(texts)} texts...")
        
        try:
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch, convert_to_tensor=False)
                embeddings.extend(batch_embeddings.tolist())
                
                if (i // batch_size + 1) % 10 == 0:
                    print(f"   Processed {i + len(batch):,}/{len(texts):,} texts...")
            
            print("✅ Embeddings created successfully")
            return embeddings
            
        except Exception as e:
            print(f"❌ Failed to create embeddings: {e}")
            raise
    
    def prepare_vectors(self, records: List[Dict]) -> List[Dict]:
        """Prepare vectors for Pinecone upload"""
        print("🔧 Preparing vectors for upload...")
        
        # Extract texts for embedding
        texts = []
        for record in records:
            # Combine text with key metadata for better embeddings
            combined_text = f"{record.get('text', '')} {record.get('medical_specialty', '')} {record.get('keywords', '')}"
            texts.append(combined_text[:8000])  # Limit text length
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        
        # Prepare vectors
        vectors = []
        for i, record in enumerate(records):
            # Create unique ID
            vector_id = record.get('id', f"godzilla_{i}")
            
            # Prepare metadata (Pinecone has limits on metadata size)
            metadata = {
                'source_dataset': record.get('source_dataset', ''),
                'medical_specialty': record.get('medical_specialty', ''),
                'keywords': record.get('keywords', '')[:500],  # Limit keywords length
                'confidence_score': float(record.get('confidence_score', 0.5)),
                'page_number': record.get('page_number', ''),
                'book_title': record.get('book_title', '')[:200],  # Limit title length
                'chapter_title': record.get('chapter_title', '')[:200],
                'age_groups': record.get('age_groups', ''),
                'clinical_relevance_score': float(record.get('clinical_relevance_score', 0.5)),
                'reading_difficulty': record.get('reading_difficulty', ''),
                'chunk_token_count': int(record.get('chunk_token_count', 0)),
                'text_preview': record.get('text', '')[:500],  # First 500 chars for preview
                'created_at': record.get('created_at', ''),
                'uploaded_at': datetime.now().isoformat()
            }
            
            vector = {
                'id': vector_id,
                'values': embeddings[i],
                'metadata': metadata
            }
            vectors.append(vector)
        
        print(f"✅ Prepared {len(vectors):,} vectors for upload")
        return vectors
    
    def upload_vectors(self, vectors: List[Dict], batch_size: int = 100):
        """Upload vectors to Pinecone in batches"""
        print(f"🚀 Uploading {len(vectors):,} vectors to Pinecone...")
        
        try:
            uploaded_count = 0
            failed_count = 0
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                
                try:
                    self.index.upsert(vectors=batch)
                    uploaded_count += len(batch)
                    
                    if (i // batch_size + 1) % 10 == 0:
                        print(f"   Uploaded {uploaded_count:,}/{len(vectors):,} vectors...")
                        
                except Exception as e:
                    print(f"⚠️ Failed to upload batch {i//batch_size + 1}: {e}")
                    failed_count += len(batch)
            
            print(f"✅ Upload complete! {uploaded_count:,} vectors uploaded, {failed_count} failed")
            
            # Get final index stats
            stats = self.index.describe_index_stats()
            print(f"📊 Final index stats: {stats['total_vector_count']} total vectors")
            
            return uploaded_count, failed_count
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            raise
    
    def upload_godzilla_dataset(self, 
                               csv_file: str = "godzilla_medical_dataset.csv",
                               index_name: str = "godzilla-medical",
                               model_name: str = "all-MiniLM-L6-v2"):
        """Complete pipeline to upload Godzilla dataset to Pinecone"""
        print("🦖" * 20)
        print("GODZILLA MEDICAL DATASET → PINECONE UPLOAD")
        print("🦖" * 20)
        
        try:
            # Initialize components
            self.initialize_pinecone()
            self.initialize_embedding_model(model_name)
            self.create_or_get_index(index_name, dimension=384)  # all-MiniLM-L6-v2 has 384 dimensions
            
            # Load and process data
            records = self.load_godzilla_dataset(csv_file)
            vectors = self.prepare_vectors(records)
            
            # Upload to Pinecone
            uploaded, failed = self.upload_vectors(vectors)
            
            # Save upload report
            report = {
                'upload_timestamp': datetime.now().isoformat(),
                'dataset_file': csv_file,
                'index_name': index_name,
                'embedding_model': model_name,
                'total_records': len(records),
                'vectors_uploaded': uploaded,
                'vectors_failed': failed,
                'success_rate': (uploaded / len(records)) * 100 if len(records) > 0 else 0
            }
            
            with open('pinecone_upload_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            print("\n" + "🦖" * 20)
            print("GODZILLA DATASET UPLOAD COMPLETE!")
            print("🦖" * 20)
            print(f"📊 Upload Summary:")
            print(f"   Total Records: {len(records):,}")
            print(f"   Vectors Uploaded: {uploaded:,}")
            print(f"   Success Rate: {report['success_rate']:.1f}%")
            print(f"   Index Name: {index_name}")
            print(f"   Embedding Model: {model_name}")
            print(f"📁 Upload Report: pinecone_upload_report.json")
            print("\n🚀 GODZILLA IS NOW POWERING PINECONE! 🦖")
            
            return report
            
        except Exception as e:
            print(f"\n❌ UPLOAD FAILED: {e}")
            raise

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload Godzilla Medical Dataset to Pinecone")
    parser.add_argument("--api-key", help="Pinecone API key (or set PINECONE_API_KEY env var)")
    parser.add_argument("--csv-file", default="godzilla_medical_dataset.csv", help="Path to Godzilla dataset CSV")
    parser.add_argument("--index-name", default="godzilla-medical", help="Pinecone index name")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Sentence transformer model name")
    parser.add_argument("--environment", default="us-east-1-aws", help="Pinecone environment")
    
    args = parser.parse_args()
    
    try:
        uploader = GodzillaPineconeUploader(api_key=args.api_key, environment=args.environment)
        uploader.upload_godzilla_dataset(
            csv_file=args.csv_file,
            index_name=args.index_name,
            model_name=args.model
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
