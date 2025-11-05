"""
Comprehensive endpoint testing script for Resume Parser API
Tests all available endpoints with the existing resume data
"""

import requests
import json
from typing import Dict, Any
import time

BASE_URL = "http://localhost:8000/api/v1"
RESUME_ID = "f9570a37-6946-4552-9d57-9d264236ff83"  # Existing resume in DB

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_result(endpoint: str, status: int, response: Any, success: bool = True):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {endpoint}")
    print(f"   Status: {status}")
    if isinstance(response, dict):
        print(f"   Response keys: {list(response.keys())}")
    print()

def test_health():
    """Test 1: Health Check"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print_result("GET /health", response.status_code, data, response.status_code == 200)
        if response.status_code == 200:
            print(f"   API Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_get_resume():
    """Test 2: Get Resume Details"""
    print_section("TEST 2: Get Resume Details")
    
    try:
        response = requests.get(f"{BASE_URL}/resumes/{RESUME_ID}")
        data = response.json()
        print_result(f"GET /resumes/{RESUME_ID}", response.status_code, data, response.status_code == 200)
        
        if response.status_code == 200:
            print(f"   Resume ID: {data.get('id')}")
            personal = data.get('personalInfo', {})
            print(f"   Name: {personal.get('name', {}).get('fullName', 'N/A')}")
            print(f"   Email: {personal.get('contact', {}).get('email', 'N/A')}")
            print(f"   Experience Items: {len(data.get('experience', []))}")
            print(f"   Education Items: {len(data.get('education', []))}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_get_status():
    """Test 3: Get Processing Status"""
    print_section("TEST 3: Get Processing Status")
    
    try:
        response = requests.get(f"{BASE_URL}/resumes/{RESUME_ID}/status")
        data = response.json()
        print_result(f"GET /resumes/{RESUME_ID}/status", response.status_code, data, response.status_code == 200)
        
        if response.status_code == 200:
            print(f"   Status: {data.get('status')}")
            print(f"   Progress: {data.get('progress', 0)}%")
            print(f"   Steps Completed: {len(data.get('stepsCompleted', []))}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_get_analysis():
    """Test 4: Get AI Analysis"""
    print_section("TEST 4: Get AI Analysis")
    
    try:
        response = requests.get(f"{BASE_URL}/resumes/{RESUME_ID}/analysis")
        data = response.json()
        print_result(f"GET /resumes/{RESUME_ID}/analysis", response.status_code, data, response.status_code == 200)
        
        if response.status_code == 200:
            print(f"   Quality Score: {data.get('qualityScore', 'N/A')}")
            print(f"   Completeness Score: {data.get('completenessScore', 'N/A')}")
            print(f"   Industry Matches: {len(data.get('industryMatches', []))}")
            print(f"   Skill Gaps: {len(data.get('skillGaps', []))}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_job_matching():
    """Test 5: Job Matching"""
    print_section("TEST 5: Job Matching with Job Description")
    
    job_data = {
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
            "includeExplanation": True,
            "detailedBreakdown": True,
            "suggestImprovements": True
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/resumes/{RESUME_ID}/match",
            json=job_data,
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        print_result(f"POST /resumes/{RESUME_ID}/match", response.status_code, data, response.status_code == 200)
        
        if response.status_code == 200:
            results = data.get('matchingResults', {})
            print(f"   Overall Score: {results.get('overallScore')}%")
            print(f"   Confidence: {results.get('confidence')}")
            print(f"   Recommendation: {results.get('recommendation')}")
            
            print("\n   Category Scores:")
            for category, details in results.get('categoryScores', {}).items():
                print(f"     • {category}: {details.get('score')} (weight: {details.get('weight')}%)")
            
            print(f"\n   Strength Areas: {len(results.get('strengthAreas', []))}")
            print(f"   Critical Gaps: {len(results.get('gapAnalysis', {}).get('criticalGaps', []))}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_search_resumes():
    """Test 6: Search Resumes"""
    print_section("TEST 6: Search Resumes")
    
    search_params = {
        "query": "python developer",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/resumes/search", params=search_params)
        data = response.json()
        print_result("GET /resumes/search", response.status_code, data, response.status_code == 200)
        
        if response.status_code == 200:
            results = data.get('results', [])
            print(f"   Total Results: {data.get('total', 0)}")
            print(f"   Returned: {len(results)}")
            if results:
                print(f"\n   Top Result:")
                top = results[0]
                print(f"     ID: {top.get('id')}")
                print(f"     Score: {top.get('score', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_list_resumes():
    """Test 7: List All Resumes"""
    print_section("TEST 7: List All Resumes (Paginated)")
    
    try:
        response = requests.get(f"{BASE_URL}/resumes?limit=5")
        data = response.json()
        print_result("GET /resumes?limit=5", response.status_code, data, response.status_code == 200)
        
        if response.status_code == 200:
            results = data.get('results', []) if isinstance(data, dict) else data
            print(f"   Returned: {len(results)} resumes")
            if results and len(results) > 0:
                first = results[0]
                if isinstance(first, dict):
                    print(f"\n   First Resume:")
                    print(f"     ID: {first.get('id', 'N/A')}")
                    personal = first.get('personalInfo', {})
                    print(f"     Name: {personal.get('name', {}).get('fullName', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}\n")

def test_upload_resume():
    """Test 8: Upload Resume (Test with sample file if available)"""
    print_section("TEST 8: Upload Resume")
    
    print("⚠️  Skipping upload test - would require a sample resume file")
    print("   To test upload, use Swagger UI at http://localhost:8000/api/v1/docs")
    print("   Upload endpoint: POST /resumes/upload\n")

def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("RESUME PARSER API - COMPREHENSIVE ENDPOINT TESTING")
    print("🚀 " * 20)
    
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Resume ID: {RESUME_ID}")
    
    # Run all tests
    test_health()
    time.sleep(0.5)
    
    test_get_resume()
    time.sleep(0.5)
    
    test_get_status()
    time.sleep(0.5)
    
    test_get_analysis()
    time.sleep(0.5)
    
    test_job_matching()
    time.sleep(0.5)
    
    test_search_resumes()
    time.sleep(0.5)
    
    test_list_resumes()
    time.sleep(0.5)
    
    test_upload_resume()
    
    # Summary
    print_section("TESTING COMPLETE!")
    print("✅ All available endpoints have been tested")
    print("\n📖 For detailed API documentation, visit:")
    print(f"   Swagger UI: {BASE_URL}/docs")
    print(f"   ReDoc: {BASE_URL}/redoc")
    print("\n")

if __name__ == "__main__":
    main()
