#!/usr/bin/env python3
"""
Example: Using the Godzilla Medical Dataset in Pinecone
Demonstrates semantic search capabilities after upload
"""

import os
from sentence_transformers import SentenceTransformer

try:
    from pinecone import Pinecone
except ImportError:
    print("❌ Pinecone library not found. Installing...")
    os.system("pip install pinecone-client")
    from pinecone import Pinecone

def search_medical_knowledge(query: str, 
                           api_key: str = None,
                           index_name: str = "godzilla-medical",
                           top_k: int = 5):
    """
    Search the Godzilla Medical Dataset in Pinecone
    
    Args:
        query: Medical question or topic to search
        api_key: Pinecone API key
        index_name: Name of the Pinecone index
        top_k: Number of results to return
    """
    
    # Initialize Pinecone
    api_key = api_key or os.getenv('PINECONE_API_KEY')
    if not api_key:
        raise ValueError("❌ Pinecone API key required. Set PINECONE_API_KEY environment variable")
    
    print(f"🔍 Searching for: '{query}'")
    print("=" * 50)
    
    # Connect to Pinecone
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    
    # Load the same embedding model used for upload
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Create query embedding
    query_embedding = model.encode([query]).tolist()[0]
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Display results
    print(f"📊 Found {len(results['matches'])} relevant results:\n")
    
    for i, match in enumerate(results['matches'], 1):
        metadata = match['metadata']
        score = match['score']
        
        print(f"🏥 Result #{i} (Similarity: {score:.3f})")
        print(f"   Specialty: {metadata.get('medical_specialty', 'N/A')}")
        print(f"   Source: {metadata.get('source_dataset', 'N/A')}")
        print(f"   Quality Score: {metadata.get('confidence_score', 'N/A')}")
        print(f"   Age Groups: {metadata.get('age_groups', 'N/A')}")
        print(f"   Keywords: {metadata.get('keywords', 'N/A')[:100]}...")
        print(f"   Text Preview: {metadata.get('text_preview', 'N/A')[:200]}...")
        print(f"   Book: {metadata.get('book_title', 'N/A')}")
        if metadata.get('chapter_title'):
            print(f"   Chapter: {metadata.get('chapter_title', 'N/A')}")
        print("-" * 50)
    
    return results

def filtered_search_example():
    """Example of filtered searches"""
    
    print("\n🎯 FILTERED SEARCH EXAMPLES")
    print("=" * 50)
    
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("❌ Set PINECONE_API_KEY environment variable to run examples")
        return
    
    pc = Pinecone(api_key=api_key)
    index = pc.Index("godzilla-medical")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Example 1: Pediatrics only
    print("\n1️⃣ Pediatric Heart Conditions (Pediatrics Only)")
    query = "heart conditions in children"
    query_embedding = model.encode([query]).tolist()[0]
    
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter={"medical_specialty": "pediatrics"}
    )
    
    for match in results['matches']:
        print(f"   • {match['metadata']['text_preview'][:100]}... (Score: {match['score']:.3f})")
    
    # Example 2: High quality only
    print("\n2️⃣ High-Quality Medical Content (Score ≥ 0.9)")
    query = "treatment guidelines"
    query_embedding = model.encode([query]).tolist()[0]
    
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter={"confidence_score": {"$gte": 0.9}}
    )
    
    for match in results['matches']:
        print(f"   • {match['metadata']['text_preview'][:100]}... (Quality: {match['metadata']['confidence_score']})")
    
    # Example 3: Specific source
    print("\n3️⃣ Nelson Textbook Content Only")
    query = "developmental milestones"
    query_embedding = model.encode([query]).tolist()[0]
    
    results = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True,
        filter={"source_dataset": "nelson_enhanced"}
    )
    
    for match in results['matches']:
        print(f"   • {match['metadata']['text_preview'][:100]}... (Chapter: {match['metadata'].get('chapter_title', 'N/A')[:30]})")

def main():
    """Main function with example searches"""
    
    print("🦖" * 20)
    print("GODZILLA MEDICAL DATASET - PINECONE SEARCH EXAMPLES")
    print("🦖" * 20)
    
    # Check for API key
    if not os.getenv('PINECONE_API_KEY'):
        print("❌ Please set your PINECONE_API_KEY environment variable:")
        print("   export PINECONE_API_KEY='your-api-key-here'")
        return
    
    try:
        # Example searches
        example_queries = [
            "pediatric heart disease treatment",
            "diabetes management in children",
            "respiratory infections symptoms",
            "neurological development milestones",
            "emergency medicine protocols"
        ]
        
        for query in example_queries:
            print(f"\n{'='*60}")
            search_medical_knowledge(query, top_k=3)
        
        # Filtered search examples
        filtered_search_example()
        
        print(f"\n{'🦖'*20}")
        print("SEARCH EXAMPLES COMPLETE!")
        print("🦖" * 20)
        print("\n🚀 Your Godzilla Medical Dataset is ready for production use!")
        print("💡 Customize the search parameters for your specific use case.")
        
    except Exception as e:
        print(f"❌ Error during search: {e}")
        print("💡 Make sure you've uploaded the dataset first using upload_to_pinecone.py")

if __name__ == "__main__":
    main()
