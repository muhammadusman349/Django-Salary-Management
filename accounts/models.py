from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        if password is None:
            raise TypeError("User must have a password")
        user = self.create_user(email, password=password)
        user.save()

        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.is_approved = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('ADMIN', 'Admin'),
        ('HR', 'HR'),
        ('EMPLOYEE', 'Employee'),
    )

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, null=True)
    email = models.EmailField(max_length=55, unique=True)
    role = models.CharField(max_length=10, choices=ROLES, default='EMPLOYEE')
    phone = models.CharField(max_length=120, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)
    is_approved = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class OtpVerify(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()

    def __str__(self):
        return str(self.user)
