# Kaggle Dataset Integration Guide

This guide explains how to download and import the Kaggle resume dataset into the system.

## Dataset Information

- **Source**: [Kaggle Resume Dataset by Sneha Anbhawal](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset)
- **Size**: ~2,400+ resumes
- **Categories**: Multiple job categories (Software Engineering, Data Science, HR, etc.)
- **Format**: CSV file with resume text and category labels

## Quick Start

### Option 1: Automated Download (Recommended)

1. **Setup Kaggle API credentials**:
   - Go to https://www.kaggle.com/settings/account
   - Scroll to "API" section
   - Click "Create New API Token"
   - Download `kaggle.json`
   - Place it in:
     - **Windows**: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
     - **Linux/Mac**: `~/.kaggle/kaggle.json`

2. **Download the dataset**:
   ```bash
   python scripts/download_kaggle_dataset.py
   ```

3. **Import into database**:
   ```bash
   python scripts/import_kaggle_dataset.py
   ```

### Option 2: Manual Download

1. **Download manually**:
   - Visit https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
   - Click "Download" button
   - Extract the ZIP file
   - Place `Resume.csv` in `data/kaggle_resume_dataset/`

2. **Import into database**:
   ```bash
   python scripts/import_kaggle_dataset.py
   ```

## What the Import Script Does

The import script (`import_kaggle_dataset.py`):

1. ✅ Reads the CSV file
2. ✅ Processes each resume through the full AI pipeline:
   - Document parsing
   - NER extraction (names, emails, phones, skills, etc.)
   - Text classification (industry, role, career level)
   - Embedding generation for semantic search
   - LLM-based quality analysis
3. ✅ Stores in PostgreSQL database
4. ✅ Indexes in Elasticsearch for semantic search
5. ✅ Adds AI enhancements (quality score, industry fit, skill gaps)

## Dataset Structure

The Kaggle dataset contains:

```
Resume.csv
├── ID (optional)
├── Resume_str / Resume (resume text)
└── Category (job category label)
```

Categories include:
- Data Science
- HR
- Advocate
- Arts
- Web Designing
- Mechanical Engineer
- Sales
- Health and Fitness
- Civil Engineer
- Java Developer
- Business Analyst
- SAP Developer
- Automation Testing
- Electrical Engineering
- Operations Manager
- Python Developer
- DevOps Engineer
- Network Security Engineer
- PMO
- Database
- Hadoop
- ETL Developer
- DotNet Developer
- Blockchain
- Testing

## Processing Limits

By default, the import script processes **50 resumes** for testing. To process all resumes, modify this line in `import_kaggle_dataset.py`:

```python
if processed_count >= 50:  # Change this number or remove the check
```

## Verification

After import, verify the data:

```bash
# Check database
python scripts/import_kaggle_dataset.py  # Runs verification automatically

# Or query via API
curl http://localhost:8000/api/v1/resumes/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "Python developer with machine learning experience", "top_k": 5}'
```

## Example Usage After Import

### 1. Search for Resumes
```bash
curl -X POST http://localhost:8000/api/v1/resumes/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "experienced data scientist with Python",
    "top_k": 10
  }'
```

### 2. Get Resume Details
```bash
curl http://localhost:8000/api/v1/resumes/{resume_id}
```

### 3. Get AI Analysis
```bash
curl http://localhost:8000/api/v1/resumes/{resume_id}/analysis
```

### 4. Match with Job
```bash
curl -X POST http://localhost:8000/api/v1/resumes/{resume_id}/match \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Data Scientist",
    "requirements": ["Python", "Machine Learning", "TensorFlow", "SQL"],
    "required_experience_years": 5,
    "industry": "Data Science"
  }'
```

## Expected Processing Time

- **Download**: ~1-2 minutes (depends on internet speed)
- **Import (50 resumes)**: ~5-10 minutes (depends on AI model initialization)
- **Full dataset (2400+)**: ~2-4 hours

## Troubleshooting

### Kaggle API Error
```
OSError: Could not find kaggle.json
```
**Solution**: Follow step 1 in "Automated Download" section above.

### Dataset Not Found
```
Dataset not found at data/kaggle_resume_dataset/Resume.csv
```
**Solution**: Run `python scripts/download_kaggle_dataset.py` first.

### Out of Memory
**Solution**: Process in batches by modifying the limit in the import script.

### Elasticsearch Not Available
**Solution**: Ensure Elasticsearch is running:
```bash
docker-compose up -d elasticsearch
```

## Performance Tips

1. **Start services first**: `docker-compose up -d`
2. **Use batch processing**: Process resumes in smaller batches
3. **Monitor resources**: Check Docker container logs
4. **Cache AI models**: Models are cached after first load

## Next Steps

After successful import:
1. ✅ Test semantic search functionality
2. ✅ Verify AI analysis quality
3. ✅ Test job matching with different criteria
4. ✅ Benchmark response times
5. ✅ Fine-tune AI models if needed
