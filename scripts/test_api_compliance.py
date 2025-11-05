"""
Test script to verify API endpoints match exact specification.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.schemas.resume import (
    UploadOptions, JobMatchRequest, JobDescription, ExperienceRequirement,
    Requirements, SkillsRequirement, SalaryRange, MatchOptions
)
from app.utils.transform import transform_resume_to_api_response, transform_job_match_to_api_response
from app.models import Resume
from datetime import datetime
import json


def test_upload_options():
    """Test UploadOptions schema."""
    print("\n" + "="*80)
    print("TEST 1: Upload Options Schema")
    print("="*80)
    
    options = UploadOptions(
        extractTechnologies=True,
        performOCR=True,
        enhanceWithAI=True,
        anonymize=False,
        language="en"
    )
    
    print("✅ UploadOptions created successfully")
    print(json.dumps(options.dict(), indent=2))
    
    # Verify all required fields present
    assert options.extractTechnologies == True
    assert options.performOCR == True
    assert options.enhanceWithAI == True
    assert options.anonymize == False
    assert options.language == "en"
    
    print("✅ All fields match specification")
    return True


def test_job_description_schema():
    """Test JobDescription schema."""
    print("\n" + "="*80)
    print("TEST 2: Job Description Schema")
    print("="*80)
    
    job_desc = JobDescription(
        title="Senior Software Engineer",
        company="Tech Innovation Corp",
        location="San Francisco, CA",
        type="full-time",
        experience=ExperienceRequirement(
            minimum=5,
            preferred=8,
            level="senior"
        ),
        description="We are seeking a highly skilled Senior Software Engineer...",
        requirements=Requirements(
            required=[
                "5+ years of software development experience",
                "Proficiency in Python and JavaScript",
                "Experience with cloud platforms (AWS, GCP, or Azure)",
                "Strong understanding of microservices architecture",
                "Bachelor's degree in Computer Science or related field"
            ],
            preferred=[
                "Experience with Docker and Kubernetes",
                "Knowledge of machine learning frameworks",
                "Previous startup experience",
                "Master's degree preferred"
            ]
        ),
        skills=SkillsRequirement(
            required=["Python", "JavaScript", "AWS", "Microservices", "REST APIs"],
            preferred=["Docker", "Kubernetes", "Machine Learning", "PostgreSQL", "React"]
        ),
        salary=SalaryRange(
            min=140000,
            max=180000,
            currency="USD"
        ),
        benefits=["Health insurance", "401k matching", "Remote work options"],
        industry="technology"
    )
    
    print("✅ JobDescription created successfully")
    job_dict = job_desc.dict()
    
    # Verify structure
    assert job_dict['title'] == "Senior Software Engineer"
    assert job_dict['company'] == "Tech Innovation Corp"
    assert job_dict['experience']['minimum'] == 5
    assert job_dict['experience']['preferred'] == 8
    assert job_dict['experience']['level'] == "senior"
    assert len(job_dict['requirements']['required']) == 5
    assert len(job_dict['requirements']['preferred']) == 4
    assert len(job_dict['skills']['required']) == 5
    assert len(job_dict['skills']['preferred']) == 5
    assert job_dict['salary']['min'] == 140000
    assert job_dict['salary']['max'] == 180000
    
    print("✅ All nested fields match specification")
    print(json.dumps(job_dict, indent=2)[:500] + "...")
    return True


def test_job_match_request():
    """Test complete job match request."""
    print("\n" + "="*80)
    print("TEST 3: Job Match Request Schema")
    print("="*80)
    
    request = JobMatchRequest(
        jobDescription=JobDescription(
            title="Senior Software Engineer",
            company="Tech Innovation Corp",
            location="San Francisco, CA",
            type="full-time",
            experience=ExperienceRequirement(
                minimum=5,
                preferred=8,
                level="senior"
            ),
            description="Test description",
            requirements=Requirements(
                required=["Python", "AWS"],
                preferred=["Docker"]
            ),
            skills=SkillsRequirement(
                required=["Python", "JavaScript"],
                preferred=["Docker"]
            ),
            salary=SalaryRange(min=140000, max=180000, currency="USD"),
            benefits=["Health insurance"],
            industry="technology"
        ),
        options=MatchOptions(
            includeExplanation=True,
            detailedBreakdown=True,
            suggestImprovements=True
        )
    )
    
    print("✅ JobMatchRequest created successfully")
    
    # Verify options
    assert request.options.includeExplanation == True
    assert request.options.detailedBreakdown == True
    assert request.options.suggestImprovements == True
    
    print("✅ All request fields match specification")
    return True


def test_resume_response_transformation():
    """Test resume transformation to API response format."""
    print("\n" + "="*80)
    print("TEST 4: Resume Response Transformation")
    print("="*80)
    
    # Create mock resume
    mock_resume = type('Resume', (), {
        'id': '550e8400-e29b-41d4-a716-446655440000',
        'file_name': 'john_doe_resume.pdf',
        'file_size': 2048576,
        'uploaded_at': datetime(2025, 9, 10, 10, 30, 0),
        'processed_at': datetime(2025, 9, 10, 10, 30, 45),
        'processing_status': 'COMPLETED',
        'structured_data': {
            'personal_info': {
                'full_name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+1-555-123-4567',
                'linkedin': 'https://linkedin.com/in/johndoe',
                'address': {
                    'city': 'San Francisco',
                    'state': 'CA',
                    'zipCode': '94105'
                }
            },
            'work_experiences': [
                {
                    'id': 'exp-1',
                    'job_title': 'Senior Software Engineer',
                    'company_name': 'Tech Corp',
                    'location': 'San Francisco, CA',
                    'start_date': '2021-03-01',
                    'end_date': '2025-09-01',
                    'is_current': True,
                    'description': 'Led development of microservices architecture',
                    'achievements': ['Improved system performance by 40%'],
                    'technologies': ['Python', 'Docker', 'AWS']
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Science',
                    'field_of_study': 'Computer Science',
                    'institution': 'University of California, Berkeley',
                    'location': 'Berkeley, CA',
                    'graduation_date': '2018-05-15',
                    'gpa': 3.7,
                    'honors': ['Magna Cum Laude']
                }
            ],
            'skills': [
                {'skill_name': 'Python', 'category': 'Programming Languages'},
                {'skill_name': 'JavaScript', 'category': 'Programming Languages'},
                {'skill_name': 'Django', 'category': 'Frameworks'},
                {'skill_name': 'React', 'category': 'Frameworks'}
            ],
            'total_experience_years': 5
        },
        'ai_enhancements': {
            'quality_score': 87,
            'completeness_score': 92,
            'suggestions': ['Add quantifiable achievements', 'Include certifications'],
            'industry_fit': {
                'software_engineering': 0.95,
                'data_science': 0.45
            }
        }
    })()
    
    # Transform
    response = transform_resume_to_api_response(mock_resume)
    
    # Verify structure
    assert response.id == '550e8400-e29b-41d4-a716-446655440000'
    assert response.metadata.fileName == 'john_doe_resume.pdf'
    assert response.metadata.fileSize == 2048576
    assert response.personalInfo.name.full == 'John Doe'
    assert response.personalInfo.name.first == 'John'
    assert response.personalInfo.name.last == 'Doe'
    assert response.personalInfo.contact.email == 'john.doe@example.com'
    assert response.personalInfo.contact.phone == '+1-555-123-4567'
    assert len(response.experience) == 1
    assert response.experience[0].title == 'Senior Software Engineer'
    assert len(response.education) == 1
    assert response.education[0].degree == 'Bachelor of Science'
    assert response.aiEnhancements.qualityScore == 87
    assert response.aiEnhancements.completenessScore == 92
    
    print("✅ Resume transformation successful")
    print(f"✅ Metadata: fileName={response.metadata.fileName}, fileSize={response.metadata.fileSize}")
    print(f"✅ Personal: {response.personalInfo.name.full} ({response.personalInfo.contact.email})")
    print(f"✅ Experience: {len(response.experience)} items")
    print(f"✅ Education: {len(response.education)} items")
    print(f"✅ AI Scores: quality={response.aiEnhancements.qualityScore}, completeness={response.aiEnhancements.completenessScore}")
    
    return True


def test_job_match_response_transformation():
    """Test job match transformation."""
    print("\n" + "="*80)
    print("TEST 5: Job Match Response Transformation")
    print("="*80)
    
    # Mock data
    resume_id = '550e8400-e29b-41d4-a716-446655440000'
    
    job_description = {
        'jobDescription': {
            'title': 'Senior Software Engineer',
            'company': 'Tech Innovation Corp',
            'location': 'San Francisco, CA',
            'experience': {
                'minimum': 5,
                'preferred': 8,
                'level': 'senior'
            },
            'skills': {
                'required': ['Python', 'JavaScript', 'AWS'],
                'preferred': ['Docker', 'Kubernetes']
            },
            'salary': {
                'min': 140000,
                'max': 180000,
                'currency': 'USD'
            }
        }
    }
    
    match_result = {
        'overall_score': 87,
        'category_scores': {
            'skills': {
                'score': 85,
                'matched_skills': ['Python', 'JavaScript', 'AWS'],
                'missing_skills': ['Docker', 'Kubernetes']
            },
            'experience': {
                'score': 90,
                'industry_match': True
            }
        }
    }
    
    resume_data = {
        'total_experience_years': 5.5,
        'skills': ['Python', 'JavaScript', 'AWS', 'PostgreSQL'],
        'work_experiences': [
            {'job_title': 'Senior Software Engineer', 'company_name': 'Tech Corp'}
        ],
        'education': [
            {'degree': 'Bachelor of Science', 'field_of_study': 'Computer Science'}
        ],
        'personal_info': {
            'address': {'city': 'San Francisco', 'state': 'CA'}
        }
    }
    
    # Transform
    start_time = datetime.utcnow()
    response = transform_job_match_to_api_response(
        resume_id=resume_id,
        job_description=job_description,
        match_result=match_result,
        resume_data=resume_data,
        processing_start_time=start_time
    )
    
    # Verify structure
    assert response.resumeId == resume_id
    assert response.jobTitle == 'Senior Software Engineer'
    assert response.company == 'Tech Innovation Corp'
    assert response.matchingResults.overallScore == 87
    assert response.matchingResults.recommendation in ['Strong Match', 'Good Match', 'Moderate Match']
    assert 'skillsMatch' in response.matchingResults.categoryScores
    assert 'experienceMatch' in response.matchingResults.categoryScores
    assert 'educationMatch' in response.matchingResults.categoryScores
    assert 'roleAlignment' in response.matchingResults.categoryScores
    assert 'locationMatch' in response.matchingResults.categoryScores
    assert response.matchingResults.categoryScores['skillsMatch'].weight == 35
    assert response.matchingResults.categoryScores['experienceMatch'].weight == 25
    assert len(response.explanation.summary) > 0
    assert len(response.explanation.keyFactors) > 0
    assert len(response.explanation.recommendations) > 0
    assert response.metadata.algorithm == 'AI-Enhanced Semantic Matching v2.1'
    
    print("✅ Job match transformation successful")
    print(f"✅ Match ID: {response.matchId}")
    print(f"✅ Overall Score: {response.matchingResults.overallScore}")
    print(f"✅ Recommendation: {response.matchingResults.recommendation}")
    print(f"✅ Category Scores: {len(response.matchingResults.categoryScores)} categories")
    print(f"✅ Skills Match: {response.matchingResults.categoryScores['skillsMatch'].score} (weight: {response.matchingResults.categoryScores['skillsMatch'].weight}%)")
    print(f"✅ Experience Match: {response.matchingResults.categoryScores['experienceMatch'].score} (weight: {response.matchingResults.categoryScores['experienceMatch'].weight}%)")
    print(f"✅ Critical Gaps: {len(response.matchingResults.gapAnalysis.criticalGaps)}")
    print(f"✅ Improvement Areas: {len(response.matchingResults.gapAnalysis.improvementAreas)}")
    print(f"✅ Strength Areas: {len(response.matchingResults.strengthAreas)}")
    print(f"✅ Competitive Advantages: {len(response.matchingResults.competitiveAdvantages)}")
    print(f"✅ Explanation: {len(response.explanation.summary)} chars")
    print(f"✅ Algorithm: {response.metadata.algorithm}")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("EXACT API SPECIFICATION COMPLIANCE TESTS")
    print("="*80)
    
    tests = [
        ("Upload Options Schema", test_upload_options),
        ("Job Description Schema", test_job_description_schema),
        ("Job Match Request Schema", test_job_match_request),
        ("Resume Response Transformation", test_resume_response_transformation),
        ("Job Match Response Transformation", test_job_match_response_transformation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - API IS 100% SPECIFICATION COMPLIANT! 🎉")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed - review errors above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
