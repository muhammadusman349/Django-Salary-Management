from django.contrib import admin
from .models import User, OtpVerify
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'is_superuser']


class OtpVerifyAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'otp']
    search_fields = ['user', 'otp']


admin.site.register(User, UserAdmin)
admin.site.register(OtpVerify, OtpVerifyAdmin)
