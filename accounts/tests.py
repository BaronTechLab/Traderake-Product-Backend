from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class AuthenticationTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/accounts/users/' # djoser registration endpoint
        self.login_url = reverse('login') # keep custom login endpoint
        self.request_otp_url = reverse('request-otp')

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'country_code': '+1',
            'phone_number': '1234567890',
            'password': 'strongpassword123',
            'whatsapp_opt_in': True
        }

        self.verification_user_data = {
            'username': 'unverifieduser',
            'email': 'unverified@example.com',
            'country_code': '+1',
            'phone_number': '0987654321',
            'password': 'strongpassword123',
            'whatsapp_opt_in': False
        }


    def test_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.country_code, '+1')
        self.assertEqual(user.phone_number, '1234567890')
        self.assertTrue(user.whatsapp_opt_in)

    def test_login_with_username(self):
        User.objects.create_user(**self.user_data)
        
        response = self.client.post(self.login_url, {
            'identifier': 'testuser',
            'password': 'strongpassword123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_email(self):
        User.objects.create_user(**self.user_data)
        
        response = self.client.post(self.login_url, {
            'identifier': 'test@example.com',
            'password': 'strongpassword123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_phone_and_otp(self):
        user = User.objects.create_user(**self.user_data)
        
        # 1. Request OTP
        response = self.client.post(self.request_otp_url, {
            'country_code': '+1',
            'phone_number': '1234567890'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Get the generated OTP from the database
        otp_obj = OTP.objects.get(user=user)
        otp_code = otp_obj.code
        
        # 2. Login with Phone + OTP
        login_response = self.client.post(self.login_url, {
            'identifier': '1234567890',
            'otp': otp_code
        }, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        
        # Verify the OTP was deleted/used
        self.assertFalse(OTP.objects.filter(id=otp_obj.id).exists())

        # Verify that logging in with an OTP automatically set the phone to verified
        user.refresh_from_db()
        self.assertTrue(user.phone_verified)

    def test_invalid_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            'identifier': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_valid_email(self):
        user = User.objects.create_user(**self.user_data)
        response = self.client.post('/api/accounts/users/reset_password/', {'email': user.email}, format='json')
        # Djoser returns 204 No Content for a successful password reset email request
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_request_invalid_email(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post('/api/accounts/users/reset_password/', {'email': 'nonexistent@example.com'}, format='json')
        # Djoser doesn't leak emails, returns 204 either way or 400 depending on settings
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST])

    def test_password_reset_confirm_valid_token(self):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        user = User.objects.create_user(**self.user_data)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        url = '/api/accounts/users/reset_password_confirm/'
        response = self.client.post(url, {
            'uid': uidb64,
            'token': token,
            'new_password': 'newstrongpassword123',
            're_new_password': 'newstrongpassword123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        user.refresh_from_db()
        self.assertTrue(user.check_password('newstrongpassword123'))

    def test_password_reset_confirm_invalid_token(self):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        user = User.objects.create_user(**self.user_data)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        url = '/api/accounts/users/reset_password_confirm/'
        response = self.client.post(url, {
            'uid': uidb64,
            'token': 'invalid-token',
            'new_password': 'newstrongpassword123',
            're_new_password': 'newstrongpassword123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        user.refresh_from_db()
        self.assertFalse(user.check_password('newstrongpassword123'))

    def test_email_activation_and_phone_verification(self):
        # 1. Ensure user is created as inactive via Djoser API
        response = self.client.post(self.register_url, self.verification_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(username=self.verification_user_data['username'])
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_verified)
        self.assertFalse(user.phone_verified)

        # 2. Activate user (mocking Djoser activation)
        from django.contrib.auth.tokens import default_token_generator
        from djoser.utils import encode_uid
        uid = encode_uid(user.pk)
        token = default_token_generator.make_token(user)

        response = self.client.post('/api/accounts/users/activation/', {
            'uid': uid,
            'token': token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Signal should have fired and updated email_verified to True
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verified)
        self.assertFalse(user.phone_verified)

    def test_resend_activation(self):
        # 1. Create an inactive user
        response = self.client.post(self.register_url, self.verification_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Resend activation email
        from django.core import mail
        initial_outbox_len = len(mail.outbox)
        
        response = self.client.post('/api/accounts/users/resend_activation/', {
            'email': self.verification_user_data['email']
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), initial_outbox_len + 1)

        # 3. Requesting again for an active user should still return 204 or 400 depending on settings
        # By default Djoser returns 400 if user is already active
        user = User.objects.get(email=self.verification_user_data['email'])
        user.is_active = True
        user.save()
        
        response = self.client.post('/api/accounts/users/resend_activation/', {
            'email': self.verification_user_data['email']
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_email_activation_and_phone_verification(self):
        # 1. Ensure user is created as inactive via Djoser API
        response = self.client.post(self.register_url, self.verification_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(username=self.verification_user_data['username'])
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_verified)
        self.assertFalse(user.phone_verified)

        # 2. Activate user (mocking Djoser activation)
        from django.contrib.auth.tokens import default_token_generator
        from djoser.utils import encode_uid
        uid = encode_uid(user.pk)
        token = default_token_generator.make_token(user)

        response = self.client.post('/api/accounts/users/activation/', {
            'uid': uid,
            'token': token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Signal should have fired and updated email_verified to True
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verified)
        self.assertFalse(user.phone_verified)

        # 3. Simulate getting an access token to access protected views
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        # 4. Request Phone Verification OTP
        response = self.client.post(reverse('request-phone-verification-otp'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        otp_obj = OTP.objects.get(user=user, is_used=False)

        # 5. Verify Phone
        response = self.client.post(reverse('verify-phone'), {
            'otp': otp_obj.code
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.phone_verified)

    def test_logout(self):
        # 1. Login to get tokens
        User.objects.create_user(**self.user_data)
        login_response = self.client.post(self.login_url, {
            'identifier': 'testuser',
            'password': 'strongpassword123'
        }, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']

        # 2. Attempt to logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post(reverse('logout'), {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        # 3. Attempt to use the refresh token again (should fail because it's blacklisted)
        refresh_response = self.client.post('/api/accounts/jwt/refresh/', {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

