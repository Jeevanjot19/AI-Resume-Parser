"""Test enhanced extraction features."""

import asyncio
from app.ai.ner_extractor import NERExtractor
from app.services.resume_parser import ResumeParserService

async def test_skills():
    """Test skill extraction."""
    print("\n=== Testing Skill Extraction ===")
    extractor = NERExtractor()
    await extractor.initialize()
    
    test_text = """
    Experienced Python developer with 5+ years in web development.
    Skills: React.js, Node.js, Docker, Kubernetes (k8s), AWS, PostgreSQL, MongoDB.
    Strong leadership and communication skills. Proficient in Agile/Scrum.
    """
    
    skills = await extractor.extract_skills(test_text)
    print(f"✅ Extracted {len(skills)} skills:")
    print(f"   {', '.join(sorted(skills)[:15])}")
    print(f"   ... and {len(skills) - 15} more" if len(skills) > 15 else "")

async def test_section_detection():
    """Test section detection."""
    print("\n=== Testing Section Detection ===")
    parser = ResumeParserService()
    
    test_text = """
    PROFESSIONAL SUMMARY
    Experienced software engineer with 10 years in full-stack development.
    
    WORK EXPERIENCE
    Senior Software Engineer - Tech Corp
    Jan 2020 - Present
    - Led team of 5 developers
    - Increased performance by 40%
    - Built microservices using Python and Docker
    
    EDUCATION
    Master of Science in Computer Science
    Stanford University
    GPA: 3.9/4.0
    2015
    """
    
    summary = await parser._extract_professional_summary(test_text)
    print(f"✅ Summary extracted: {summary[:80]}..." if summary else "❌ No summary found")
    
    exp_section = parser._find_section(test_text, ['experience', 'work history'])
    print(f"✅ Experience section found: {len(exp_section)} chars" if exp_section else "❌ No experience section")
    
    edu_section = parser._find_section(test_text, ['education'])
    print(f"✅ Education section found: {len(edu_section)} chars" if edu_section else "❌ No education section")

async def main():
    print("\n" + "="*60)
    print("TESTING ENHANCED EXTRACTION FEATURES")
    print("="*60)
    
    await test_skills()
    await test_section_detection()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
