#!/usr/bin/env python3
"""
FREE Hugging Face Medical Embeddings for Godzilla Dataset
Uses BioBERT for medical-specialized embeddings - completely free!
"""

import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class GodzillaMedicalEmbeddings:
    def __init__(self, model_name="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"):
        """
        Initialize with BioBERT model for medical text
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.embeddings = None
        self.metadata = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print(f"🤗 Initializing Hugging Face Medical Embeddings")
        print(f"🏥 Model: {model_name}")
        print(f"💻 Device: {self.device}")
    
    def load_model(self):
        """Load BioBERT model and tokenizer"""
        print(f"📥 Loading BioBERT model...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print(f"🔄 Falling back to sentence-transformers...")
            
            # Fallback to sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.model_name = 'all-MiniLM-L6-v2'
                print(f"✅ Fallback model loaded!")
                return True
            except Exception as e2:
                print(f"❌ Fallback failed: {e2}")
                return False
    
    def get_embeddings(self, texts, batch_size=32):
        """Generate embeddings for texts using BioBERT"""
        print(f"🧠 Generating embeddings for {len(texts)} texts...")
        
        if isinstance(self.model, torch.nn.Module):
            # Using transformers model
            embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                print(f"  Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
                
                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors='pt'
                ).to(self.device)
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # Use CLS token embedding
                    batch_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                    embeddings.extend(batch_embeddings)
            
            return np.array(embeddings)
        
        else:
            # Using sentence-transformers
            print(f"  Using sentence-transformers for embedding generation...")
            return self.model.encode(texts, show_progress_bar=True, convert_to_tensor=False)
    
    def load_dataset(self, csv_path="godzilla_medical_dataset.csv"):
        """Load Godzilla medical dataset"""
        print(f"📖 Loading dataset from {csv_path}...")
        
        try:
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df)} records")
            
            # Prepare texts for embedding
            texts = []
            metadata = []
            
            for idx, row in df.iterrows():
                # Combine relevant text fields
                combined_text = f"{row.get('text', '')} {row.get('medical_specialty', '')} {row.get('keywords', '')}"
                texts.append(combined_text[:8000])  # Limit text length
                
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
        """Create embeddings for the entire dataset"""
        print(f"🦖" * 20)
        print("GODZILLA MEDICAL DATASET → HUGGING FACE EMBEDDINGS")
        print(f"🦖" * 20)
        
        start_time = datetime.now()
        
        # Load model
        if not self.load_model():
            return False
        
        # Load dataset
        texts = self.load_dataset(csv_path)
        if texts is None:
            return False
        
        # Generate embeddings
        self.embeddings = self.get_embeddings(texts)
        
        # Save embeddings and metadata
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
            'device_used': str(self.device),
            'storage_size_mb': self.embeddings.nbytes / (1024 * 1024)
        }
        
        with open('huggingface_embeddings_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n🎉 EMBEDDINGS CREATED SUCCESSFULLY!")
        print(f"📊 Records: {len(texts):,}")
        print(f"🧠 Model: {self.model_name}")
        print(f"📐 Dimensions: {self.embeddings.shape[1]}")
        print(f"💾 Size: {report['storage_size_mb']:.1f} MB")
        print(f"⏱️ Duration: {duration.total_seconds():.1f} seconds")
        
        return True
    
    def save_embeddings(self):
        """Save embeddings and metadata to files"""
        print(f"💾 Saving embeddings and metadata...")
        
        # Save embeddings as numpy array
        np.save('godzilla_medical_embeddings.npy', self.embeddings)
        
        # Save metadata as JSON
        with open('godzilla_medical_metadata.json', 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save as pickle for easy loading
        with open('godzilla_medical_complete.pkl', 'wb') as f:
            pickle.dump({
                'embeddings': self.embeddings,
                'metadata': self.metadata,
                'model_name': self.model_name
            }, f)
        
        print(f"✅ Saved to:")
        print(f"  - godzilla_medical_embeddings.npy")
        print(f"  - godzilla_medical_metadata.json")
        print(f"  - godzilla_medical_complete.pkl")
    
    def load_embeddings(self):
        """Load previously saved embeddings"""
        try:
            self.embeddings = np.load('godzilla_medical_embeddings.npy')
            with open('godzilla_medical_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            print(f"✅ Loaded {len(self.embeddings)} embeddings")
            return True
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            return False
    
    def search(self, query, top_k=5):
        """Search for similar medical records"""
        if self.embeddings is None or self.metadata is None:
            if not self.load_embeddings():
                print("❌ No embeddings found. Run create_embeddings() first.")
                return []
        
        if self.model is None:
            if not self.load_model():
                return []
        
        print(f"🔍 Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.get_embeddings([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            result = {
                'rank': i + 1,
                'similarity': float(similarities[idx]),
                'metadata': self.metadata[idx]
            }
            results.append(result)
        
        return results
    
    def print_search_results(self, results):
        """Pretty print search results"""
        print(f"\n📋 SEARCH RESULTS:")
        print("=" * 80)
        
        for result in results:
            print(f"\n🏥 Rank {result['rank']} | Similarity: {result['similarity']:.3f}")
            print(f"📝 Specialty: {result['metadata']['medical_specialty']}")
            print(f"🔑 Keywords: {result['metadata']['keywords']}")
            print(f"📄 Text: {result['metadata']['text_preview']}...")
            print("-" * 80)

def main():
    """Main function to create embeddings"""
    embedder = GodzillaMedicalEmbeddings()
    
    # Create embeddings
    success = embedder.create_embeddings()
    
    if success:
        # Test search
        print(f"\n🔍 Testing search functionality...")
        results = embedder.search("pediatric heart conditions treatment", top_k=3)
        embedder.print_search_results(results)
        
        print(f"\n🎯 Ready for use! Your medical dataset is now searchable with BioBERT embeddings!")
        print(f"💰 Total cost: $0 (completely free!)")

if __name__ == "__main__":
    main()
