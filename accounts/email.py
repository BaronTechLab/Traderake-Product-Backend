from djoser.email import ActivationEmail, PasswordResetEmail
from accounts.notifications.email import send_activation_email, send_password_reset_email


class CustomActivationEmail(ActivationEmail):

    def send(self, to, *args, **kwargs):

        context = self.get_context_data()

        uid = context.get("uid")
        token = context.get("token")

        # backend activation endpoint
        activation_link = f"http://127.0.0.1:8000/api/accounts/users/activation/?uid={uid}&token={token}"

        email = to[0]

        send_activation_email(email, activation_link)


class CustomPasswordResetEmail(PasswordResetEmail):

    def send(self, to, *args, **kwargs):

        context = self.get_context_data()

        uid = context.get("uid")
        token = context.get("token")

        # Frontend password reset endpoint (using the URL defined in Djoser settings)
        # Note: If FRONTEND_DOMAIN is not set, this will be a relative path
        url = self.context.get("url")
        
        # If Djoser provides a URL we use it, otherwise we fall back (e.g. #/password/reset/confirm/{uid}/{token})
        # Assuming typical setup, we pass the uid and token.
        # Ensure your frontend URL points to the correct location for the reset page.
        reset_link = url if url else f"http://localhost:3000/password/reset/confirm/{uid}/{token}"

        email = to[0]

        send_password_reset_email(email, reset_link)