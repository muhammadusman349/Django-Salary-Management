from django.db import models
from accounts.models import User
from datetime import date
# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='leading_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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


class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
        ('INCOMPLETE', 'Information Incomplete'),
    ]
    MARITAL_STATUS = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
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
