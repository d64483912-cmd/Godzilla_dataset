#!/usr/bin/env python3
"""
Interactive Medical Search Interface
Uses the fast Hugging Face embeddings
"""

import json
import numpy as np
from fast_hf_embeddings import FastMedicalEmbeddings

def main():
    """Interactive search interface"""
    print("🦖" * 30)
    print("GODZILLA MEDICAL SEARCH INTERFACE")
    print("🦖" * 30)
    
    # Initialize embedder
    embedder = FastMedicalEmbeddings()
    
    # Load embeddings
    print("📥 Loading embeddings...")
    if not embedder.load_embeddings():
        print("❌ No embeddings found! Please wait for fast_hf_embeddings.py to complete.")
        return
    
    # Load model
    if not embedder.load_model():
        print("❌ Failed to load model!")
        return
    
    print(f"✅ Loaded {len(embedder.embeddings)} medical records")
    print(f"🧠 Model: {embedder.model_name}")
    print(f"📐 Dimensions: {embedder.embeddings.shape[1]}")
    
    print("\n🔍 MEDICAL SEARCH READY!")
    print("Enter your medical queries (type 'quit' to exit)")
    print("=" * 60)
    
    # Demo queries
    demo_queries = [
        "pediatric heart conditions treatment",
        "diabetes management in elderly patients",
        "respiratory infections in children",
        "neurological symptoms diagnosis",
        "cancer screening procedures"
    ]
    
    print("\n💡 Try these example queries:")
    for i, query in enumerate(demo_queries, 1):
        print(f"  {i}. {query}")
    print()
    
    while True:
        try:
            query = input("🏥 Medical Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            # Check if it's a demo query number
            if query.isdigit() and 1 <= int(query) <= len(demo_queries):
                query = demo_queries[int(query) - 1]
                print(f"🔍 Using demo query: '{query}'")
            
            # Search
            results = embedder.search(query, top_k=5)
            
            if results:
                embedder.print_results(results)
            else:
                print("❌ No results found.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
