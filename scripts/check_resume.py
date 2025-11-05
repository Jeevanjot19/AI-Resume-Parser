"""Check a specific resume's data."""
import sys
from app.core.database import SessionLocal
from app.models.resume import Resume
import json

def check_resume(resume_id: str):
    db = SessionLocal()
    try:
        # Try to parse as UUID
        import uuid
        try:
            resume_uuid = uuid.UUID(resume_id)
        except ValueError:
            print(f"Invalid UUID format: {resume_id}")
            return
        
        resume = db.query(Resume).filter(Resume.id == resume_uuid).first()
        
        if not resume:
            print(f"Resume not found: {resume_id}")
            return
        
        print(f"\n{'='*60}")
        print(f"RESUME: {resume_id}")
        print(f"{'='*60}")
        print(f"Filename: {resume.file_name}")
        print(f"File Type: {resume.file_type}")
        print(f"File Size: {resume.file_size} bytes")
        print(f"Uploaded: {resume.uploaded_at}")
        print(f"Processed: {resume.processed_at}")
        print(f"Status: {resume.processing_status.value}")
        print(f"\nRaw Text Length: {len(resume.raw_text) if resume.raw_text else 0}")
        print(f"Has Structured Data: {resume.structured_data is not None}")
        print(f"Has AI Enhancements: {resume.ai_enhancements is not None}")
        
        if resume.structured_data:
            print(f"\nStructured Data Keys: {list(resume.structured_data.keys())}")
            print(f"\nStructured Data Preview:")
            print(json.dumps(resume.structured_data, indent=2)[:1000])
        else:
            print(f"\n⚠️ No structured data - resume hasn't been processed yet!")
            print(f"Status: {resume.processing_status.value}")
            
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_resume.py <resume_id>")
        print("\nExample: python scripts/check_resume.py e39d982d-6955-42b8-8088-92b3e775fbec")
        sys.exit(1)
    
    check_resume(sys.argv[1])
