from django.urls import path, include
from .views import (
    LoginAPIClient, RequestOTPAPIClient,
    RequestPhoneVerificationOTPView, VerifyPhoneView,
    LogoutAPIView
)



urlpatterns = [
    # Custom endpoints that handle our unique multis-field and OTP logic
    path('login/', LoginAPIClient.as_view(), name='login'),
    path('request-otp/', RequestOTPAPIClient.as_view(), name='request-otp'),
    
    # Phone Verification endpoints
    path('request-phone-verification-otp/', RequestPhoneVerificationOTPView.as_view(), name='request-phone-verification-otp'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),

    # Logout
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    # Djoser handles everything else (registration, password reset, standard JWT)
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]

