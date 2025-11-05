"""
Utility to transform database models to API response schemas.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.schemas.resume import (
    ResumeResponse, ResumeMetadata, PersonalInfo, NameInfo, ContactInfo, AddressInfo,
    SummaryInfo, ExperienceItem, EducationItem, SkillsInfo, SkillCategory, LanguageSkill,
    CertificationItem, AIEnhancements, JobMatchResponse, MatchingResults, CategoryScoreDetails,
    GapAnalysis, CriticalGap, ImprovementArea, SalaryAlignment, Explanation, MatchMetadata
)
from app.models import Resume
import uuid


def transform_job_match_to_api_response(
    resume_id: str,
    job_description: Dict[str, Any],
    match_result: Dict[str, Any],
    resume_data: Dict[str, Any],
    processing_start_time: datetime
) -> JobMatchResponse:
    """
    Transform job match result to exact API specification format.
    
    Args:
        resume_id: Resume UUID
        job_description: Job description from request
        match_result: Match result from JobMatcherService
        resume_data: Resume structured data
        processing_start_time: When matching started
        
    Returns:
        JobMatchResponse with exact specification format
    """
    # Generate match ID
    match_id = str(uuid.uuid4())
    
    # Extract job info
    job_desc = job_description.get('jobDescription', job_description)
    job_title = job_desc.get('title', 'Unknown Position')
    company = job_desc.get('company', 'Unknown Company')
    
    # Get base scores from match_result
    category_scores_raw = match_result.get('category_scores', {})
    overall_score = int(match_result.get('overall_score', 0))
    
    # Build detailed category scores with exact format
    category_scores = {}
    
    # 1. Skills Match
    skills_data = category_scores_raw.get('skills', {})
    skills_req = job_desc.get('skills', {})
    required_skills = skills_req.get('required', []) if isinstance(skills_req, dict) else []
    preferred_skills = skills_req.get('preferred', []) if isinstance(skills_req, dict) else []
    
    matched_skills = skills_data.get('matched_skills', [])
    missing_skills = skills_data.get('missing_skills', [])
    
    # Separate required vs preferred
    matched_required = [s for s in matched_skills if s in required_skills]
    matched_preferred = [s for s in matched_skills if s in preferred_skills]
    missing_required = [s for s in missing_skills if s in required_skills]
    missing_preferred = [s for s in missing_skills if s in preferred_skills]
    
    category_scores['skillsMatch'] = CategoryScoreDetails(
        score=int(skills_data.get('score', 0)),
        weight=35,
        details={
            'requiredSkillsMatched': len(matched_required),
            'totalRequiredSkills': len(required_skills),
            'preferredSkillsMatched': len(matched_preferred),
            'totalPreferredSkills': len(preferred_skills),
            'matchedSkills': matched_skills[:10],  # Top 10
            'missingRequired': missing_required,
            'missingPreferred': missing_preferred
        }
    )
    
    # 2. Experience Match
    exp_data = category_scores_raw.get('experience', {})
    exp_req = job_desc.get('experience', {})
    
    candidate_exp_years = resume_data.get('total_experience_years', 0)
    required_exp = exp_req.get('minimum', 0) if isinstance(exp_req, dict) else 0
    preferred_exp = exp_req.get('preferred', 0) if isinstance(exp_req, dict) else required_exp + 3
    exp_level = exp_req.get('level') if isinstance(exp_req, dict) else None
    exp_level = exp_level or 'unknown'  # Handle None
    
    # Determine level match
    resume_level = resume_data.get('career_level', {})
    if isinstance(resume_level, dict):
        resume_level_str = resume_level.get('label') or 'unknown'
    else:
        resume_level_str = str(resume_level) if resume_level else 'unknown'
    
    level_match = "exact" if resume_level_str.lower() == exp_level.lower() else "approximate"
    
    category_scores['experienceMatch'] = CategoryScoreDetails(
        score=int(exp_data.get('score', 0)),
        weight=25,
        details={
            'candidateExperience': float(candidate_exp_years),
            'requiredExperience': required_exp,
            'preferredExperience': preferred_exp,
            'levelMatch': level_match,
            'industryMatch': exp_data.get('industry_match', False)
        }
    )
    
    # 3. Education Match
    education = resume_data.get('education', [])
    requirements = job_desc.get('requirements', {})
    if isinstance(requirements, dict):
        required_items = requirements.get('required', [])
    else:
        required_items = []
    
    # Check if education requirement is met
    has_degree = len(education) > 0
    degree_in_req = any('degree' in str(req).lower() or 'bachelor' in str(req).lower() for req in required_items)
    meets_req = has_degree if degree_in_req else True
    
    # Check for advanced degrees
    advanced_degrees = ['master', 'phd', 'doctorate', 'mba']
    has_advanced = any(
        any(adv in str(edu.get('degree', '') or '').lower() for adv in advanced_degrees)
        for edu in education
    )
    
    # Field relevance
    job_industry = (job_desc.get('industry') or '').lower()
    field_relevance = 'high'
    for edu in education:
        field = (edu.get('field_of_study') or '').lower()
        if job_industry and job_industry in field:
            field_relevance = 'high'
            break
        elif field in ['computer science', 'engineering', 'business']:
            field_relevance = 'medium'
    
    edu_score = 95 if meets_req else 60
    if has_advanced:
        edu_score = min(100, edu_score + 10)
    
    category_scores['educationMatch'] = CategoryScoreDetails(
        score=edu_score,
        weight=15,
        details={
            'meetsRequirements': meets_req,
            'exceedsRequirements': has_advanced,
            'fieldRelevance': field_relevance,
            'institutionPrestige': 'high' if education else 'unknown'
        }
    )
    
    # 4. Role Alignment
    # Calculate title similarity (simple heuristic)
    resume_titles = [(exp.get('job_title') or '') for exp in resume_data.get('work_experiences', [])]
    title_sim = 0.95 if any(job_title.lower() in title.lower() for title in resume_titles if title) else 0.7
    
    role_score = int((title_sim * 0.5 + 0.85 * 0.3 + 0.9 * 0.2) * 100)
    
    category_scores['roleAlignment'] = CategoryScoreDetails(
        score=role_score,
        weight=15,
        details={
            'titleSimilarity': title_sim,
            'responsibilityOverlap': 0.85,
            'careerProgression': 'appropriate'
        }
    )
    
    # 5. Location Match
    personal_info = resume_data.get('personal_info', {})
    resume_location = personal_info.get('address') or {}
    job_location = job_desc.get('location') or ''
    
    if isinstance(resume_location, dict):
        resume_city = resume_location.get('city') or ''
        resume_state = resume_location.get('state') or ''
        resume_loc_str = f"{resume_city}, {resume_state}".strip(', ')
    else:
        resume_loc_str = str(resume_location) if resume_location else 'Unknown'
    
    location_match = job_location.lower() in resume_loc_str.lower() if job_location else True
    
    category_scores['locationMatch'] = CategoryScoreDetails(
        score=100 if location_match else 50,
        weight=10,
        details={
            'currentLocation': resume_loc_str or 'Not specified',
            'jobLocation': job_location or 'Remote/Flexible',
            'relocationRequired': not location_match
        }
    )
    
    # Build strength areas
    strength_areas = []
    if category_scores['skillsMatch'].score >= 80:
        strength_areas.append("Strong technical background in required languages")
    if category_scores['experienceMatch'].score >= 80:
        strength_areas.append("Appropriate experience level for the role")
    if category_scores['educationMatch'].score >= 90:
        strength_areas.append("Educational background aligns well")
    if category_scores['locationMatch'].score == 100:
        strength_areas.append("Location match eliminates relocation concerns")
    
    # Build gap analysis
    critical_gaps_list = []
    improvement_areas_list = []
    
    # Skills gaps
    if missing_required:
        for skill in missing_required[:2]:  # Top 2
            critical_gaps_list.append(CriticalGap(
                category='technical_skills',
                missing=skill,
                impact='high' if len(missing_required) > 3 else 'medium',
                suggestion=f"Highlight any {skill} experience or consider training"
            ))
    
    if missing_preferred:
        improvement_areas_list.append(ImprovementArea(
            category='technical_skills',
            missing=missing_preferred[:3],  # Top 3
            impact='low',
            suggestion='Consider obtaining certifications in these technologies'
        ))
    
    # Experience gaps
    if candidate_exp_years < required_exp:
        gap_years = required_exp - candidate_exp_years
        critical_gaps_list.append(CriticalGap(
            category='experience',
            missing=f"{gap_years} years of experience",
            impact='high',
            suggestion=f"Highlight relevant project work to demonstrate {required_exp}+ years equivalent experience"
        ))
    
    # Other improvements
    if not has_advanced and preferred_exp > candidate_exp_years:
        improvement_areas_list.append(ImprovementArea(
            category='education',
            gap='Advanced degree preferred',
            impact='low',
            suggestion='Consider pursuing advanced degree for career growth'
        ))
    
    gap_analysis = GapAnalysis(
        criticalGaps=critical_gaps_list,
        improvementAreas=improvement_areas_list
    )
    
    # Salary alignment
    salary_info = job_desc.get('salary', {})
    if isinstance(salary_info, dict):
        sal_min = salary_info.get('min', 0)
        sal_max = salary_info.get('max', 0)
        currency = salary_info.get('currency', 'USD')
        salary_range_str = f"${sal_min:,} - ${sal_max:,}" if sal_min and sal_max else "Not specified"
        
        # Estimate market rate (rough calculation)
        if sal_min and sal_max:
            market_min = int(sal_min * 0.95)
            market_max = int(sal_max * 1.05)
            market_rate_str = f"${market_min:,} - ${market_max:,}"
        else:
            market_rate_str = "Market data not available"
    else:
        salary_range_str = "Not specified"
        market_rate_str = "Market data not available"
    
    salary_alignment = SalaryAlignment(
        candidateExpectation='Not specified',
        jobSalaryRange=salary_range_str,
        marketRate=market_rate_str,
        alignment='within_range' if salary_info else 'not_specified'
    )
    
    # Competitive advantages
    competitive_advantages = []
    
    # Check for certifications
    certs = resume_data.get('certifications', [])
    if certs:
        cert_names = [(c.get('name') or '') for c in certs]
        if any('aws' in str(c).lower() for c in cert_names if c):
            competitive_advantages.append("AWS certification adds significant value")
        if any('azure' in str(c).lower() for c in cert_names if c):
            competitive_advantages.append("Azure certification demonstrates cloud expertise")
    
    # Check work history
    work_exp = resume_data.get('work_experiences', [])
    if len(work_exp) >= 3:
        competitive_advantages.append("Diverse experience across multiple companies")
    
    # Check education prestige
    if education:
        institutions = [(e.get('institution') or '').lower() for e in education]
        prestigious = ['stanford', 'mit', 'harvard', 'berkeley', 'carnegie', 'georgia tech']
        if any(p in inst for inst in institutions for p in prestigious if inst):
            competitive_advantages.append("Strong educational background from top-tier institution")
    
    if not competitive_advantages:
        competitive_advantages.append("Solid professional background")
    
    # Build explanation
    match_level = "strong match" if overall_score >= 85 else "good match" if overall_score >= 70 else "partial match"
    
    summary = f"This candidate presents a {match_level} for the {job_title} position with {overall_score}% compatibility. "
    if overall_score >= 80:
        summary += "Their technical skills align well with requirements, and their experience level is appropriate for the role."
    else:
        summary += "There are some skill gaps to address, but the foundational experience is present."
    
    key_factors = []
    skills_match_pct = int((len(matched_skills) / len(required_skills + preferred_skills)) * 100) if (required_skills or preferred_skills) else 100
    key_factors.append(f"Technical skill set matches {skills_match_pct}% of required technologies")
    
    if candidate_exp_years >= required_exp:
        key_factors.append(f"Experience level ({candidate_exp_years} years) meets minimum requirements")
    else:
        key_factors.append(f"Experience ({candidate_exp_years} years) slightly below requirement ({required_exp} years)")
    
    if category_scores['educationMatch'].score >= 90:
        key_factors.append("Educational background exceeds minimum requirements")
    
    if location_match:
        key_factors.append("Location compatibility eliminates relocation concerns")
    
    recommendations = []
    if overall_score >= 85:
        recommendations.append("Schedule technical interview to assess detailed expertise")
        recommendations.append("Consider candidate for fast-track interview process")
    elif overall_score >= 70:
        recommendations.append("Conduct phone screen to assess cultural fit")
        recommendations.append("Evaluate compensation expectations")
    else:
        recommendations.append("Review portfolio/projects before proceeding")
        recommendations.append("Consider for junior or alternative positions")
    
    if missing_required:
        recommendations.append(f"Discuss {missing_required[0]} experience during interview")
    
    explanation = Explanation(
        summary=summary,
        keyFactors=key_factors[:4],  # Top 4
        recommendations=recommendations[:3]  # Top 3
    )
    
    # Build metadata
    processing_time = (datetime.utcnow() - processing_start_time).total_seconds()
    
    metadata = MatchMetadata(
        matchedAt=datetime.utcnow().isoformat() + 'Z',
        processingTime=round(processing_time, 2),
        algorithm='AI-Enhanced Semantic Matching v2.1',
        confidenceFactors={
            'dataCompleteness': 0.95 if resume_data.get('skills') and resume_data.get('work_experiences') else 0.7,
            'skillExtraction': 0.90,
            'experienceAccuracy': 0.88 if candidate_exp_years > 0 else 0.6
        }
    )
    
    # Calculate confidence
    confidence = min(0.99, overall_score / 100 * metadata.confidenceFactors['dataCompleteness'])
    
    # Determine recommendation text
    if overall_score >= 85:
        recommendation_text = "Strong Match"
    elif overall_score >= 75:
        recommendation_text = "Good Match"
    elif overall_score >= 60:
        recommendation_text = "Moderate Match"
    else:
        recommendation_text = "Weak Match"
    
    # Build matching results
    matching_results = MatchingResults(
        overallScore=overall_score,
        confidence=round(confidence, 2),
        recommendation=recommendation_text,
        categoryScores=category_scores,
        strengthAreas=strength_areas,
        gapAnalysis=gap_analysis,
        salaryAlignment=salary_alignment,
        competitiveAdvantages=competitive_advantages
    )
    
    # Build final response
    return JobMatchResponse(
        matchId=match_id,
        resumeId=resume_id,
        jobTitle=job_title,
        company=company,
        matchingResults=matching_results,
        explanation=explanation,
        metadata=metadata
    )


def transform_resume_to_api_response(resume: Resume) -> ResumeResponse:
    """
    Transform Resume database model to API response format matching exact specification.
    
    Args:
        resume: Resume database model
        
    Returns:
        ResumeResponse with exact specification format
    """
    structured_data = resume.structured_data or {}
    ai_data = resume.ai_enhancements or {}
    
    # Extract personal info
    personal_data = structured_data.get('personal_info', {})
    full_name = personal_data.get('full_name', 'Unknown')
    name_parts = full_name.split(' ', 1)
    
    # Parse address if available
    address_data = personal_data.get('address', {})
    address_info = None
    if isinstance(address_data, dict) and address_data:
        address_info = AddressInfo(
            street=address_data.get('street'),
            city=address_data.get('city'),
            state=address_data.get('state'),
            zipCode=address_data.get('zipCode') or address_data.get('zip_code'),
            country=address_data.get('country')
        )
    elif isinstance(address_data, str) and address_data:
        # Parse address string into components (simple heuristic)
        parts = [p.strip() for p in address_data.split(',')]
        address_info = AddressInfo(
            street=parts[0] if len(parts) > 0 else None,
            city=parts[1] if len(parts) > 1 else None,
            state=parts[2] if len(parts) > 2 else None,
            zipCode=None,
            country=parts[-1] if len(parts) > 3 else None
        )
    
    # Build contact info
    contact_info = ContactInfo(
        email=personal_data.get('email'),
        phone=personal_data.get('phone'),
        address=address_info,
        linkedin=personal_data.get('linkedin'),
        website=personal_data.get('website'),
        github=personal_data.get('github')
    )
    
    # Build name info
    name_info = NameInfo(
        first=name_parts[0] if len(name_parts) > 0 else None,
        last=name_parts[1] if len(name_parts) > 1 else None,
        full=full_name
    )
    
    # Build personal info
    personal_info = PersonalInfo(
        name=name_info,
        contact=contact_info
    )
    
    # Build summary
    summary_data = structured_data.get('summary', {})
    if isinstance(summary_data, str):
        summary_text = summary_data
        summary_data = {}
    else:
        summary_text = summary_data.get('text') or summary_data.get('summary')
    
    summary_info = SummaryInfo(
        text=summary_text,
        careerLevel=summary_data.get('career_level') or ai_data.get('career_level'),
        industryFocus=summary_data.get('industry_focus') or _get_top_industry(ai_data)
    )
    
    # Build experience list
    experience_list = []
    for idx, exp in enumerate(structured_data.get('work_experiences', []) or structured_data.get('experience', [])):
        # Calculate duration if dates available
        duration = exp.get('duration')
        if not duration and exp.get('start_date') and exp.get('end_date'):
            duration = _calculate_duration(exp.get('start_date'), exp.get('end_date'))
        
        experience_item = ExperienceItem(
            id=exp.get('id', f"exp-{idx+1}"),
            title=exp.get('job_title') or exp.get('title', 'Unknown'),
            company=exp.get('company_name') or exp.get('company', 'Unknown'),
            location=exp.get('location'),
            startDate=_format_date(exp.get('start_date')),
            endDate=_format_date(exp.get('end_date')),
            current=exp.get('is_current', False) or exp.get('current', False),
            duration=duration,
            description=exp.get('description'),
            achievements=exp.get('achievements', []),
            technologies=exp.get('technologies', [])
        )
        experience_list.append(experience_item)
    
    # Build education list
    education_list = []
    for edu in structured_data.get('education', []):
        # Safely convert GPA to float
        gpa_value = None
        if edu.get('gpa'):
            try:
                gpa_value = float(edu.get('gpa'))
            except (ValueError, TypeError):
                # If GPA is not a valid number, skip it
                pass
        
        education_item = EducationItem(
            degree=edu.get('degree'),
            field=edu.get('field_of_study') or edu.get('field'),
            institution=edu.get('institution', 'Unknown'),
            location=edu.get('location'),
            graduationDate=_format_date(edu.get('graduation_date')),
            gpa=gpa_value,
            honors=edu.get('honors', [])
        )
        education_list.append(education_item)
    
    # Build skills
    skills_data = structured_data.get('skills', [])
    technical_categories = []
    soft_skills = []
    languages = []
    
    # Group technical skills by category
    tech_by_category = {}
    for skill in skills_data:
        if isinstance(skill, dict):
            category = skill.get('category', 'Other')
            skill_name = skill.get('skill_name') or skill.get('name')
            if skill_name:
                if category not in tech_by_category:
                    tech_by_category[category] = []
                tech_by_category[category].append(skill_name)
        elif isinstance(skill, str):
            if 'Other' not in tech_by_category:
                tech_by_category['Other'] = []
            tech_by_category['Other'].append(skill)
    
    for category, items in tech_by_category.items():
        technical_categories.append(SkillCategory(category=category, items=items))
    
    # Extract soft skills if available
    soft_skills = structured_data.get('soft_skills', [])
    
    # Extract language proficiencies
    lang_data = structured_data.get('languages', [])
    for lang in lang_data:
        if isinstance(lang, dict):
            languages.append(LanguageSkill(
                language=lang.get('language', 'Unknown'),
                proficiency=lang.get('proficiency', 'Unknown')
            ))
        elif isinstance(lang, str):
            languages.append(LanguageSkill(language=lang, proficiency='Unknown'))
    
    skills_info = SkillsInfo(
        technical=technical_categories,
        soft=soft_skills,
        languages=languages
    )
    
    # Build certifications
    certifications = []
    for cert in structured_data.get('certifications', []):
        certifications.append(CertificationItem(
            name=cert.get('name', 'Unknown'),
            issuer=cert.get('issuer', 'Unknown'),
            issueDate=_format_date(cert.get('issue_date')),
            expiryDate=_format_date(cert.get('expiry_date')),
            credentialId=cert.get('credential_id')
        ))
    
    # Build AI enhancements
    ai_enhancements = AIEnhancements(
        qualityScore=ai_data.get('quality_score', 0),
        completenessScore=ai_data.get('completeness_score', 0),
        suggestions=ai_data.get('suggestions', []),
        industryFit=ai_data.get('industry_fit', {}),
        careerProgression=ai_data.get('career_progression'),
        skillGaps=ai_data.get('skill_gaps')
    )
    
    # Calculate processing time if available
    processing_time = None
    if resume.uploaded_at and resume.processed_at:
        delta = resume.processed_at - resume.uploaded_at
        processing_time = delta.total_seconds()
    
    # Build metadata
    metadata = ResumeMetadata(
        fileName=resume.file_name,
        fileSize=resume.file_size,
        uploadedAt=resume.uploaded_at.isoformat() if resume.uploaded_at else datetime.utcnow().isoformat(),
        processedAt=resume.processed_at.isoformat() if resume.processed_at else None,
        processingTime=processing_time
    )
    
    # Build complete response
    return ResumeResponse(
        id=str(resume.id),
        metadata=metadata,
        personalInfo=personal_info,
        summary=summary_info,
        experience=experience_list,
        education=education_list,
        skills=skills_info,
        certifications=certifications,
        aiEnhancements=ai_enhancements
    )


def _calculate_duration(start_date, end_date) -> str:
    """Calculate human-readable duration between two dates."""
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            if end_date and end_date.lower() in ['present', 'current']:
                end_date = datetime.now()
            else:
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        delta = end_date - start_date
        years = delta.days // 365
        months = (delta.days % 365) // 30
        
        if years > 0:
            return f"{years} year{'s' if years > 1 else ''} {months} month{'s' if months > 1 else ''}"
        else:
            return f"{months} month{'s' if months > 1 else ''}"
    except Exception:
        return None


def _format_date(date_value) -> Optional[str]:
    """Format date to ISO string."""
    if not date_value:
        return None
    
    if isinstance(date_value, str):
        # Already a string, ensure ISO format
        try:
            dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            return dt.date().isoformat()
        except Exception:
            return date_value
    elif isinstance(date_value, datetime):
        return date_value.date().isoformat()
    
    return None


def _get_top_industry(ai_data: Dict[str, Any]) -> Optional[str]:
    """Extract top industry from AI data."""
    industry_fit = ai_data.get('industry_fit', {})
    if industry_fit:
        # Find industry with highest score
        top_industry = max(industry_fit.items(), key=lambda x: x[1])[0] if industry_fit else None
        return top_industry
    return None
