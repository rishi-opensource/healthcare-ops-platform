from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import Role, RoleAssignment, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "description", "is_system", "created_at", "updated_at"]


class RoleAssignmentSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source="role.code", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = RoleAssignment
        fields = [
            "id",
            "role",
            "role_code",
            "role_name",
            "branch",
            "branch_name",
            "starts_at",
            "ends_at",
            "is_active",
        ]


class UserSerializer(serializers.ModelSerializer):
    roles = RoleAssignmentSerializer(source="role_assignments", many=True, read_only=True)
    primary_branch_name = serializers.CharField(source="primary_branch.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "phone",
            "is_active",
            "is_staff",
            "primary_branch",
            "primary_branch_name",
            "mfa_required",
            "mfa_enrolled",
            "last_seen_at",
            "roles",
            "date_joined",
        ]
        read_only_fields = ["is_staff", "last_seen_at", "date_joined"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive")
        attrs["user"] = user
        return attrs

