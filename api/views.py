from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_service import (
    AIAnalysisError,
    analyze_resume,
    generate_interview_questions,
    generate_job_match,
)
from .models import Resume
from .pdf_utils import extract_text_from_pdf
from .serializers import ResumeSerializer


def api_error_response(message, status_code, code):
    return Response(
        {
            'error': {
                'code': code,
                'message': message,
            }
        },
        status=status_code,
    )


def _get_resume_or_error(resume_id):
    try:
        return Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        return None


class HealthCheckView(APIView):
    def get(self, request):
        return Response({'message': 'API is running'})


class ResumeUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return api_error_response(
                'No file uploaded. Use form field name "file".',
                status.HTTP_400_BAD_REQUEST,
                'file_missing',
            )

        if not uploaded_file.name.lower().endswith('.pdf'):
            return api_error_response(
                'Only PDF files are supported in Prompt 1.',
                status.HTTP_400_BAD_REQUEST,
                'unsupported_file_type',
            )

        extracted_text = extract_text_from_pdf(uploaded_file)
        uploaded_file.seek(0)

        resume = Resume.objects.create(
            file=uploaded_file,
            extracted_text=extracted_text,
        )

        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ResumeAnalyzeView(APIView):
    def post(self, request, resume_id):
        resume = _get_resume_or_error(resume_id)
        if not resume:
            return api_error_response('Resume not found.', status.HTTP_404_NOT_FOUND, 'resume_not_found')

        if not resume.extracted_text.strip():
            return api_error_response(
                'Resume text is empty. Upload a readable PDF first.',
                status.HTTP_400_BAD_REQUEST,
                'resume_text_empty',
            )

        try:
            result = analyze_resume(resume.extracted_text)
        except AIAnalysisError as exc:
            return api_error_response(str(exc), status.HTTP_502_BAD_GATEWAY, 'analysis_failed')
        except Exception as exc:  # noqa: BLE001
            return api_error_response(
                f'Unexpected AI processing error: {exc}',
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                'unexpected_error',
            )

        resume.analysis_result = result['analysis']
        resume.save(update_fields=['analysis_result'])

        return Response(
            {
                'resume_id': resume.id,
                'provider_used': result['provider'],
                'analysis': result['analysis'],
            },
            status=status.HTTP_200_OK,
        )


class InterviewQuestionsView(APIView):
    def post(self, request, resume_id):
        resume = _get_resume_or_error(resume_id)
        if not resume:
            return api_error_response('Resume not found.', status.HTTP_404_NOT_FOUND, 'resume_not_found')

        if not resume.extracted_text.strip():
            return api_error_response(
                'Resume text is empty. Upload a readable PDF first.',
                status.HTTP_400_BAD_REQUEST,
                'resume_text_empty',
            )

        try:
            result = generate_interview_questions(resume.extracted_text, resume.analysis_result or {})
        except AIAnalysisError as exc:
            return api_error_response(str(exc), status.HTTP_502_BAD_GATEWAY, 'interview_generation_failed')
        except Exception as exc:  # noqa: BLE001
            return api_error_response(
                f'Unexpected AI processing error: {exc}',
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                'unexpected_error',
            )

        return Response(
            {
                'resume_id': resume.id,
                'provider_used': result['provider'],
                'questions': result['questions'],
            },
            status=status.HTTP_200_OK,
        )


class JobMatchView(APIView):
    def post(self, request, resume_id):
        resume = _get_resume_or_error(resume_id)
        if not resume:
            return api_error_response('Resume not found.', status.HTTP_404_NOT_FOUND, 'resume_not_found')

        job_description = str(request.data.get('job_description', '')).strip()
        if not job_description:
            return api_error_response(
                'Job description is required.',
                status.HTTP_400_BAD_REQUEST,
                'job_description_required',
            )

        if not resume.extracted_text.strip():
            return api_error_response(
                'Resume text is empty. Upload a readable PDF first.',
                status.HTTP_400_BAD_REQUEST,
                'resume_text_empty',
            )

        try:
            result = generate_job_match(
                resume.extracted_text,
                job_description,
                resume.analysis_result or {},
            )
        except AIAnalysisError as exc:
            return api_error_response(str(exc), status.HTTP_502_BAD_GATEWAY, 'job_match_failed')
        except Exception as exc:  # noqa: BLE001
            return api_error_response(
                f'Unexpected AI processing error: {exc}',
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                'unexpected_error',
            )

        return Response(
            {
                'resume_id': resume.id,
                'provider_used': result['provider'],
                'job_description': job_description,
                'match': result['match'],
            },
            status=status.HTTP_200_OK,
        )
