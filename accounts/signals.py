from django.dispatch import receiver
from djoser.signals import user_activated
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(user_activated)
def set_email_verified_true(user, request, **kwargs):
    """
    When Djoser activates a user (via their email activation flow),
    we automatically mark their email as verified in our custom model.
    """
    user.email_verified = True
    user.save(update_fields=['email_verified'])
