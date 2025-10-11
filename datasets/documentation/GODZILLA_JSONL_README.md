# Godzilla Medical Dataset - JSONL Format

## 📋 **Dataset Overview**
- **File**: `godzilla_medical_dataset.jsonl`
- **Format**: JSON Lines (JSONL) - each line is a complete JSON object
- **Total Records**: 9,616 medical text chunks
- **File Size**: 36.33 MB
- **Dataset Version**: 1.0
- **Created**: October 2025

## 🏗️ **Record Structure**

Each JSONL record contains the following fields:

### **Core Medical Content**
- **`id`**: Unique identifier (UUID)
- **`text`**: Main medical content (up to 5000 characters)
- **`medical_specialty`**: Medical field (pediatrics, cardiology, etc.)
- **`source_dataset`**: Source type (`medical_documents`, `nelson_enhanced`)

### **Metadata Fields**
- **`keywords`**: Array of extracted medical keywords
- **`confidence_score`**: Content quality score (0.0-1.0)
- **`clinical_relevance_score`**: Clinical importance (0.0-1.0)
- **`reading_difficulty`**: Complexity level (`expert`, `intermediate`, `beginner`)
- **`learning_objectives`**: Educational goals

### **Source Information**
- **`source_file`**: Original PDF filename
- **`book_title`**: Source textbook name
- **`chapter_title`**: Chapter or section title
- **`page_number`**: Page reference (integer)

### **Text Analytics**
- **`chunk_token_count`**: Original token count
- **`word_count`**: Original word count (from CSV)
- **`text_length`**: Character count (calculated)
- **`word_count_calculated`**: Recalculated word count

### **Training Metadata**
- **`dataset_version`**: Version identifier
- **`record_type`**: Always "medical_knowledge"
- **`training_category`**: Normalized specialty for ML training
- **`age_groups`**: Target age groups
- **`created_at`**: Original creation timestamp
- **`godzilla_created_at`**: Dataset compilation timestamp

## 📊 **Dataset Statistics**

### **Source Distribution**
- **Nelson Enhanced**: 9,068 records (94.3%)
- **Medical Documents**: 548 records (5.7%)

### **Medical Specialties**
- **Pediatrics**: 9,275 records (96.4%)
- **Cardiology**: 47 records
- **Dermatology**: 38 records
- **Urology**: 33 records
- **Neurology**: 43 records
- **Emergency**: 13 records
- **Other specialties**: ~190 records

### **Quality Metrics**
- **Average Confidence Score**: 0.845
- **High Quality Records (≥0.7)**: 100%
- **Average Text Length**: ~3,780 characters
- **Average Word Count**: ~538 words

## 🎯 **Use Cases**

### **Machine Learning Applications**
- **Medical Question Answering**: Train models to answer pediatric queries
- **Text Classification**: Classify medical content by specialty
- **Semantic Search**: Build medical knowledge retrieval systems
- **Medical NLP**: Named entity recognition, relation extraction

### **Training Data Formats**
- **Instruction Tuning**: Use text as context, create Q&A pairs
- **RAG Systems**: Vector embeddings for retrieval augmented generation
- **Fine-tuning**: Domain-specific model adaptation
- **Multi-task Learning**: Combine classification and generation tasks

## 🔧 **Loading the Dataset**

### **Python Example**
```python
import json

def load_godzilla_dataset(file_path):
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line.strip())
            records.append(record)
    return records

# Load dataset
dataset = load_godzilla_dataset('godzilla_medical_dataset.jsonl')
print(f"Loaded {len(dataset)} medical records")

# Filter by specialty
pediatrics_records = [r for r in dataset if r['medical_specialty'] == 'pediatrics']
print(f"Pediatrics records: {len(pediatrics_records)}")
```

### **Pandas DataFrame**
```python
import pandas as pd
import json

def jsonl_to_dataframe(file_path):
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line.strip()))
    return pd.DataFrame(records)

# Create DataFrame
df = jsonl_to_dataframe('godzilla_medical_dataset.jsonl')
print(df.shape)
print(df['medical_specialty'].value_counts())
```

### **Hugging Face Datasets**
```python
from datasets import Dataset
import json

def load_as_hf_dataset(file_path):
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            records.append(json.loads(line.strip()))
    return Dataset.from_list(records)

# Create Hugging Face dataset
dataset = load_as_hf_dataset('godzilla_medical_dataset.jsonl')
print(dataset)
```

## 🎨 **Data Filtering Examples**

### **High Quality Content**
```python
high_quality = [r for r in dataset if r['confidence_score'] >= 0.9]
```

### **By Medical Specialty**
```python
cardiology = [r for r in dataset if r['training_category'] == 'cardiology']
```

### **By Text Length**
```python
long_texts = [r for r in dataset if r['text_length'] >= 3000]
```

### **By Keywords**
```python
asthma_related = [r for r in dataset if 'asthma' in r['keywords']]
```

## 🚀 **Training Recommendations**

### **For Question Answering**
- Use `text` as context
- Generate questions from `keywords` and `learning_objectives`
- Filter by `confidence_score` ≥ 0.8 for training

### **For Classification**
- Use `text` as input
- Use `medical_specialty` as labels
- Balance dataset by specialty if needed

### **For RAG Systems**
- Create embeddings for `text` field
- Use `keywords` for keyword search fallback
- Index by `medical_specialty` for filtered retrieval

### **For Instruction Tuning**
- Format as: `"Context: {text}\n\nQuestion: {generated_question}\n\nAnswer: {generated_answer}"`
- Use `clinical_relevance_score` to prioritize important content
- Include `source_file` and `page_number` for citations

## ⚠️ **Important Notes**

### **Content Limitations**
- Text chunks are truncated at 5000 characters
- Some medical figures and tables may be referenced but not included
- Content is primarily pediatric-focused (96.4%)

### **Quality Considerations**
- All records have confidence_score ≥ 0.7
- Higher confidence_score indicates better text quality
- `reading_difficulty` is mostly "expert" level

### **Usage Guidelines**
- Validate medical accuracy for clinical applications
- Consider combining with additional medical knowledge sources
- Respect copyright and licensing for commercial use
- Always include human review for medical decision support

## 📄 **Sample Record Structure**
```json
{
    "id": "efdde4ab-fcf9-45ef-b3a8-136b8255cc3c",
    "source_dataset": "medical_documents",
    "text": "Medical content text...",
    "medical_specialty": "pediatrics",
    "keywords": ["liver", "demonstrates", "lobe", "mass"],
    "confidence_score": 0.95,
    "clinical_relevance_score": 0.5,
    "text_length": 5000,
    "word_count_calculated": 718,
    "training_category": "pediatrics",
    "dataset_version": "1.0",
    "record_type": "medical_knowledge"
}
```

## 🔗 **Related Files**
- Original CSV: `godzilla_medical_dataset.csv` (31.58 MB)
- Conversion script: `convert_to_jsonl.py`
- Dataset statistics: `godzilla_medical_dataset_stats.json`
- Enhanced Nelson chunks: `nelson_chunks_enhanced.csv`

---
**Dataset created by**: Godzilla Medical Dataset Project  
**Conversion date**: October 2025  
**Format version**: JSONL 1.0