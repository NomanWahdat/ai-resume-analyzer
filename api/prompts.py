import json

ANALYSIS_RESPONSE_TEMPLATE = {
    'summary': '',
    'technical_skills': [],
    'soft_skills': [],
    'strengths': [],
    'weaknesses': [],
    'resume_score': 0,
    'ats_score': 0,
    'improvement_suggestions': [],
}

INTERVIEW_RESPONSE_TEMPLATE = {
    'hr_questions': [],
    'technical_questions': [],
    'behavioral_questions': [],
    'project_based_questions': [],
}

JOB_MATCH_RESPONSE_TEMPLATE = {
    'match_percentage': 0,
    'matching_skills': [],
    'missing_skills': [],
    'recommendations': [],
    'risk_analysis': '',
    'salary_level_fit': 'low',
}

ANALYSIS_SYSTEM_PROMPT = """
You are a senior technical recruiter and ATS analyzer.
Analyze the resume text and return JSON only.
Do not include markdown, prose, or explanations outside JSON.
Use this exact schema:
{
  "summary": "string",
  "technical_skills": ["string"],
  "soft_skills": ["string"],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "resume_score": 0,
  "ats_score": 0,
  "improvement_suggestions": ["string"]
}
Rules:
- resume_score and ats_score must be integers between 0 and 100.
- Return concise, professional, portfolio-ready analysis.
""".strip()

INTERVIEW_SYSTEM_PROMPT = """
You are a senior technical interviewer for hiring developers.
Generate structured interview questions as JSON only.
Do not include markdown, prose, or explanations outside JSON.
Use this exact schema:
{
  "hr_questions": ["string"],
  "technical_questions": ["string"],
  "behavioral_questions": ["string"],
  "project_based_questions": ["string"]
}
Rules:
- Create realistic interview scenarios.
- Make questions relevant to the resume skills and experience.
- Increase difficulty from basic to advanced.
- Keep the output concise and practical.
""".strip()

JOB_MATCH_SYSTEM_PROMPT = """
You are an ATS analyst and career strategist.
Compare the candidate resume against the target job description and return JSON only.
Do not include markdown, prose, or explanations outside JSON.
Use this exact schema:
{
  "match_percentage": 0,
  "matching_skills": ["string"],
  "missing_skills": ["string"],
  "recommendations": ["string"],
  "risk_analysis": "string",
  "salary_level_fit": "low | medium | high"
}
Rules:
- match_percentage must be an integer between 0 and 100.
- Use ATS-style comparison logic.
- Highlight the most important skill gaps and hiring risks.
- salary_level_fit must be one of low, medium, or high.
""".strip()


def build_analysis_prompt(resume_text):
    return f'{ANALYSIS_SYSTEM_PROMPT}\n\nRESUME_TEXT:\n{resume_text}'


def build_interview_prompt(resume_text, analysis_result=None):
    analysis_blob = json.dumps(analysis_result or {}, ensure_ascii=False, indent=2)
    return (
        f'{INTERVIEW_SYSTEM_PROMPT}\n\n'
        f'RESUME_TEXT:\n{resume_text}\n\n'
        f'ANALYSIS_RESULT:\n{analysis_blob}'
    )


def build_job_match_prompt(resume_text, job_description, analysis_result=None):
    analysis_blob = json.dumps(analysis_result or {}, ensure_ascii=False, indent=2)
    return (
        f'{JOB_MATCH_SYSTEM_PROMPT}\n\n'
        f'RESUME_TEXT:\n{resume_text}\n\n'
        f'JOB_DESCRIPTION:\n{job_description}\n\n'
        f'ANALYSIS_RESULT:\n{analysis_blob}'
    )
