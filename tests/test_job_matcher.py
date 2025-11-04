import pytest
from app.services.job_matcher import JobMatcherService

@pytest.mark.asyncio
async def test_resume_job_matching(test_resume_data, test_job_description):
    """Test resume-job matching"""
    matcher = JobMatcherService()
    match_result = await matcher.match_resume_with_job(
        resume_id="test-id",
        job_description=test_job_description
    )
    
    # Check overall structure
    assert "overallScore" in match_result
    assert "categoryScores" in match_result
    assert "gapAnalysis" in match_result
    assert "recommendations" in match_result
    
    # Check score ranges
    assert 0 <= match_result["overallScore"] <= 100
    
    # Check category scores
    categories = match_result["categoryScores"]
    assert "skills" in categories
    assert "experience" in categories
    assert "education" in categories
    
    # Validate skills matching
    skills_match = categories["skills"]
    assert "score" in skills_match
    assert "matched_skills" in skills_match
    assert "missing_skills" in skills_match
    
    # Check gap analysis
    gaps = match_result["gapAnalysis"]
    assert "critical_gaps" in gaps
    assert "improvement_areas" in gaps
    
    # Check recommendations
    assert isinstance(match_result["recommendations"], list)
    assert len(match_result["recommendations"]) > 0

@pytest.mark.asyncio
async def test_skills_matching(test_resume_data, test_job_description):
    """Test skills matching logic"""
    matcher = JobMatcherService()
    skills_match = matcher._calculate_skills_match(test_resume_data, test_job_description)
    
    assert isinstance(skills_match, dict)
    assert "score" in skills_match
    assert 0 <= skills_match["score"] <= 100
    
    assert isinstance(skills_match["matched_skills"], list)
    assert isinstance(skills_match["missing_skills"], list)

@pytest.mark.asyncio
async def test_experience_matching(test_resume_data, test_job_description):
    """Test experience matching logic"""
    matcher = JobMatcherService()
    exp_match = matcher._calculate_experience_match(test_resume_data, test_job_description)
    
    assert isinstance(exp_match, dict)
    assert "score" in exp_match
    assert 0 <= exp_match["score"] <= 100
    
    assert isinstance(exp_match["years_match"], bool)
    assert isinstance(exp_match["level_match"], bool)

@pytest.mark.asyncio
async def test_gap_analysis(test_resume_data, test_job_description):
    """Test gap analysis"""
    matcher = JobMatcherService()
    gaps = await matcher._analyze_gaps(test_resume_data, test_job_description)
    
    assert isinstance(gaps, dict)
    assert "critical_gaps" in gaps
    assert "improvement_areas" in gaps
    assert isinstance(gaps["critical_gaps"], list)
    assert isinstance(gaps["improvement_areas"], list)

@pytest.mark.asyncio
async def test_recommendation_generation(test_resume_data, test_job_description):
    """Test recommendation generation"""
    matcher = JobMatcherService()
    recommendations = await matcher._generate_recommendations(
        test_resume_data,
        test_job_description
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert all(isinstance(r, str) for r in recommendations)