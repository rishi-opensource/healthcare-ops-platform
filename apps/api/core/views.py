from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsSuperAdminOrReadOnly

from .models import Branch, Organization
from .serializers import BranchSerializer, OrganizationSerializer


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    search_fields = ["name", "legal_name", "trading_name"]
    ordering_fields = ["name", "created_at"]


class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.select_related("organization").all()
    serializer_class = BranchSerializer
    permission_classes = [IsSuperAdminOrReadOnly]
    search_fields = ["name", "code", "organization__name"]
    ordering_fields = ["name", "code", "created_at"]

