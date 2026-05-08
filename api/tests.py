import requests
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from unittest.mock import patch

from .ai_service import AIAnalysisError, _parse_ai_json, analyze_resume
from .models import Resume


def _mock_success_payload():
    return {
        'summary': 'Strong backend developer with modern web experience.',
        'technical_skills': ['Python', 'Django', 'React'],
        'soft_skills': ['Communication'],
        'strengths': ['Solid API design'],
        'weaknesses': ['Needs stronger cloud depth'],
        'resume_score': 84,
        'ats_score': 78,
        'improvement_suggestions': ['Add quantified achievements'],
    }


class AIServiceTests(TestCase):
    @patch('api.ai_service._call_ollama')
    @patch('api.ai_service._call_groq')
    @patch('api.ai_service._call_gemini')
    @patch.dict(
        'os.environ',
        {'USE_LOCAL_AI': 'False', 'USE_GROQ': 'True', 'USE_GEMINI': 'True'},
        clear=False,
    )
    def test_groq_is_primary_when_enabled(self, mock_gemini, mock_groq, mock_ollama):
        mock_groq.return_value = _mock_success_payload()

        result = analyze_resume('sample resume text')

        self.assertEqual(result['provider'], 'groq')
        self.assertEqual(result['analysis']['resume_score'], 84)
        mock_groq.assert_called_once()
        mock_gemini.assert_not_called()
        mock_ollama.assert_not_called()

    @patch('api.ai_service._call_ollama')
    @patch('api.ai_service._call_groq')
    @patch('api.ai_service._call_gemini')
    @patch.dict(
        'os.environ',
        {'USE_LOCAL_AI': 'False', 'USE_GROQ': 'True', 'USE_GEMINI': 'True'},
        clear=False,
    )
    def test_fallback_to_gemini_when_groq_fails(self, mock_gemini, mock_groq, mock_ollama):
        mock_groq.side_effect = requests.exceptions.Timeout('groq timed out')
        mock_gemini.return_value = _mock_success_payload()

        result = analyze_resume('sample resume text')

        self.assertEqual(result['provider'], 'gemini')
        mock_gemini.assert_called_once()
        mock_ollama.assert_not_called()

    @patch('api.ai_service._call_ollama')
    @patch('api.ai_service._call_groq')
    @patch('api.ai_service._call_gemini')
    @patch.dict(
        'os.environ',
        {'USE_LOCAL_AI': 'True', 'USE_GROQ': 'True', 'USE_GEMINI': 'True'},
        clear=False,
    )
    def test_fallback_to_ollama_when_cloud_providers_fail(self, mock_gemini, mock_groq, mock_ollama):
        mock_groq.side_effect = requests.exceptions.Timeout('groq timed out')
        mock_gemini.side_effect = ValueError('invalid gemini response')
        mock_ollama.return_value = _mock_success_payload()

        result = analyze_resume('sample resume text')

        self.assertEqual(result['provider'], 'ollama')
        self.assertEqual(result['analysis']['ats_score'], 78)

    @patch('api.ai_service._call_ollama')
    @patch('api.ai_service._call_groq')
    @patch('api.ai_service._call_gemini')
    @patch.dict(
        'os.environ',
        {'USE_LOCAL_AI': 'False', 'USE_GROQ': 'True', 'USE_GEMINI': 'False'},
        clear=False,
    )
    def test_timeout_returns_analysis_error(self, mock_gemini, mock_groq, mock_ollama):
        mock_groq.side_effect = requests.exceptions.Timeout('groq timed out')

        with self.assertRaises(AIAnalysisError):
            analyze_resume('sample resume text')

    def test_invalid_ai_response_handling(self):
        with self.assertRaises(ValueError):
            _parse_ai_json('not a valid json payload')


class AnalyzeResumeEndpointTests(TestCase):
    @patch('api.views.analyze_resume')
    def test_analyze_endpoint_success(self, mock_analyze_resume):
        mock_analyze_resume.return_value = {'provider': 'groq', 'analysis': _mock_success_payload()}

        resume = Resume.objects.create(
            file=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test'),
            extracted_text='Candidate with Django and React skills.',
        )

        response = self.client.post(f'/api/analyze-resume/{resume.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['provider_used'], 'groq')

    @patch('api.views.analyze_resume')
    def test_analyze_endpoint_handles_ai_failure(self, mock_analyze_resume):
        mock_analyze_resume.side_effect = AIAnalysisError('All providers failed')
        resume = Resume.objects.create(
            file=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test'),
            extracted_text='Candidate with Python experience.',
        )

        response = self.client.post(f'/api/analyze-resume/{resume.id}/')
        self.assertEqual(response.status_code, 502)
        self.assertIn('error', response.json())


class Prompt4EndpointTests(TestCase):
    @patch('api.views.generate_interview_questions')
    def test_generate_interview_questions_endpoint(self, mock_generate_questions):
        mock_generate_questions.return_value = {
            'provider': 'groq',
            'questions': {
                'hr_questions': ['Tell me about your background.'],
                'technical_questions': ['How would you design a scalable API?'],
                'behavioral_questions': ['Describe a time you handled ambiguity.'],
                'project_based_questions': ['Walk me through the most complex project on your resume.'],
            },
        }
        resume = Resume.objects.create(
            file=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test'),
            extracted_text='Candidate with Python and Django experience.',
            analysis_result={'technical_skills': ['Python', 'Django']},
        )

        response = self.client.post(f'/api/generate-interview-questions/{resume.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['provider_used'], 'groq')
        self.assertIn('technical_questions', response.json()['questions'])

    @patch('api.views.generate_job_match')
    def test_job_match_endpoint(self, mock_generate_job_match):
        mock_generate_job_match.return_value = {
            'provider': 'gemini',
            'match': {
                'match_percentage': 87,
                'matching_skills': ['Python', 'Django'],
                'missing_skills': ['AWS'],
                'recommendations': ['Highlight cloud projects'],
                'risk_analysis': 'Moderate gap in cloud experience.',
                'salary_level_fit': 'medium',
            },
        }
        resume = Resume.objects.create(
            file=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test'),
            extracted_text='Candidate with backend experience.',
            analysis_result={'technical_skills': ['Python']},
        )

        response = self.client.post(
            f'/api/job-match/{resume.id}/',
            data={'job_description': 'Python backend engineer with AWS experience.'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['provider_used'], 'gemini')
        self.assertEqual(response.json()['match']['match_percentage'], 87)

    def test_job_match_requires_job_description(self):
        resume = Resume.objects.create(
            file=SimpleUploadedFile('resume.pdf', b'%PDF-1.4 test'),
            extracted_text='Candidate with backend experience.',
        )

        response = self.client.post(f'/api/job-match/{resume.id}/', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
