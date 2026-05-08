from django.urls import path

from .views import (
    HealthCheckView,
    InterviewQuestionsView,
    JobMatchView,
    ResumeAnalyzeView,
    ResumeUploadView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('upload-resume/', ResumeUploadView.as_view(), name='upload-resume'),
    path('analyze-resume/<int:resume_id>/', ResumeAnalyzeView.as_view(), name='analyze-resume'),
    path(
        'generate-interview-questions/<int:resume_id>/',
        InterviewQuestionsView.as_view(),
        name='generate-interview-questions',
    ),
    path('job-match/<int:resume_id>/', JobMatchView.as_view(), name='job-match'),
]
