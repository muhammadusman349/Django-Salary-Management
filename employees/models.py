from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta, date
from .utils import (department_perm_choices, position_perm_choices,
                    employee_perm_choices, organization_perm_choices)
from .import GENDER_CHOICES, STATUS_CHOICES, MARITAL_STATUS
from accounts.models import User
import secrets

# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leading_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DepartmentPermission(models.Model):
    code = models.CharField(max_length=120)
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.name)

    def get_code_name(self):
        try:
            _ = Permission.objects.get_or_create(
                codename=self.code,
                name=self.name,
                content_type=ContentType.objects.get_for_model(Department),
            )
        except Exception as e:
            print("exception in get code name DP", e)
        return self.code


class DepartmentRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    permission = models.ManyToManyField(DepartmentPermission)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(DepartmentRole, self).save(*args, **kwargs)


class Position(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    salary_range_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_range_max = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.department.name}"

    @property
    def department_name(self):
        return self.department.name


class PositionPermission(models.Model):
    code = models.CharField(max_length=120)
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.name)

    def get_code_name(self):
        try:
            _ = Permission.objects.get_or_create(
                codename=self.code,
                name=self.name,
                content_type=ContentType.objects.get_for_model(Position),
            )
        except Exception as e:
            print("exception in get code name POS", e)
        return self.code


class PositionRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    permission = models.ManyToManyField(PositionPermission)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(PositionRole, self).save(*args, **kwargs)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_employees')
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField()
    leaving_date = models.DateField(blank=True, null=True)
    personal_email = models.EmailField(blank=True)
    personal_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=100, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_on_leave = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    @property
    def tenure(self):
        end_date = self.leaving_date if self.leaving_date else date.today()
        return (end_date - self.joining_date).days // 365


class EmployeePermission(models.Model):
    code = models.CharField(max_length=120)
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.name)

    def get_code_name(self):
        try:
            _ = Permission.objects.get_or_create(
                codename=self.code,
                name=self.name,
                content_type=ContentType.objects.get_for_model(Employee),
            )
        except Exception as e:
            print("exception in get code name DP", e)
        return self.code


class EmployeeRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    permission = models.ManyToManyField(EmployeePermission)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(EmployeeRole, self).save(*args, **kwargs)


class Organization(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_of_organization')
    employees = models.ManyToManyField(Employee, related_name='members_of_organization')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class OrganizationPermission(models.Model):
    code = models.CharField(max_length=120)
    name = models.CharField(max_length=120)

    def __str__(self):
        return str(self.name)

    def get_code_name(self):
        try:
            _ = Permission.objects.get_or_create(
                codename=self.code,
                name=self.name,
                content_type=ContentType.objects.get_for_model(Organization),
            )
        except Exception as e:
            print("exception in get code name ORG", e)
        return self.code


class OrganizationRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    permission = models.ManyToManyField(OrganizationPermission)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(OrganizationRole, self).save(*args, **kwargs)


class EmployeeInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired')
    ]

    email = models.EmailField()
    token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation for {self.email} to {self.organization}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(50)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        if self._state.adding and not self.last_sent_at:
            self.last_sent_at = timezone.now()
        super().save(*args, **kwargs)

    def resend(self):
        self.expires_at = timezone.now() + timedelta(days=7)
        self.last_sent_at = timezone.now()
        self.save()
        return self

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


def setup_permissions():
    try:
        for i in department_perm_choices:
            try:
                obj, created = DepartmentPermission.objects.get_or_create(code=i[0], name=i[1])
            except Exception as e:
                print("Exception as", e)
        for i in position_perm_choices:
            try:
                obj, created = PositionPermission.objects.get_or_create(code=i[0], name=i[1])
            except Exception as e:
                print("Exception as", e)
        for i in employee_perm_choices:
            try:
                obj, created = EmployeePermission.objects.get_or_create(code=i[0], name=i[1])
            except Exception as e:
                print("Exception as", e)
        for i in organization_perm_choices:
            try:
                obj, created = OrganizationPermission.objects.get_or_create(code=i[0], name=i[1])
            except Exception as e:
                print("Exception as", e)
    except Exception as e:
        print("exception in permission creation", e)
