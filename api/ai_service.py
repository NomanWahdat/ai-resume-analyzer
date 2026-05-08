import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Callable

import google.generativeai as genai
import requests

from .prompts import (
    ANALYSIS_RESPONSE_TEMPLATE,
    JOB_MATCH_RESPONSE_TEMPLATE,
    INTERVIEW_RESPONSE_TEMPLATE,
    build_analysis_prompt,
    build_job_match_prompt,
    build_interview_prompt,
)

logger = logging.getLogger(__name__)

MAX_PROVIDER_RETRIES = 2
RETRY_DELAY_SECONDS = 0.25


class AIAnalysisError(Exception):
    """Raised when all AI providers fail to produce a valid response."""


@dataclass
class AIProvider:
    name: str
    enabled: bool
    caller: Callable[[str], str]


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _clean_json_payload(raw_text):
    text = (raw_text or '').strip()
    if not text:
        raise ValueError('Empty AI response')

    if text.startswith('```'):
        text = text.strip('`').replace('json\n', '', 1).strip()

    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        raise ValueError('No JSON object found in AI response')

    return text[start:end + 1]


def _coerce_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _coerce_score(value):
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, score))


def _normalize_analysis_response(data):
    payload = dict(ANALYSIS_RESPONSE_TEMPLATE)
    payload['summary'] = str(data.get('summary', '')).strip()
    payload['technical_skills'] = _coerce_list(data.get('technical_skills'))
    payload['soft_skills'] = _coerce_list(data.get('soft_skills'))
    payload['strengths'] = _coerce_list(data.get('strengths'))
    payload['weaknesses'] = _coerce_list(data.get('weaknesses'))
    payload['resume_score'] = _coerce_score(data.get('resume_score'))
    payload['ats_score'] = _coerce_score(data.get('ats_score'))
    payload['improvement_suggestions'] = _coerce_list(data.get('improvement_suggestions'))
    return payload


def _normalize_interview_response(data):
    payload = dict(INTERVIEW_RESPONSE_TEMPLATE)
    payload['hr_questions'] = _coerce_list(data.get('hr_questions'))
    payload['technical_questions'] = _coerce_list(data.get('technical_questions'))
    payload['behavioral_questions'] = _coerce_list(data.get('behavioral_questions'))
    payload['project_based_questions'] = _coerce_list(data.get('project_based_questions'))
    return payload


def _normalize_job_match_response(data):
    payload = dict(JOB_MATCH_RESPONSE_TEMPLATE)
    payload['match_percentage'] = _coerce_score(data.get('match_percentage'))
    payload['matching_skills'] = _coerce_list(data.get('matching_skills'))
    payload['missing_skills'] = _coerce_list(data.get('missing_skills'))
    payload['recommendations'] = _coerce_list(data.get('recommendations'))
    payload['risk_analysis'] = str(data.get('risk_analysis', '')).strip()

    salary_level_fit = str(data.get('salary_level_fit', 'low')).strip().lower()
    payload['salary_level_fit'] = salary_level_fit if salary_level_fit in {'low', 'medium', 'high'} else 'low'
    return payload


def _parse_ai_json(raw_text, normalizer=_normalize_analysis_response):
    if isinstance(raw_text, dict):
        return normalizer(raw_text)

    payload_text = _clean_json_payload(raw_text)
    data = json.loads(payload_text)
    if not isinstance(data, dict):
        raise ValueError('AI response JSON must be an object')
    return normalizer(data)


def _analysis_prompt(resume_text):
    return build_analysis_prompt(resume_text)


def _interview_prompt(resume_text, analysis_result=None):
    return build_interview_prompt(resume_text, analysis_result=analysis_result)


def _job_match_prompt(resume_text, job_description, analysis_result=None):
    return build_job_match_prompt(resume_text, job_description, analysis_result=analysis_result)


def _call_ollama(prompt_text):
    model = os.getenv('OLLAMA_MODEL', 'llama3')
    timeout_seconds = int(os.getenv('AI_TIMEOUT_SECONDS', '45'))
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': model,
            'prompt': prompt_text,
            'stream': False,
            'format': 'json',
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    body = response.json()
    return body.get('response', '')


def _call_groq(prompt_text):
    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        raise ValueError('GROQ_API_KEY is missing')

    model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    timeout_seconds = int(os.getenv('AI_TIMEOUT_SECONDS', '45'))
    response = requests.post(
        'https://api.groq.com/openai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'model': model,
            'temperature': 0.2,
            'response_format': {'type': 'json_object'},
            'messages': [
                {'role': 'system', 'content': prompt_text},
            ],
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    body = response.json()
    content = body['choices'][0]['message']['content']
    return content


def _call_gemini(prompt_text):
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not api_key:
        raise ValueError('GEMINI_API_KEY is missing')

    model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    timeout_seconds = int(os.getenv('AI_TIMEOUT_SECONDS', '45'))
    genai.configure(api_key=api_key)
    model_client = genai.GenerativeModel(model)
    response = model_client.generate_content(
        prompt_text,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2,
            response_mime_type='application/json',
        ),
        request_options={'timeout': timeout_seconds},
    )
    return getattr(response, 'text', '')


def _provider_chain():
    return [
        AIProvider('groq', _env_flag('USE_GROQ', True), _call_groq),
        AIProvider('gemini', _env_flag('USE_GEMINI', False), _call_gemini),
        AIProvider('ollama', _env_flag('USE_LOCAL_AI', False), _call_ollama),
    ]


def _call_provider_with_retries(provider_name, caller, prompt_text, operation_name):
    last_error = None
    for attempt in range(MAX_PROVIDER_RETRIES + 1):
        start_time = time.monotonic()
        try:
            response_text = caller(prompt_text)
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            logger.info(
                'ai_call_success',
                extra={
                    'provider': provider_name,
                    'operation': operation_name,
                    'attempt': attempt + 1,
                    'duration_ms': duration_ms,
                    'status': 'success',
                },
            )
            return response_text
        except Exception as exc:  # noqa: BLE001
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            last_error = exc
            logger.warning(
                'ai_call_failure',
                extra={
                    'provider': provider_name,
                    'operation': operation_name,
                    'attempt': attempt + 1,
                    'duration_ms': duration_ms,
                    'status': 'failure',
                    'error': str(exc),
                },
            )
            if attempt < MAX_PROVIDER_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * (2 ** attempt))

    raise last_error


def _execute_ai_task(operation_name, prompt_text, response_parser, response_key, error_label):
    enabled_providers = [provider for provider in _provider_chain() if provider.enabled]
    if not enabled_providers:
        raise AIAnalysisError('No AI provider is enabled. Check USE_GROQ/USE_GEMINI/USE_LOCAL_AI.')

    errors = []
    for provider in enabled_providers:
        try:
            logger.info(
                'ai_provider_selected',
                extra={
                    'provider': provider.name,
                    'operation': operation_name,
                    'status': 'started',
                },
            )
            response_text = _call_provider_with_retries(provider.name, provider.caller, prompt_text, operation_name)
            parsed_response = _parse_ai_json(response_text, response_parser)
            logger.info(
                'ai_provider_completed',
                extra={
                    'provider': provider.name,
                    'operation': operation_name,
                    'status': 'success',
                },
            )
            return {'provider': provider.name, response_key: parsed_response}
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                'ai_provider_failed',
                extra={
                    'provider': provider.name,
                    'operation': operation_name,
                    'status': 'failure',
                },
            )
            errors.append(f'{provider.name}: {exc}')

    raise AIAnalysisError(f'Unable to complete {error_label}. ' + ' | '.join(errors))


def analyze_resume(resume_text):
    if not resume_text or not resume_text.strip():
        raise AIAnalysisError('Resume text is empty')

    return _execute_ai_task(
        operation_name='analysis',
        prompt_text=_analysis_prompt(resume_text),
        response_parser=_normalize_analysis_response,
        response_key='analysis',
        error_label='resume analysis',
    )


def generate_interview_questions(resume_text, analysis_result=None):
    if not resume_text or not resume_text.strip():
        raise AIAnalysisError('Resume text is empty')

    return _execute_ai_task(
        operation_name='interview_questions',
        prompt_text=_interview_prompt(resume_text, analysis_result=analysis_result),
        response_parser=_normalize_interview_response,
        response_key='questions',
        error_label='interview question generation',
    )


def generate_job_match(resume_text, job_description, analysis_result=None):
    if not resume_text or not resume_text.strip():
        raise AIAnalysisError('Resume text is empty')

    if not job_description or not job_description.strip():
        raise AIAnalysisError('Job description is empty')

    return _execute_ai_task(
        operation_name='job_match',
        prompt_text=_job_match_prompt(resume_text, job_description, analysis_result=analysis_result),
        response_parser=_normalize_job_match_response,
        response_key='match',
        error_label='job match analysis',
    )
