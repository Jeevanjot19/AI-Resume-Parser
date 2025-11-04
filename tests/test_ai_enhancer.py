import pytest
from app.services.ai_enhancer import AIEnhancerService

@pytest.mark.asyncio
async def test_resume_enhancement(test_resume_data):
    """Test AI enhancement of resume data"""
    enhancer = AIEnhancerService()
    enhanced_data = await enhancer.enhance_resume(test_resume_data)
    
    # Check structure
    assert "ai_enhancements" in enhanced_data
    enhancements = enhanced_data["ai_enhancements"]
    
    # Check scores
    assert "qualityScore" in enhancements
    assert isinstance(enhancements["qualityScore"], int)
    assert 0 <= enhancements["qualityScore"] <= 100
    
    assert "completenessScore" in enhancements
    assert isinstance(enhancements["completenessScore"], int)
    assert 0 <= enhancements["completenessScore"] <= 100
    
    # Check suggestions
    assert "suggestions" in enhancements
    assert isinstance(enhancements["suggestions"], list)
    assert len(enhancements["suggestions"]) > 0
    
    # Check industry fit
    assert "industryFit" in enhancements
    assert isinstance(enhancements["industryFit"], dict)
    for score in enhancements["industryFit"].values():
        assert 0 <= score <= 1

@pytest.mark.asyncio
async def test_quality_score_calculation(test_resume_data):
    """Test quality score calculation"""
    enhancer = AIEnhancerService()
    score = await enhancer._calculate_quality_score(test_resume_data)
    assert isinstance(score, int)
    assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_completeness_score_calculation(test_resume_data):
    """Test completeness score calculation"""
    enhancer = AIEnhancerService()
    score = await enhancer._calculate_completeness_score(test_resume_data)
    assert isinstance(score, int)
    assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_suggestion_generation(test_resume_data):
    """Test suggestion generation"""
    enhancer = AIEnhancerService()
    suggestions = await enhancer._generate_suggestions(test_resume_data)
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(s, str) for s in suggestions)

@pytest.mark.asyncio
async def test_industry_fit_analysis(test_resume_data):
    """Test industry fit analysis"""
    enhancer = AIEnhancerService()
    fit_scores = await enhancer._analyze_industry_fit(test_resume_data)
    assert isinstance(fit_scores, dict)
    assert len(fit_scores) > 0
    assert all(0 <= score <= 1 for score in fit_scores.values())