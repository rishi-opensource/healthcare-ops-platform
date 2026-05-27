from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from audit.services import record_audit_event

from .models import Role, User
from .permissions import IsSelfOrPrivileged, IsSuperAdmin
from .serializers import LoginSerializer, RoleSerializer, UserSerializer


class AuthLoginView(GenericAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    @extend_schema(
        request=LoginSerializer,
        responses=inline_serializer(
            name="LoginResponse",
            fields={
                "token": serializers.CharField(),
                "user": UserSerializer(),
            },
        ),
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.last_seen_at = timezone.now()
        user.save(update_fields=["last_seen_at"])
        token, _ = Token.objects.get_or_create(user=user)
        record_audit_event(
            actor_user=user,
            action="auth.login",
            target=user,
            request=request,
            metadata={"auth": "token"},
        )
        return Response({"token": token.key, "user": UserSerializer(user).data})


class AuthLogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        record_audit_event(
            actor_user=request.user,
            action="auth.logout",
            target=request.user,
            request=request,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrPrivileged]
    search_fields = ["email", "full_name", "phone"]
    ordering_fields = ["email", "full_name", "date_joined"]

    def get_queryset(self):
        queryset = User.objects.select_related("primary_branch").prefetch_related(
            "role_assignments__role",
            "role_assignments__branch",
        )
        request_user = getattr(self.request, "user", None)
        if not request_user or not request_user.is_authenticated:
            return queryset.none()
        if request_user.is_superuser or request_user.role_assignments.filter(
            role__code__in=["super_admin", "manager", "hr_payroll", "compliance"],
            ends_at__isnull=True,
        ).exists():
            return queryset
        return queryset.filter(id=request_user.id)


class RoleViewSet(ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["code", "name"]
    ordering_fields = ["name", "code"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsSuperAdmin()]
        return super().get_permissions()
