-- Supabase Schema Setup for Godzilla Medical Embeddings
-- Run this SQL in your Supabase SQL Editor

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

-- Grant permissions (adjust as needed)
GRANT ALL ON medical_embeddings TO authenticated;
GRANT ALL ON medical_embeddings TO anon;

-- Enable Row Level Security (optional - uncomment if needed)
-- ALTER TABLE medical_embeddings ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access (optional - uncomment if needed)
-- CREATE POLICY "Public read access" ON medical_embeddings FOR SELECT USING (true);

SELECT 'Supabase schema setup complete! 🦖' as status;
