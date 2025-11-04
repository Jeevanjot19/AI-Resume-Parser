# Quick Dataset Setup - Visual Guide

## 📥 Step-by-Step: Manual Download

### 1️⃣ Visit Kaggle
```
🌐 https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
```

### 2️⃣ Click Download Button
- You'll need a free Kaggle account (sign up if you don't have one)
- Click the blue "Download" button
- File will download as `archive.zip` or similar

### 3️⃣ Extract the ZIP
```
📦 archive.zip
   └── 📄 Resume.csv  ← This is what you need!
```

### 4️⃣ Create Folder Structure
In your project directory, create this folder:

**Windows PowerShell:**
```powershell
New-Item -ItemType Directory -Force -Path "data\kaggle_resume_dataset"
```

**Windows Command Prompt:**
```cmd
mkdir data\kaggle_resume_dataset
```

**Linux/Mac:**
```bash
mkdir -p data/kaggle_resume_dataset
```

### 5️⃣ Copy Resume.csv
Copy the extracted `Resume.csv` file to:
```
D:\gemini hackathon\resume_parser_ai\data\kaggle_resume_dataset\Resume.csv
```

Your folder structure should look like:
```
resume_parser_ai/
├── app/
├── data/
│   └── kaggle_resume_dataset/
│       └── Resume.csv          ← File should be here
├── scripts/
│   └── import_kaggle_dataset.py
└── ...
```

### 6️⃣ Run Import Script
```bash
python scripts/import_kaggle_dataset.py
```

### 7️⃣ Wait for Processing
```
Processing resume 1/2400 - Category: Data Science
✓ Resume 0 processed successfully (ID: uuid-here)

Processing resume 2/2400 - Category: HR
✓ Resume 1 processed successfully (ID: uuid-here)

...
```

By default, it processes **50 resumes** for testing.

### 8️⃣ Verify Import
The script automatically verifies at the end:
```
Total resumes in database: 50
Sample resumes:
- uuid-1: kaggle_resume_0.txt (Category: Data Science)
  Skills: ['Python', 'Machine Learning', 'TensorFlow', ...]
```

## ✅ Done!

Now you can:
- Search resumes via API
- Test job matching
- Analyze resume quality
- Use semantic search

## 🚀 Test It Out

```bash
# Search for Python developers
curl -X POST http://localhost:8000/api/v1/resumes/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer with machine learning", "top_k": 5}'
```

## 📊 Dataset Stats

The Resume.csv contains:
- **2,400+ resumes**
- **24 job categories**
- Categories include:
  - Data Science
  - Software Engineering (Java, Python, .NET, etc.)
  - DevOps Engineer
  - Database Administrator
  - HR
  - Business Analyst
  - Sales
  - And more!

## 💡 Tips

1. **Processing Limit**: By default, script processes 50 resumes. To process more, edit line 104 in `scripts/import_kaggle_dataset.py`:
   ```python
   if processed_count >= 50:  # Change to 100, 500, or remove this check
   ```

2. **Check Progress**: Watch the terminal output to see each resume being processed

3. **Troubleshooting**: If import fails, check:
   - Resume.csv is in the correct folder
   - Database is running: `docker-compose ps`
   - Elasticsearch is running: `docker-compose ps`

4. **Re-import**: To re-import, you can delete existing data or use different IDs

## 🎯 What Happens During Import?

Each resume goes through:
1. ✅ Text extraction
2. ✅ NER (Named Entity Recognition) - extracts names, emails, skills, etc.
3. ✅ Industry classification - determines industry fit
4. ✅ Career level detection - Entry, Junior, Mid, Senior, etc.
5. ✅ Skills extraction - technical and soft skills
6. ✅ Embedding generation - 768-dim vectors for semantic search
7. ✅ Quality analysis - AI-powered quality scoring
8. ✅ Storage in PostgreSQL
9. ✅ Indexing in Elasticsearch

All using **real AI models** - no mocks! 🤖
