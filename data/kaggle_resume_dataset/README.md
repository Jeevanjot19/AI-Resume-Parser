# Kaggle Resume Dataset

## 📥 Place Your Downloaded Dataset Here

This folder should contain the Kaggle resume dataset files.

### What to Download:

1. **Go to**: https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset
2. **Click**: Download button (requires free Kaggle account)
3. **Extract**: The downloaded `archive.zip` file

### What to Place Here:

After extracting, you should have:

```
kaggle_resume_dataset/
├── Resume.csv              ← Place this CSV file here
└── data/                   ← Place this entire folder here
    ├── ACCOUNTANT/
    ├── ADVOCATE/
    ├── AGRICULTURE/
    ├── ARTS/
    ├── AUTOMOBILE/
    ├── AVIATION/
    ├── BANKING/
    ├── BPO/
    ├── BUSINESS-DEVELOPMENT/
    ├── CHEF/
    ├── CONSTRUCTION/
    ├── CONSULTANT/
    ├── DESIGNER/
    ├── DIGITAL-MEDIA/
    ├── ENGINEERING/
    ├── FINANCE/
    ├── FITNESS/
    ├── HEALTHCARE/
    ├── HR/
    ├── INFORMATION-TECHNOLOGY/
    ├── PUBLIC-RELATIONS/
    ├── SALES/
    ├── TEACHER/
    └── (and more categories...)
```

### Current Status:

- [ ] Resume.csv downloaded and placed here
- [ ] data/ folder downloaded and placed here

### Once Ready:

Run the import script:
```bash
python scripts/import_kaggle_dataset.py
```

This will:
- ✅ Read Resume.csv
- ✅ Process actual resume files (PDF, DOCX, images)
- ✅ Run full AI pipeline (NER, classification, embeddings)
- ✅ Store in PostgreSQL database
- ✅ Index in Elasticsearch for semantic search

### Dataset Info:

- **Total Resumes**: ~2,400+
- **Categories**: 24 job categories
- **File Formats**: PDF, DOCX, images
- **License**: Check Kaggle dataset page for license info

### Need Help?

See the guides:
- `docs/QUICK_DATASET_SETUP.md` - Visual step-by-step guide
- `docs/KAGGLE_DATASET_GUIDE.md` - Comprehensive guide with troubleshooting
