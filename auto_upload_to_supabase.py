#!/usr/bin/env python3
"""
Auto-Upload to Supabase Monitor
Automatically uploads to Supabase once HF embeddings are complete
"""

import os
import time
import subprocess
from datetime import datetime

def check_embeddings_complete():
    """Check if the HF embeddings generation is complete"""
    # Check if all required files exist
    required_files = [
        'fast_medical_embeddings.npy',
        'fast_medical_metadata.json',
        'fast_embeddings_report.json'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            return False
    
    # Check if the report indicates completion
    try:
        import json
        with open('fast_embeddings_report.json', 'r') as f:
            report = json.load(f)
        
        # Check if processing is complete
        if report.get('status') == 'completed':
            return True
            
    except Exception:
        pass
    
    return False

def monitor_and_upload():
    """Monitor for completion and auto-upload to Supabase"""
    print("🔍 SUPABASE AUTO-UPLOAD MONITOR STARTED")
    print("=" * 50)
    print("⏳ Waiting for HF embeddings to complete...")
    print("📁 Monitoring files:")
    print("   - fast_medical_embeddings.npy")
    print("   - fast_medical_metadata.json") 
    print("   - fast_embeddings_report.json")
    print()
    
    check_interval = 30  # Check every 30 seconds
    max_wait_time = 3600  # Maximum wait time: 1 hour
    start_time = time.time()
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Check if embeddings are complete
        if check_embeddings_complete():
            print("🎉 HF EMBEDDINGS COMPLETE!")
            print("🚀 Starting automatic Supabase upload...")
            print()
            
            # Run the Supabase upload script
            try:
                result = subprocess.run(['python', 'upload_to_supabase.py'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ SUPABASE UPLOAD SUCCESSFUL!")
                    print(result.stdout)
                else:
                    print("❌ SUPABASE UPLOAD FAILED!")
                    print(result.stderr)
                
            except Exception as e:
                print(f"❌ Error running upload script: {e}")
            
            break
        
        # Check if we've exceeded maximum wait time
        if elapsed_time > max_wait_time:
            print(f"⏰ Maximum wait time ({max_wait_time/60:.0f} minutes) exceeded")
            print("💡 You can run upload_to_supabase.py manually when embeddings are ready")
            break
        
        # Show progress
        minutes_elapsed = elapsed_time / 60
        print(f"⏳ Still waiting... ({minutes_elapsed:.1f} minutes elapsed)")
        
        # Wait before next check
        time.sleep(check_interval)

if __name__ == "__main__":
    monitor_and_upload()
