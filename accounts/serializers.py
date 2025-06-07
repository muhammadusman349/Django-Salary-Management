from rest_framework import serializers, status
from .models import User, OtpVerify
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import pyotp
import base64


class generatKey:
    @staticmethod
    def returnValue(userObj):
        return str(timezone.now()) + str(datetime.date(datetime.now())) + str(userObj.id)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'profile_pic', 'email', 'phone', 'role', 'is_approved', 'is_superuser', 'is_verified', 'is_staff', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')

    def get_full_name(self, obj):
        return obj.full_name


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=120, required=True, style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'password',
            'profile_pic',
            'role',
            'phone',
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        email = attrs.get('email')
        request = self.context.get('request')
        if request.method == 'POST':
            if User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError('User with this email already exists! Please try another email')
            return attrs

    def create(self, validated_data):
        if "profile_pic" in validated_data:
            profile_pic = validated_data['profile_pic']
        else:
            profile_pic = None

        newuser = User.objects.create(

        first_name=validated_data['first_name'],
        last_name=validated_data['last_name'],
        email=validated_data['email'],
        password=validated_data['password'],
        profile_pic=profile_pic,
        role=validated_data['role'],
        phone=validated_data['phone'],
        is_verified=True,
        is_active=True,
        is_approved=True,
        )
        newuser.set_password(validated_data['password'])
        newuser.save()
        return newuser


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=120, required=True)
    password = serializers.CharField(max_length=120, required=True, style={'input_type': 'password'})
    access_token = serializers.CharField(max_length=120, min_length=5, read_only=True)
    refresh_token = serializers.CharField(max_length=120, min_length=5, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'access_token',
            'refresh_token',
        ]
        read_only_fields = ('access_token', 'refresh_token')

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "provide credential are not valid/email"}, code=status.HTTP_401_UNAUTHORIZED)
        if user:
            if not user.check_password(password):
                raise serializers.ValidationError({"error": "provide credential are not valid/password"}, code=status.HTTP_401_UNAUTHORIZED)

        token = RefreshToken.for_user(user)
        attrs = {}
        attrs['id'] = str(user.id)
        attrs['first_name'] = str(user.first_name)
        attrs['last_name'] = str(user.last_name)
        attrs['email'] = str(user.email)
        attrs['access_token'] = str(token.access_token)
        attrs['refresh_token'] = str(token)
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password_confirmation = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'profile_pic', 'password', 'password_confirmation',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'role', 'is_active', 'is_verified',
            'is_approved', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'profile_pic': {'required': False},
        }

    def validate(self, attrs):
        password = attrs.get('password') or None
        password_confirmation = attrs.get('password_confirmation') or None
        phone = attrs.get('phone')

        if password or password_confirmation:
            if not password or not password_confirmation:
                raise serializers.ValidationError({
                    "password": "Both password fields are required when changing password"
                })
            if password != password_confirmation:
                raise serializers.ValidationError({
                    "password": "Passwords do not match"
                })
            if len(password) < 8:
                raise serializers.ValidationError({
                    "password": "Password must be at least 8 characters long"
                })

        if phone:
            if not phone.isdigit():
                raise serializers.ValidationError(
                    {"phone": "Phone number must contain only digits."}
                )

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirmation', None)

        profile_pic = validated_data.pop('profile_pic', None)
        print('Profile Pic:', profile_pic)
        if profile_pic:
            instance.profile_pic = profile_pic

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password and password.strip():
            instance.set_password(password)

        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password", None)
        old_password = attrs.get("old_password", None)
        try:
            user = User.objects.get(email=str(self.context['user']))
        except User.DoesNotExist:
            raise serializers.ValidationError({"error":"User not found."})
        if not user.check_password(old_password):
            raise serializers.ValidationError({"error": "Incorrect Password."})
        if new_password and len(new_password) > 5:
            if user.check_password(new_password):
                raise serializers.ValidationError({"error":"New Password should not be same as old password."})
        else:
            raise serializers.ValidationError({"error": "Minimum length of new Password should be greater than 5."})

        return attrs

    def create(self, validated_data):
        user = self.context['user']
        user.set_password(validated_data.get("new_password"))
        user.save()
        return validated_data


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email", None)
        if email is not None:
            try:
                userObj = User.objects.get(email__iexact=email)
                key = base64.b32encode(generatKey.returnValue(userObj).encode())
                otp_key = pyotp.TOTP(key)
                otp = otp_key.at(6)
                otp_obj = OtpVerify()
                otp_obj.user = userObj
                otp_obj.otp = otp
                otp_obj.save()
                # Send email with OTP
                subject = 'Password Reset OTP'
                message = f'Your OTP for password reset is: {otp}'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [email]

                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                )
            except Exception as e:
                print("Exception", e)
                raise serializers.ValidationError({"email":"Valid email is Required."})
        else:
            raise serializers.ValidationError({"email":"Email is Required."}) 
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        otp = attrs.get("otp", None)
        password = attrs.get("password", None)
        if otp:
            try:
                otpobj = OtpVerify.objects.filter(otp=otp).first()
                if otpobj:
                    otpobj.user.set_password(password)
                    otpobj.delete()
                    otpobj.user.save()
                else:
                    raise OtpVerify.DoesNotExist
            except OtpVerify.DoesNotExist:
                raise serializers.ValidationError({"error": "Valid OTP is Required"})
        else:
            raise serializers.ValidationError({"error":"Email is Required."})
        return attrs
