#!/usr/bin/env python3
"""
Monitor the Pinecone upload progress
"""

import os
import time
import subprocess

def monitor_upload():
    """Monitor the upload progress"""
    
    print("🦖 MONITORING GODZILLA DATASET UPLOAD TO PINECONE")
    print("=" * 60)
    
    while True:
        try:
            # Check if process is still running
            result = subprocess.run(['pgrep', '-f', 'upload_to_pinecone'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print("✅ Upload process completed!")
                break
            
            # Show last few lines of log
            if os.path.exists('upload_log.txt'):
                with open('upload_log.txt', 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        print(f"📊 Status: {last_line}")
            
            # Check for completion files
            if os.path.exists('pinecone_upload_report.json'):
                print("🎉 Upload report found! Upload completed successfully!")
                break
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error monitoring: {e}")
            break
    
    # Show final results if available
    if os.path.exists('pinecone_upload_report.json'):
        print("\n📋 FINAL UPLOAD REPORT:")
        print("=" * 30)
        with open('pinecone_upload_report.json', 'r') as f:
            import json
            report = json.load(f)
            print(f"📊 Total Records: {report.get('total_records', 'N/A'):,}")
            print(f"🚀 Vectors Uploaded: {report.get('vectors_uploaded', 'N/A'):,}")
            print(f"📈 Success Rate: {report.get('success_rate', 'N/A'):.1f}%")
            print(f"🏥 Index Name: {report.get('index_name', 'N/A')}")
            print(f"🤖 Model: {report.get('embedding_model', 'N/A')}")
    
    if os.path.exists('upload_log.txt'):
        print("\n📝 Final log entries:")
        with open('upload_log.txt', 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"   {line.strip()}")

if __name__ == "__main__":
    monitor_upload()
