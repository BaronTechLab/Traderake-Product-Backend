from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import OTP

User = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    def authenticate(self, request, identifier=None, password=None, otp=None, **kwargs):
        if not identifier:
            # Maybe the identifier was passed under the `username` kwarg by default Django views
            identifier = kwargs.get('username')
            if not identifier:
                return None

        try:
            # Check if identifier matches username, email, or phone_number
            user = User.objects.get(
                Q(username=identifier) | 
                Q(email=identifier) | 
                Q(phone_number=identifier)
            )
        except User.DoesNotExist:
            return None

        if otp:
            # Handle Phone OTP login
            valid_otp = OTP.objects.filter(user=user, code=otp, is_used=False).order_by('-created_at').first()
            if valid_otp and valid_otp.is_valid():
                # Mark as used if you want to invalidate it upon use, 
                # but we'll need to add is_used or just delete it.
                valid_otp.delete()
                return user
            return None
            
        elif password:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        return None
