#!/usr/bin/env python3
"""
Upload Godzilla Medical Dataset Embeddings to Hugging Face Hub
Completely free hosting and sharing!
"""

import json
import numpy as np
import pandas as pd
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi, login
import os

def upload_to_hf_hub():
    """Upload embeddings and metadata to Hugging Face Hub"""
    print("🤗" * 20)
    print("UPLOAD TO HUGGING FACE HUB")
    print("🤗" * 20)
    
    # Check if embeddings exist
    if not os.path.exists('godzilla_medical_embeddings.npy'):
        print("❌ No embeddings found! Run huggingface_medical_embeddings.py first.")
        return False
    
    if not os.path.exists('godzilla_medical_metadata.json'):
        print("❌ No metadata found! Run huggingface_medical_embeddings.py first.")
        return False
    
    # Load embeddings and metadata
    print("📥 Loading embeddings and metadata...")
    embeddings = np.load('godzilla_medical_embeddings.npy')
    
    with open('godzilla_medical_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    print(f"✅ Loaded {len(embeddings)} embeddings with {embeddings.shape[1]} dimensions")
    
    # Prepare dataset
    print("🔧 Preparing dataset for upload...")
    
    # Convert embeddings to list format for datasets
    embeddings_list = embeddings.tolist()
    
    # Create dataset dictionary
    dataset_dict = {
        'id': [item['id'] for item in metadata],
        'medical_specialty': [item['medical_specialty'] for item in metadata],
        'confidence_score': [item['confidence_score'] for item in metadata],
        'source_dataset': [item['source_dataset'] for item in metadata],
        'keywords': [item['keywords'] for item in metadata],
        'text_preview': [item['text_preview'] for item in metadata],
        'full_text': [item['full_text'] for item in metadata],
        'embeddings': embeddings_list
    }
    
    # Create Hugging Face Dataset
    dataset = Dataset.from_dict(dataset_dict)
    
    print(f"📊 Dataset created with {len(dataset)} records")
    print(f"📐 Embedding dimensions: {len(embeddings_list[0])}")
    
    # Dataset info
    dataset_info = {
        'description': 'Godzilla Medical Dataset with BioBERT embeddings for semantic search',
        'total_records': len(dataset),
        'embedding_model': 'microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract',
        'embedding_dimensions': len(embeddings_list[0]),
        'medical_specialties': list(set([item['medical_specialty'] for item in metadata])),
        'source_datasets': list(set([item['source_dataset'] for item in metadata]))
    }
    
    # Save dataset info
    with open('dataset_info.json', 'w') as f:
        json.dump(dataset_info, f, indent=2)
    
    print("\n🎯 Dataset ready for upload!")
    print("📋 Dataset Info:")
    print(f"  - Records: {dataset_info['total_records']:,}")
    print(f"  - Model: {dataset_info['embedding_model']}")
    print(f"  - Dimensions: {dataset_info['embedding_dimensions']}")
    print(f"  - Specialties: {len(dataset_info['medical_specialties'])}")
    
    # Instructions for manual upload
    print("\n🚀 TO UPLOAD TO HUGGING FACE HUB:")
    print("1. Install huggingface_hub: pip install huggingface_hub")
    print("2. Login: huggingface-cli login")
    print("3. Run this script with your username:")
    print("   python upload_to_huggingface.py your-hf-username")
    
    return True

def upload_with_username(username):
    """Upload to HF Hub with username"""
    try:
        # Load dataset
        embeddings = np.load('godzilla_medical_embeddings.npy')
        with open('godzilla_medical_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        # Prepare dataset
        embeddings_list = embeddings.tolist()
        dataset_dict = {
            'id': [item['id'] for item in metadata],
            'medical_specialty': [item['medical_specialty'] for item in metadata],
            'confidence_score': [item['confidence_score'] for item in metadata],
            'source_dataset': [item['source_dataset'] for item in metadata],
            'keywords': [item['keywords'] for item in metadata],
            'text_preview': [item['text_preview'] for item in metadata],
            'full_text': [item['full_text'] for item in metadata],
            'embeddings': embeddings_list
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        
        # Upload to Hub
        repo_name = f"{username}/godzilla-medical-embeddings"
        print(f"🚀 Uploading to {repo_name}...")
        
        dataset.push_to_hub(repo_name, private=False)
        
        print(f"✅ Successfully uploaded to: https://huggingface.co/datasets/{repo_name}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("💡 Make sure you're logged in: huggingface-cli login")
        return False

def create_gradio_app():
    """Create a Gradio app for the medical search"""
    gradio_code = '''
import gradio as gr
import numpy as np
import json
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset from HF Hub
dataset = load_dataset("your-username/godzilla-medical-embeddings")
embeddings = np.array(dataset["train"]["embeddings"])
metadata = dataset["train"]

# Load model
model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def search_medical_records(query, top_k=5):
    """Search medical records"""
    # Generate query embedding
    inputs = tokenizer(query, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        query_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    
    # Calculate similarities
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    
    # Get top results
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            "similarity": float(similarities[idx]),
            "specialty": metadata["medical_specialty"][idx],
            "text": metadata["text_preview"][idx],
            "keywords": metadata["keywords"][idx]
        })
    
    return results

# Create Gradio interface
iface = gr.Interface(
    fn=search_medical_records,
    inputs=[
        gr.Textbox(label="Medical Query", placeholder="Enter your medical search query..."),
        gr.Slider(1, 10, value=5, label="Number of Results")
    ],
    outputs=gr.JSON(label="Search Results"),
    title="🦖 Godzilla Medical Search",
    description="Search through medical records using BioBERT embeddings"
)

if __name__ == "__main__":
    iface.launch()
'''
    
    with open('gradio_medical_search.py', 'w') as f:
        f.write(gradio_code)
    
    print("✅ Created gradio_medical_search.py")
    print("🚀 Upload this to HF Spaces for a free web interface!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        upload_with_username(username)
    else:
        upload_to_hf_hub()
        create_gradio_app()
