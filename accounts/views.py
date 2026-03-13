from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .tasks import send_sms_task
 

from .models import OTP
from .serializers import (
    UserSerializer, LoginSerializer, RequestOTPSerializer,
    VerifyPhoneSerializer, LogoutSerializer
)

User = get_user_model()


class LoginAPIClient(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

class RequestOTPAPIClient(generics.GenericAPIView):
    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        country_code = serializer.validated_data['country_code']
        phone_number = serializer.validated_data['phone_number']
        full_phone_number = f"{country_code}{phone_number}"
         
        try:
            user = User.objects.get(country_code=country_code, phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"error": "User with this phone number not found."}, status=status.HTTP_404_NOT_FOUND)

        otp = OTP.objects.create(user=user)

    
        # send OTP using celery
        send_sms_task.delay(
            full_phone_number,
            f"Your TradeRake login OTP is {otp.code}"
        ) 
        
        print(f"OTP for {phone_number} is {otp.code}")

        return Response({
            "message": "OTP generated and sent successfully.",
            "otp_code_mock": otp.code # For testing purposes only, should be removed in production
        })

class RequestPhoneVerificationOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user.email_verified:
            return Response({"error": "Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
        
        if user.phone_verified:
            return Response({"error": "Phone number is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # Invalidate old OTPs for this user
        OTP.objects.filter(user=user, is_used=False).update(is_used=True)

       
        otp = OTP.objects.create(user=user)

        full_phone_number = f"{user.country_code}{user.phone_number}"

        #send SMS using celery
        send_sms_task.delay(
            full_phone_number,
            f"Your TradeRake phone verification OTP is {otp.code}"
        )
        # for testing only
        print(f"Phone Verification OTP for {user.phone_number} is {otp.code}")

        return Response({
            "message": "Verification OTP sent successfully.",
            "otp":otp.code
        }, status=status.HTTP_200_OK)


class VerifyPhoneView(generics.GenericAPIView):
    serializer_class = VerifyPhoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp']
        user = request.user

        if user.phone_verified:
            return Response({"error": "Phone number is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # We look for a valid OTP that matches the user and isn't expired/used
            otp = OTP.objects.get(user=user, code=otp_code, is_used=False)
            
            if not otp.is_valid():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used
            otp.is_used = True
            otp.save()

            # Mark user's phone as verified
            user.phone_verified = True
            user.save(update_fields=['phone_verified'])

            return Response({"message": "Phone number verified successfully."}, status=status.HTTP_200_OK)

        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

