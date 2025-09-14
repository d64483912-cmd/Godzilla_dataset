#!/usr/bin/env python3
"""
Simple Medical Search Interface for Godzilla Dataset
Uses the generated Hugging Face embeddings for search
"""

import json
import numpy as np
from huggingface_medical_embeddings import GodzillaMedicalEmbeddings

def interactive_search():
    """Interactive search interface"""
    print("🦖" * 20)
    print("GODZILLA MEDICAL SEARCH INTERFACE")
    print("🦖" * 20)
    
    # Initialize embedder
    embedder = GodzillaMedicalEmbeddings()
    
    # Load existing embeddings
    print("📥 Loading embeddings...")
    if not embedder.load_embeddings():
        print("❌ No embeddings found! Please run huggingface_medical_embeddings.py first.")
        return
    
    # Load model for query processing
    if not embedder.load_model():
        print("❌ Failed to load model!")
        return
    
    print(f"✅ Loaded {len(embedder.embeddings)} medical records")
    print(f"🧠 Model: {embedder.model_name}")
    print("\n🔍 Enter your medical queries (type 'quit' to exit):")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n🏥 Medical Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            # Search
            results = embedder.search(query, top_k=5)
            
            if results:
                embedder.print_search_results(results)
            else:
                print("❌ No results found.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_searches():
    """Run some demo searches"""
    print("🦖 DEMO MEDICAL SEARCHES")
    print("=" * 40)
    
    embedder = GodzillaMedicalEmbeddings()
    
    # Load embeddings
    if not embedder.load_embeddings():
        print("❌ No embeddings found!")
        return
    
    if not embedder.load_model():
        print("❌ Failed to load model!")
        return
    
    demo_queries = [
        "pediatric heart conditions",
        "diabetes treatment options",
        "respiratory infections in children",
        "neurological disorders symptoms",
        "cancer diagnosis procedures"
    ]
    
    for query in demo_queries:
        print(f"\n🔍 Demo Query: '{query}'")
        print("-" * 50)
        
        results = embedder.search(query, top_k=3)
        
        if results:
            for result in results:
                print(f"🏥 Similarity: {result['similarity']:.3f}")
                print(f"📝 Specialty: {result['metadata']['medical_specialty']}")
                print(f"📄 Text: {result['metadata']['text_preview'][:150]}...")
                print()
        else:
            print("❌ No results found.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_searches()
    else:
        interactive_search()
