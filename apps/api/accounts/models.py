from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=64, blank=True)
    primary_branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_users",
    )
    mfa_required = models.BooleanField(default=False)
    mfa_enrolled = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    @property
    def display_name(self) -> str:
        return self.full_name or self.email


class Role(TimeStampedModel):
    class Codes(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        MANAGER = "manager", "Clinic Manager"
        HR_PAYROLL = "hr_payroll", "HR / Payroll"
        FINANCE = "finance", "Finance"
        COMPLIANCE = "compliance", "Compliance"
        RECEPTIONIST = "receptionist", "Receptionist"
        DOCTOR = "doctor", "Doctor / Practitioner"
        NURSE = "nurse", "Nurse / Clinical Assistant"
        PHARMACIST = "pharmacist", "Pharmacist / Medication Manager"
        INVENTORY = "inventory", "Inventory / Procurement"
        SUPPLIER = "supplier", "Supplier / Vendor"
        CONTRACTOR = "contractor", "Contractor / Service Provider"
        AI_AGENT = "ai_agent", "AI Agent"

    code = models.SlugField(max_length=64, unique=True, choices=Codes.choices)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RoleAssignment(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments")
    branch = models.ForeignKey(
        "core.Branch",
        on_delete=models.CASCADE,
        related_name="role_assignments",
        null=True,
        blank=True,
    )
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role", "branch"],
                name="unique_active_role_assignment_scope",
            )
        ]
        ordering = ["user__email", "role__name"]

    def __str__(self) -> str:
        scope = self.branch.name if self.branch else "global"
        return f"{self.user.email} - {self.role.code} ({scope})"

    @property
    def is_active(self) -> bool:
        now = timezone.now()
        return self.starts_at <= now and (self.ends_at is None or self.ends_at > now)

