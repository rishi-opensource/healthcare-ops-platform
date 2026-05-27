from rest_framework import serializers

from .models import Branch, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "legal_name",
            "trading_name",
            "abn",
            "is_active",
            "created_at",
            "updated_at",
        ]


class BranchSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = Branch
        fields = [
            "id",
            "organization",
            "organization_name",
            "name",
            "code",
            "timezone",
            "address_line_1",
            "address_line_2",
            "suburb",
            "state",
            "postcode",
            "is_active",
            "created_at",
            "updated_at",
        ]

