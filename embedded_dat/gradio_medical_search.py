#!/usr/bin/env python3
"""
Gradio Web Interface for Godzilla Medical Search
Deploy this to Hugging Face Spaces for free!
"""

import gradio as gr
import numpy as np
import json
from fast_hf_embeddings import FastMedicalEmbeddings
import pandas as pd

# Global embedder instance
embedder = None

def initialize_embedder():
    """Initialize the embedder with pre-computed embeddings"""
    global embedder
    
    if embedder is None:
        embedder = FastMedicalEmbeddings()
        
        # Load embeddings
        if not embedder.load_embeddings():
            return False
        
        # Load model
        if not embedder.load_model():
            return False
    
    return True

def search_medical_records(query, num_results=5):
    """Search medical records and return formatted results"""
    if not query.strip():
        return "Please enter a medical query."
    
    # Initialize embedder if needed
    if not initialize_embedder():
        return "❌ Error: Could not load embeddings. Please make sure the embeddings are generated first."
    
    try:
        # Perform search
        results = embedder.search(query, top_k=num_results)
        
        if not results:
            return "No results found for your query."
        
        # Format results for display
        formatted_results = []
        
        for result in results:
            metadata = result['metadata']
            formatted_result = {
                "Rank": result['rank'],
                "Similarity Score": f"{result['similarity']:.3f}",
                "Medical Specialty": metadata['medical_specialty'],
                "Keywords": metadata['keywords'],
                "Text Preview": metadata['text_preview'],
                "Confidence Score": metadata['confidence_score'],
                "Source Dataset": metadata['source_dataset']
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
        
    except Exception as e:
        return f"❌ Error during search: {str(e)}"

def get_dataset_stats():
    """Get dataset statistics"""
    if not initialize_embedder():
        return "Could not load dataset statistics."
    
    try:
        total_records = len(embedder.embeddings)
        embedding_dims = embedder.embeddings.shape[1]
        
        # Get unique specialties
        specialties = set([item['medical_specialty'] for item in embedder.metadata])
        
        stats = f"""
        📊 **Dataset Statistics:**
        - Total Records: {total_records:,}
        - Embedding Dimensions: {embedding_dims}
        - Medical Specialties: {len(specialties)}
        - Model: {embedder.model_name}
        """
        
        return stats
        
    except Exception as e:
        return f"Error getting statistics: {str(e)}"

def create_interface():
    """Create the Gradio interface"""
    
    # Custom CSS for better styling
    css = """
    .gradio-container {
        font-family: 'Arial', sans-serif;
    }
    .title {
        text-align: center;
        color: #2E8B57;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .description {
        text-align: center;
        font-size: 1.2em;
        color: #666;
        margin-bottom: 30px;
    }
    """
    
    with gr.Blocks(css=css, title="🦖 Godzilla Medical Search") as interface:
        
        # Header
        gr.HTML("""
        <div class="title">🦖 Godzilla Medical Search</div>
        <div class="description">
            Semantic search through medical records using Hugging Face embeddings
        </div>
        """)
        
        # Main search interface
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="🔍 Medical Query",
                    placeholder="Enter your medical search query (e.g., 'pediatric heart conditions', 'diabetes treatment')",
                    lines=2
                )
                
                num_results = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=5,
                    step=1,
                    label="Number of Results"
                )
                
                search_btn = gr.Button("🔍 Search", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                stats_btn = gr.Button("📊 Dataset Stats", variant="secondary")
                stats_output = gr.Textbox(
                    label="Dataset Information",
                    lines=8,
                    interactive=False
                )
        
        # Results display
        results_output = gr.JSON(
            label="🏥 Search Results",
            show_label=True
        )
        
        # Example queries
        gr.HTML("""
        <div style="margin-top: 30px;">
            <h3>💡 Example Queries:</h3>
            <ul>
                <li>pediatric heart conditions treatment</li>
                <li>diabetes management in elderly patients</li>
                <li>respiratory infections in children</li>
                <li>neurological symptoms diagnosis</li>
                <li>cancer screening procedures</li>
                <li>hypertension medication side effects</li>
            </ul>
        </div>
        """)
        
        # Event handlers
        search_btn.click(
            fn=search_medical_records,
            inputs=[query_input, num_results],
            outputs=results_output
        )
        
        stats_btn.click(
            fn=get_dataset_stats,
            outputs=stats_output
        )
        
        # Auto-load stats on startup
        interface.load(
            fn=get_dataset_stats,
            outputs=stats_output
        )
    
    return interface

def main():
    """Main function to launch the interface"""
    print("🦖 Starting Godzilla Medical Search Interface...")
    
    # Create and launch interface
    interface = create_interface()
    
    # Launch with public sharing
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Creates public link
        show_error=True
    )

if __name__ == "__main__":
    main()
