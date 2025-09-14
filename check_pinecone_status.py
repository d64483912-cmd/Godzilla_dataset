#!/usr/bin/env python3
"""
Check Pinecone index status and storage
"""

import os
from pinecone import Pinecone

def check_pinecone_status():
    """Check the current status of Pinecone index"""
    
    api_key = os.getenv('PINECONE_API_KEY')
    if not api_key:
        print("❌ Please set PINECONE_API_KEY environment variable")
        return
    
    print("🦖 CHECKING PINECONE INDEX STATUS")
    print("=" * 40)
    
    # Initialize Pinecone
    print("🔌 Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)
    
    # List all indexes
    print("📊 Available indexes:")
    indexes = pc.list_indexes()
    for idx in indexes:
        print(f"  - {idx.name}: {idx.dimension} dimensions, {idx.metric} metric")
    
    # Check godzilla-medical index specifically
    index_name = "godzilla-medical"
    if any(idx.name == index_name for idx in indexes):
        print(f"\n🏥 Checking '{index_name}' index details...")
        
        # Get index object
        index = pc.Index(index_name)
        
        # Get detailed stats
        stats = index.describe_index_stats()
        print(f"📈 Index Statistics:")
        print(f"  - Total vectors: {stats.get('total_vector_count', 0):,}")
        print(f"  - Dimension: {stats.get('dimension', 'N/A')}")
        print(f"  - Index fullness: {stats.get('index_fullness', 0):.4f}")
        
        # Check namespaces
        namespaces = stats.get('namespaces', {})
        if namespaces:
            print(f"  - Namespaces:")
            for ns_name, ns_stats in namespaces.items():
                print(f"    * {ns_name}: {ns_stats.get('vector_count', 0):,} vectors")
        else:
            print(f"  - No namespaces (using default)")
        
        # Try a simple query to test if vectors exist
        print(f"\n🔍 Testing vector retrieval...")
        try:
            # Create a dummy query vector (384 dimensions)
            dummy_query = [0.1] * 384
            results = index.query(
                vector=dummy_query,
                top_k=1,
                include_metadata=True
            )
            
            if results['matches']:
                print(f"✅ Found vectors! Top match score: {results['matches'][0]['score']:.4f}")
                print(f"   Metadata: {results['matches'][0].get('metadata', {})}")
            else:
                print(f"❌ No vectors found in index")
                
        except Exception as e:
            print(f"❌ Error querying index: {e}")
    
    else:
        print(f"❌ Index '{index_name}' not found!")
    
    # Check test index too
    test_index_name = "godzilla-medical-test"
    if any(idx.name == test_index_name for idx in indexes):
        print(f"\n🧪 Checking test index '{test_index_name}'...")
        test_index = pc.Index(test_index_name)
        test_stats = test_index.describe_index_stats()
        print(f"📊 Test index vectors: {test_stats.get('total_vector_count', 0):,}")

if __name__ == "__main__":
    check_pinecone_status()
