from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    filename = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['id', 'filename', 'file', 'extracted_text', 'analysis_result', 'uploaded_at']
        read_only_fields = ['id', 'filename', 'extracted_text', 'analysis_result', 'uploaded_at']
        extra_kwargs = {
            'file': {'write_only': True},
        }

    def get_filename(self, obj):
        return obj.file.name.split('/')[-1]
