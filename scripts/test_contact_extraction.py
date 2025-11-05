"""
Test contact information extraction improvements
"""

import asyncio
from app.ai import NERExtractor

# Test cases with various contact formats
TEST_RESUMES = [
    {
        "name": "Simple Contact",
        "text": """
        John Doe
        Email: john.doe@gmail.com
        Phone: (555) 123-4567
        LinkedIn: linkedin.com/in/johndoe
        """
    },
    {
        "name": "International Phone",
        "text": """
        Jane Smith
        jane.smith@company.com
        +91-9876543210
        https://www.linkedin.com/in/janesmith
        GitHub: github.com/janesmith
        """
    },
    {
        "name": "No Labels",
        "text": """
        Bob Johnson
        bob.johnson@example.org
        +1-555-987-6543
        www.bobjohnson.com
        """
    },
    {
        "name": "Various Formats",
        "text": """
        Alice Brown
        E-mail: alice.brown@tech.co.uk
        Mobile: +44-7123456789
        Portfolio: https://alicebrown.dev
        LinkedIn: www.linkedin.com/in/alicebrown
        Twitter: twitter.com/alicebrown
        """
    },
    {
        "name": "Inline Contact",
        "text": """
        Michael Chen | michael.chen@startup.io | 650-555-1234
        https://github.com/michaelchen | San Francisco, CA
        """
    },
    {
        "name": "India Format",
        "text": """
        Priya Sharma
        priya.sharma@infosys.com
        +91 98765 43210
        Bangalore, India
        linkedin.com/in/priyasharma
        """
    },
    {
        "name": "Minimal Format",
        "text": """
        David Lee
        david.lee@university.edu
        5551234567
        """
    },
    {
        "name": "Labeled Format",
        "text": """
        Sarah Martinez
        Email: sarah.m@company.com
        Phone: 555.123.4567
        Cell: (555) 987-6543
        LinkedIn: https://linkedin.com/in/sarahmartinez
        """
    }
]


async def test_contact_extraction():
    """Test contact information extraction."""
    print("=" * 80)
    print("TESTING CONTACT INFORMATION EXTRACTION")
    print("=" * 80)
    
    # Initialize NER extractor
    ner = NERExtractor()
    await ner.initialize()
    
    total_tests = len(TEST_RESUMES)
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_RESUMES, 1):
        print(f"\n\nTest {i}/{total_tests}: {test_case['name']}")
        print("-" * 80)
        print("Input text:")
        print(test_case['text'])
        print("\nExtracted:")
        
        entities = await ner.extract_entities(test_case['text'])
        
        emails = entities.get('emails', [])
        phones = entities.get('phones', [])
        urls = entities.get('urls', [])
        persons = entities.get('persons', [])
        locations = entities.get('locations', [])
        
        print(f"  Persons: {persons}")
        print(f"  Emails: {emails}")
        print(f"  Phones: {phones}")
        print(f"  URLs: {urls}")
        print(f"  Locations: {locations}")
        
        # Check if at least email OR phone was extracted
        if emails or phones:
            print("  ✅ PASS - Contact info extracted")
            passed += 1
        else:
            print("  ❌ FAIL - No contact info extracted")
            failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_tests*100:.1f}%)")
    
    if passed >= total_tests * 0.75:  # 75% pass rate
        print("\n✅ OVERALL: GOOD - Contact extraction is working!")
    elif passed >= total_tests * 0.5:  # 50% pass rate
        print("\n⚠️  OVERALL: FAIR - Contact extraction needs improvement")
    else:
        print("\n❌ OVERALL: POOR - Contact extraction needs major fixes")
    
    return passed / total_tests


async def test_on_actual_resumes():
    """Test on actual resumes from database."""
    print("\n\n" + "=" * 80)
    print("TESTING ON ACTUAL DATABASE RESUMES")
    print("=" * 80)
    
    from app.core.database import get_async_db
    from app.models import Resume
    from sqlalchemy import select
    import random
    
    async for db in get_async_db():
        # Get 100 resumes to sample from
        result = await db.execute(
            select(Resume).limit(100)
        )
        all_resumes = result.scalars().all()
        
        if len(all_resumes) == 0:
            print("No resumes found in database!")
            return
        
        # Sample 10 random resumes
        sample_size = min(10, len(all_resumes))
        sample = random.sample(all_resumes, sample_size)
        
        ner = NERExtractor()
        await ner.initialize()
        
        emails_found = 0
        phones_found = 0
        urls_found = 0
        
        print(f"\nTesting on {sample_size} random resumes...")
        
        for resume in sample:
            entities = await ner.extract_entities(resume.raw_text)
            
            if entities.get('emails'):
                emails_found += 1
            if entities.get('phones'):
                phones_found += 1
            if entities.get('urls'):
                urls_found += 1
        
        print(f"\nResults:")
        print(f"  Emails found: {emails_found}/{sample_size} ({emails_found/sample_size*100:.1f}%)")
        print(f"  Phones found: {phones_found}/{sample_size} ({phones_found/sample_size*100:.1f}%)")
        print(f"  URLs found: {urls_found}/{sample_size} ({urls_found/sample_size*100:.1f}%)")
        
        if emails_found >= sample_size * 0.5:
            print("\n✅ Email extraction: WORKING")
        else:
            print("\n❌ Email extraction: NEEDS IMPROVEMENT")
        
        if phones_found >= sample_size * 0.5:
            print("✅ Phone extraction: WORKING")
        else:
            print("❌ Phone extraction: NEEDS IMPROVEMENT")
        
        break  # Exit after first db session


async def main():
    """Run all tests."""
    # Test on synthetic data
    synthetic_score = await test_contact_extraction()
    
    # Test on actual database
    await test_on_actual_resumes()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
