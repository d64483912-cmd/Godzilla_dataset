#!/usr/bin/env python3
"""
Upload Godzilla Medical Embeddings to Hugging Face Datasets Hub
Free hosting and sharing for your medical search system!
"""

import json
import numpy as np
import pandas as pd
from datasets import Dataset
import os

def prepare_dataset():
    """Prepare dataset for Hugging Face Hub"""
    print("🤗" * 20)
    print("PREPARE FOR HUGGING FACE DATASETS")
    print("🤗" * 20)
    
    # Check if files exist
    if not os.path.exists('fast_medical_embeddings.npy'):
        print("❌ No embeddings found! Run fast_hf_embeddings.py first.")
        return None
    
    if not os.path.exists('fast_medical_metadata.json'):
        print("❌ No metadata found! Run fast_hf_embeddings.py first.")
        return None
    
    # Load data
    print("📥 Loading embeddings and metadata...")
    embeddings = np.load('fast_medical_embeddings.npy')
    
    with open('fast_medical_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    print(f"✅ Loaded {len(embeddings)} embeddings with {embeddings.shape[1]} dimensions")
    
    # Prepare dataset dictionary
    print("🔧 Preparing dataset...")
    
    dataset_dict = {
        'id': [item['id'] for item in metadata],
        'medical_specialty': [item['medical_specialty'] for item in metadata],
        'confidence_score': [item['confidence_score'] for item in metadata],
        'source_dataset': [item['source_dataset'] for item in metadata],
        'keywords': [item['keywords'] for item in metadata],
        'text_preview': [item['text_preview'] for item in metadata],
        'full_text': [item['full_text'] for item in metadata],
        'embeddings': embeddings.tolist()  # Convert to list for JSON serialization
    }
    
    # Create dataset
    dataset = Dataset.from_dict(dataset_dict)
    
    print(f"📊 Dataset created:")
    print(f"  - Records: {len(dataset):,}")
    print(f"  - Embedding dimensions: {len(dataset_dict['embeddings'][0])}")
    print(f"  - Features: {list(dataset.features.keys())}")
    
    return dataset

def create_dataset_card():
    """Create a dataset card for Hugging Face"""
    card_content = """---
license: mit
task_categories:
- text-retrieval
- semantic-similarity
language:
- en
tags:
- medical
- healthcare
- embeddings
- semantic-search
- biomedical
size_categories:
- 1K<n<10K
---

# 🦖 Godzilla Medical Dataset with Embeddings

This dataset contains medical text records with pre-computed embeddings for semantic search.

## Dataset Description

- **Total Records**: 9,616 medical text records
- **Embedding Model**: all-MiniLM-L6-v2 (sentence-transformers)
- **Embedding Dimensions**: 384
- **Use Case**: Medical semantic search and similarity matching

## Features

- `id`: Unique identifier for each record
- `medical_specialty`: Medical specialty category
- `confidence_score`: Confidence score for the record
- `source_dataset`: Original source of the data
- `keywords`: Medical keywords associated with the text
- `text_preview`: First 200 characters of the medical text
- `full_text`: Complete medical text
- `embeddings`: 384-dimensional embedding vector

## Usage

```python
from datasets import load_dataset
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
dataset = load_dataset("your-username/godzilla-medical-embeddings")

# Extract embeddings and metadata
embeddings = np.array(dataset["train"]["embeddings"])
texts = dataset["train"]["text_preview"]

# Example: Find similar medical records
query_embedding = embeddings[0:1]  # Use first record as query
similarities = cosine_similarity(query_embedding, embeddings)[0]
top_indices = np.argsort(similarities)[::-1][:5]

print("Top 5 similar records:")
for idx in top_indices:
    print(f"Similarity: {similarities[idx]:.3f}")
    print(f"Text: {texts[idx]}")
    print()
```

## Medical Specialties Included

The dataset covers various medical specialties including but not limited to:
- Cardiology
- Pediatrics
- Neurology
- Oncology
- Respiratory Medicine
- And many more...

## License

This dataset is released under the MIT License.

## Citation

If you use this dataset in your research, please cite:

```
@dataset{godzilla_medical_embeddings,
  title={Godzilla Medical Dataset with Embeddings},
  author={Your Name},
  year={2024},
  url={https://huggingface.co/datasets/your-username/godzilla-medical-embeddings}
}
```
"""
    
    with open('README.md', 'w') as f:
        f.write(card_content)
    
    print("✅ Created README.md dataset card")

def main():
    """Main function"""
    # Prepare dataset
    dataset = prepare_dataset()
    if dataset is None:
        return
    
    # Create dataset card
    create_dataset_card()
    
    # Save locally for inspection
    print("💾 Saving dataset locally...")
    dataset.save_to_disk("godzilla_medical_dataset_hf")
    
    print("\n🚀 READY FOR UPLOAD!")
    print("To upload to Hugging Face Datasets Hub:")
    print("1. Install: pip install datasets huggingface_hub")
    print("2. Login: huggingface-cli login")
    print("3. Upload with:")
    print("   dataset.push_to_hub('your-username/godzilla-medical-embeddings')")
    
    print("\n📋 Manual upload code:")
    print("""
from datasets import load_from_disk
dataset = load_from_disk("godzilla_medical_dataset_hf")
dataset.push_to_hub("your-username/godzilla-medical-embeddings")
""")

if __name__ == "__main__":
    main()
