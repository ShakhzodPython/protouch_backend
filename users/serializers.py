from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import Customer
from utils.validation import validate_phone_number


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that allows authentication via phone number or email"""

    email_or_phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure phone_number is not in request body
        self.fields.pop("phone_number", None)
        self.fields.pop("email", None)  # Ensure email is not in request body

    def validate(self, attrs):
        email_or_phone = attrs.get("email_or_phone")
        password = attrs.get("password")

        if email_or_phone.isdigit():
            user = Customer.objects.filter(phone_number=email_or_phone).first()
        else:
            user = Customer.objects.filter(email=email_or_phone).first()

        if user and user.check_password(password):
            refresh = self.get_token(user)

            return {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }

        raise AuthenticationFailed(detail="Invalid credentials")


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data["access_token"] = data.pop("access")
        data.pop("refresh", None)

        return data


class CreateCustomerSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        """Validate password strength"""
        validate_password(value)
        return value

    def validate(self, attrs):
        """Check if password and confirm_password are match"""
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError(detail="Passwords don't match")
        return attrs

    def create(self, validated_data):
        """Create a new user in the database"""
        email_or_phone = validated_data.get("email_or_phone")
        password = validated_data.get("password")

        data = {"password": make_password(password)}

        if email_or_phone.isdigit():
            phone = validate_phone_number(email_or_phone)
            if Customer.objects.filter(phone_number=email_or_phone).exists():
                raise serializers.ValidationError(
                    {"email_or_phone": "User with this phone number already exists"}
                )
            data["phone_number"] = phone
        else:
            email = validate_email(email_or_phone)
            if Customer.objects.filter(email=email_or_phone).exists():
                raise serializers.ValidationError(
                    {"email_or_phone": "User with this email already exists"}
                )
            data["email"] = email

        return Customer.objects.create(**data)


class GetMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "phone_number"]


class UpdateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone_number"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
