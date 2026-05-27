from rest_framework import serializers

from .models import DocumentTemplate


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "description",
            "current_version",
            "is_active",
            "created_at",
            "updated_at",
        ]

