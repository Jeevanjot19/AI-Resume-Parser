# 🎯 Complete Guide: Testing All API Endpoints

## Server Status
✅ Server is running at: **http://localhost:8000**
✅ Swagger UI available at: **http://localhost:8000/api/v1/docs**

---

## 📋 All Available Endpoints - Testing Guide

### **1. Health Check** ✅
**Endpoint:** `GET /api/v1/health`

**How to test:**
- In Swagger UI: Find `/health` → Click "Try it out" → Click "Execute"
- Expected response: `{"status": "healthy", "version": "1.0.0"}`

---

### **2. Get Resume Details** ✅
**Endpoint:** `GET /api/v1/resumes/{resume_id}`

**How to test:**
1. Find `GET /api/v1/resumes/{resume_id}` in Swagger UI
2. Click "Try it out"
3. Enter resume ID: `f9570a37-6946-4552-9d57-9d264236ff83`
4. Click "Execute"

**What you'll see:**
- Personal information (name, email, phone)
- Work experience (job titles, companies, dates)
- Education (degrees, institutions)
- Skills (technical, soft skills)
- Complete parsed resume in structured format

---

### **3. Get Processing Status** ✅
**Endpoint:** `GET /api/v1/resumes/{resume_id}/status`

**How to test:**
1. Find `GET /api/v1/resumes/{resume_id}/status`
2. Click "Try it out"
3. Enter resume ID: `f9570a37-6946-4552-9d57-9d264236ff83`
4. Click "Execute"

**What you'll see:**
- Processing status: "COMPLETED"
- Progress percentage: 100%
- Steps completed
- Estimated completion time

---

### **4. Get AI Analysis** ✅
**Endpoint:** `GET /api/v1/resumes/{resume_id}/analysis`

**How to test:**
1. Find `GET /api/v1/resumes/{resume_id}/analysis`
2. Click "Try it out"
3. Enter resume ID: `f9570a37-6946-4552-9d57-9d264236ff83`
4. Click "Execute"

**What you'll see:**
- Quality score (0-100)
- Completeness score
- Industry matches
- Skill gaps
- Improvement suggestions
- Career path analysis

**Note:** May return empty data if AI analysis hasn't been run on this resume yet

---

### **5. Match Resume with Job** ✅ **(MOST IMPRESSIVE!)**
**Endpoint:** `POST /api/v1/resumes/{resume_id}/match`

**How to test:**
1. Find `POST /api/v1/resumes/{resume_id}/match`
2. Click "Try it out"
3. Enter resume ID: `f9570a37-6946-4552-9d57-9d264236ff83`
4. **Paste this job description in the request body:**

```json
{
  "jobDescription": {
    "title": "Senior Python Developer",
    "company": "Tech Innovations Inc",
    "location": "San Francisco, CA",
    "type": "Full-time",
    "experience": {
      "minimum": 3,
      "preferred": 5,
      "level": "Senior"
    },
    "description": "We are seeking an experienced Python developer to join our AI team",
    "requirements": {
      "required": [
        "Bachelor's degree in Computer Science",
        "5+ years Python experience"
      ],
      "preferred": [
        "Master's degree",
        "Machine Learning experience"
      ]
    },
    "skills": {
      "required": ["Python", "SQL", "REST APIs"],
      "preferred": ["FastAPI", "Docker", "AWS"]
    },
    "salary": {
      "min": 120000,
      "max": 180000,
      "currency": "USD"
    },
    "benefits": ["Health Insurance", "401k", "Remote Work"],
    "industry": "Technology"
  },
  "options": {
    "includeExplanation": true,
    "detailedBreakdown": true,
    "suggestImprovements": true
  }
}
```

5. Click "Execute"

**What you'll see (THIS IS THE BEST PART!):**
- **Overall Match Score** (0-100%)
- **5 Category Scores** with weights:
  - Skills Match (35%)
  - Experience Match (25%)
  - Education Match (15%)
  - Role Alignment (15%)
  - Location Match (10%)
- **Strength Areas**: What the candidate is good at
- **Gap Analysis**:
  - Critical gaps (high impact)
  - Improvement areas (nice to have)
- **Salary Alignment**: Job offer vs market rate
- **Competitive Advantages**: What makes this candidate stand out
- **AI-Generated Explanation**:
  - Match summary
  - Key factors
  - Recommendations for hiring manager

---

### **6. Search Resumes** ✅
**Endpoint:** `GET /api/v1/resumes/search`

**How to test:**
1. Find `GET /api/v1/resumes/search`
2. Click "Try it out"
3. Enter search parameters:
   - `query`: "python developer"
   - `skills`: ["Python", "SQL"]
   - `limit`: 10
4. Click "Execute"

**What you'll see:**
- List of matching resumes
- Match scores
- Total count
- Ranked by relevance

---

### **7. List All Resumes** ✅
**Endpoint:** `GET /api/v1/resumes`

**How to test:**
1. Find `GET /api/v1/resumes`
2. Click "Try it out"
3. Set parameters:
   - `skip`: 0
   - `limit`: 10
4. Click "Execute"

**What you'll see:**
- Paginated list of all resumes
- Basic info for each resume
- Total count

---

### **8. Upload Resume** ✅
**Endpoint:** `POST /api/v1/resumes/upload`

**How to test:**
1. Find `POST /api/v1/resumes/upload`
2. Click "Try it out"
3. Click "Choose File" and select a PDF or DOCX resume
4. Optionally add:
   ```json
   {
     "priority": "high",
     "extractImages": true,
     "performAIAnalysis": true
   }
   ```
5. Click "Execute"

**What you'll see:**
- Resume ID (newly created)
- Upload status
- Processing status
- Estimated processing time

---

### **9. Delete Resume** ⚠️
**Endpoint:** `DELETE /api/v1/resumes/{resume_id}`

**How to test:**
1. Find `DELETE /api/v1/resumes/{resume_id}`
2. Click "Try it out"
3. Enter a resume ID (⚠️ **NOT the test ID - create a new one first!**)
4. Click "Execute"

**What you'll see:**
- Success message
- Deleted resume ID

**WARNING:** Don't delete the test resume ID `f9570a37-6946-4552-9d57-9d264236ff83`!

---

## 🎨 Bonus: Alternative Testing Methods

### **Using curl (PowerShell)**

```powershell
# 1. Health Check
curl http://localhost:8000/api/v1/health

# 2. Get Resume
curl http://localhost:8000/api/v1/resumes/f9570a37-6946-4552-9d57-9d264236ff83

# 3. Get Status
curl http://localhost:8000/api/v1/resumes/f9570a37-6946-4552-9d57-9d264236ff83/status

# 4. Get Analysis
curl http://localhost:8000/api/v1/resumes/f9570a37-6946-4552-9d57-9d264236ff83/analysis

# 5. Search
curl "http://localhost:8000/api/v1/resumes/search?query=python&limit=5"
```

---

## 📊 Quick Test Summary

| Endpoint | Method | Status | Best Feature |
|----------|--------|--------|--------------|
| `/health` | GET | ✅ Working | Quick API health check |
| `/resumes/{id}` | GET | ✅ Working | Full parsed resume data |
| `/resumes/{id}/status` | GET | ✅ Working | Processing progress |
| `/resumes/{id}/analysis` | GET | ✅ Working | AI quality scores |
| `/resumes/{id}/match` | POST | ✅ **BEST!** | 5-category job matching |
| `/resumes/search` | GET | ✅ Working | Semantic resume search |
| `/resumes` | GET | ✅ Working | List all resumes |
| `/resumes/upload` | POST | ✅ Working | Upload new resumes |
| `/resumes/{id}` | DELETE | ✅ Working | Delete resume |

---

## 🚀 For Your Hackathon Demo

**Best endpoints to showcase:**

1. **Job Matching** (`/match`) - Most impressive, shows AI capabilities
2. **Get Resume** - Shows parsing accuracy
3. **Search** - Shows semantic search capability
4. **Upload** - Shows end-to-end workflow

**Demo Flow:**
1. Upload a resume → Get resume ID
2. Show parsed resume data → Structured output
3. Run job match → Detailed scoring
4. Search for similar resumes → Semantic search

---

## 📖 Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs (Interactive testing)
- **ReDoc**: http://localhost:8000/api/v1/redoc (Beautiful documentation)
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json (For tools)

---

## ✨ You're Ready!

All endpoints are working and tested. Your API is **100% ready for the hackathon!**
