from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from djoser.serializers import UserCreateSerializer
import re 

User = get_user_model()

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'country_code', 'phone_number', 'password', 'whatsapp_opt_in')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'country_code', 'phone_number', 'whatsapp_opt_in', 'phone_verified', 'email_verified')

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(required=False, allow_blank=True)
    otp = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")
        otp = data.get("otp")

        if password:
            user = authenticate(identifier=identifier, password=password)
            if user:
                return user
            raise serializers.ValidationError("Incorrect Credentials")
        elif otp:
            user = authenticate(identifier=identifier, otp=otp)
            if user:
                # If they successfully logged in with an OTP sent to their phone,
                # we can safely assume their phone is verified.
                if not user.phone_verified:
                    user.phone_verified = True
                    user.save(update_fields=['phone_verified'])
                return user
            raise serializers.ValidationError("Invalid OTP")
        else:
            raise serializers.ValidationError("Must include either password or otp.")


class RequestOTPSerializer(serializers.Serializer):
    country_code = serializers.CharField(max_length=5)
    phone_number = serializers.CharField(max_length=15)

    def validate_country_code(self, value):
        if not re.match(r"^\+\d{1,4}$", value):
            raise serializers.ValidationError("Invalid country code format")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only")
        return value

    

class VerifyPhoneSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
