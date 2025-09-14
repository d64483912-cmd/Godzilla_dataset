#!/usr/bin/env python3
"""
Upload Godzilla Medical Embeddings to Supabase
Uses pgvector for efficient vector storage and similarity search
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
import os
import requests
from supabase import create_client, Client
import asyncio

# Supabase Configuration
SUPABASE_URL = "https://bnjthwrpigvchbhsmfec.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuanRod3JwaWd2Y2hiaHNtZmVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc1MzE1OTksImV4cCI6MjA3MzEwNzU5OX0.okbuiEqTbdDEbkPFCT1w8-H46UrMHjm-4KXuyQ0PNBU"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuanRod3JwaWd2Y2hiaHNtZmVjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzUzMTU5OSwiZXhwIjoyMDczMTA3NTk5fQ.RAEuDn4bGpaHEQp8wpyKZcaoBh7wFegtX4mBaB932MU"

class SupabaseUploader:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        self.embeddings = None
        self.metadata = None
        
        print("🚀 Supabase Medical Embeddings Uploader")
        print(f"🔗 Connected to: {SUPABASE_URL}")
    
    def load_embeddings(self):
        """Load the generated embeddings and metadata"""
        print("📥 Loading embeddings and metadata...")
        
        try:
            # Load embeddings
            self.embeddings = np.load('fast_medical_embeddings.npy')
            
            # Load metadata
            with open('fast_medical_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            
            print(f"✅ Loaded {len(self.embeddings)} embeddings with {self.embeddings.shape[1]} dimensions")
            return True
            
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            print("💡 Make sure fast_hf_embeddings.py has completed successfully")
            return False
    
    def setup_database_schema(self):
        """Set up the database schema for medical embeddings"""
        print("🏗️ Setting up database schema...")
        
        # SQL to create the medical_embeddings table with pgvector
        create_table_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS vector;
        
        -- Create medical_embeddings table
        CREATE TABLE IF NOT EXISTS medical_embeddings (
            id SERIAL PRIMARY KEY,
            record_id TEXT UNIQUE NOT NULL,
            medical_specialty TEXT,
            confidence_score FLOAT,
            source_dataset TEXT,
            keywords TEXT,
            text_preview TEXT,
            full_text TEXT,
            embedding VECTOR(384),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_medical_specialty ON medical_embeddings(medical_specialty);
        CREATE INDEX IF NOT EXISTS idx_confidence_score ON medical_embeddings(confidence_score);
        CREATE INDEX IF NOT EXISTS idx_source_dataset ON medical_embeddings(source_dataset);
        CREATE INDEX IF NOT EXISTS idx_embedding_cosine ON medical_embeddings USING ivfflat (embedding vector_cosine_ops);
        """
        
        try:
            # Execute SQL using Supabase RPC
            result = self.supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
            print("✅ Database schema created successfully")
            return True
            
        except Exception as e:
            print(f"⚠️ Schema setup note: {e}")
            print("💡 You may need to enable pgvector extension manually in Supabase dashboard")
            return True  # Continue anyway, table might already exist
    
    def upload_embeddings_batch(self, batch_data, batch_num, total_batches):
        """Upload a batch of embeddings to Supabase"""
        try:
            result = self.supabase.table('medical_embeddings').insert(batch_data).execute()
            print(f"  ✅ Batch {batch_num}/{total_batches} uploaded successfully ({len(batch_data)} records)")
            return True
            
        except Exception as e:
            print(f"  ❌ Batch {batch_num} failed: {e}")
            return False
    
    def upload_to_supabase(self, batch_size=50):
        """Upload all embeddings to Supabase in batches"""
        print("🦖" * 20)
        print("GODZILLA MEDICAL DATASET → SUPABASE UPLOAD")
        print("🦖" * 20)
        
        start_time = datetime.now()
        
        # Load embeddings
        if not self.load_embeddings():
            return False
        
        # Setup database schema
        self.setup_database_schema()
        
        # Prepare data for upload
        print(f"🔧 Preparing {len(self.embeddings)} records for upload...")
        
        total_records = len(self.embeddings)
        total_batches = (total_records + batch_size - 1) // batch_size
        successful_uploads = 0
        failed_uploads = 0
        
        print(f"📦 Processing in {total_batches} batches of {batch_size} records each...")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_records)
            
            print(f"📤 Processing batch {batch_num + 1}/{total_batches} (records {start_idx + 1}-{end_idx})...")
            
            # Prepare batch data
            batch_data = []
            for i in range(start_idx, end_idx):
                record = {
                    'record_id': self.metadata[i]['id'],
                    'medical_specialty': self.metadata[i]['medical_specialty'],
                    'confidence_score': self.metadata[i]['confidence_score'],
                    'source_dataset': self.metadata[i]['source_dataset'],
                    'keywords': self.metadata[i]['keywords'],
                    'text_preview': self.metadata[i]['text_preview'],
                    'full_text': self.metadata[i]['full_text'],
                    'embedding': self.embeddings[i].tolist()  # Convert numpy array to list
                }
                batch_data.append(record)
            
            # Upload batch
            if self.upload_embeddings_batch(batch_data, batch_num + 1, total_batches):
                successful_uploads += len(batch_data)
            else:
                failed_uploads += len(batch_data)
        
        # Generate report
        end_time = datetime.now()
        duration = end_time - start_time
        
        report = {
            'upload_timestamp': end_time.isoformat(),
            'supabase_url': SUPABASE_URL,
            'total_records': total_records,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'success_rate': (successful_uploads / total_records) * 100,
            'duration_seconds': duration.total_seconds(),
            'embedding_dimensions': self.embeddings.shape[1],
            'batch_size': batch_size,
            'total_batches': total_batches
        }
        
        # Save report
        with open('supabase_upload_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n🎉 SUPABASE UPLOAD COMPLETE!")
        print(f"📊 Upload Summary:")
        print(f"   Total Records: {total_records:,}")
        print(f"   Successful: {successful_uploads:,}")
        print(f"   Failed: {failed_uploads:,}")
        print(f"   Success Rate: {report['success_rate']:.1f}%")
        print(f"   Duration: {duration.total_seconds():.1f} seconds")
        print(f"   Embedding Dimensions: {report['embedding_dimensions']}")
        
        if successful_uploads > 0:
            print(f"\n🚀 GODZILLA IS NOW POWERING SUPABASE! 🦖")
            print(f"🔗 Access your data at: {SUPABASE_URL}")
            
        return successful_uploads > 0
    
    def test_similarity_search(self, query_text="pediatric heart conditions", top_k=5):
        """Test similarity search functionality"""
        print(f"\n🔍 Testing similarity search for: '{query_text}'")
        
        try:
            # For testing, we'll use a simple text search first
            # In production, you'd generate embeddings for the query and use vector similarity
            result = self.supabase.table('medical_embeddings').select('*').ilike('full_text', f'%{query_text}%').limit(top_k).execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} similar records:")
                for i, record in enumerate(result.data, 1):
                    print(f"  {i}. Specialty: {record['medical_specialty']}")
                    print(f"     Keywords: {record['keywords']}")
                    print(f"     Preview: {record['text_preview'][:100]}...")
                    print()
            else:
                print("❌ No similar records found")
                
        except Exception as e:
            print(f"❌ Search test failed: {e}")

def create_supabase_search_functions():
    """Create SQL functions for vector similarity search"""
    search_functions_sql = """
    -- Function to search similar medical records
    CREATE OR REPLACE FUNCTION search_medical_embeddings(
        query_embedding VECTOR(384),
        match_threshold FLOAT DEFAULT 0.7,
        match_count INT DEFAULT 10
    )
    RETURNS TABLE (
        record_id TEXT,
        medical_specialty TEXT,
        keywords TEXT,
        text_preview TEXT,
        confidence_score FLOAT,
        similarity FLOAT
    )
    LANGUAGE SQL
    AS $$
        SELECT
            medical_embeddings.record_id,
            medical_embeddings.medical_specialty,
            medical_embeddings.keywords,
            medical_embeddings.text_preview,
            medical_embeddings.confidence_score,
            1 - (medical_embeddings.embedding <=> query_embedding) AS similarity
        FROM medical_embeddings
        WHERE 1 - (medical_embeddings.embedding <=> query_embedding) > match_threshold
        ORDER BY medical_embeddings.embedding <=> query_embedding
        LIMIT match_count;
    $$;
    
    -- Function to search by medical specialty
    CREATE OR REPLACE FUNCTION search_by_specialty(
        specialty_name TEXT,
        match_count INT DEFAULT 10
    )
    RETURNS TABLE (
        record_id TEXT,
        medical_specialty TEXT,
        keywords TEXT,
        text_preview TEXT,
        confidence_score FLOAT
    )
    LANGUAGE SQL
    AS $$
        SELECT
            record_id,
            medical_specialty,
            keywords,
            text_preview,
            confidence_score
        FROM medical_embeddings
        WHERE medical_specialty ILIKE '%' || specialty_name || '%'
        ORDER BY confidence_score DESC
        LIMIT match_count;
    $$;
    """
    
    with open('supabase_search_functions.sql', 'w') as f:
        f.write(search_functions_sql)
    
    print("✅ Created supabase_search_functions.sql")
    print("💡 Run this SQL in your Supabase SQL editor to enable advanced search functions")

def main():
    """Main function"""
    uploader = SupabaseUploader()
    
    # Check if embeddings are ready
    if not os.path.exists('fast_medical_embeddings.npy'):
        print("⏳ Waiting for embeddings to be generated...")
        print("💡 Run fast_hf_embeddings.py first to generate embeddings")
        return
    
    # Upload to Supabase
    success = uploader.upload_to_supabase()
    
    if success:
        # Test search functionality
        uploader.test_similarity_search()
        
        # Create search functions
        create_supabase_search_functions()
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. 🔗 Visit your Supabase dashboard: {SUPABASE_URL}")
        print(f"2. 📊 Check the 'medical_embeddings' table")
        print(f"3. 🔍 Run the SQL functions for advanced search")
        print(f"4. 🚀 Build your medical AI app with Supabase API!")

if __name__ == "__main__":
    main()
