from .base import *
import os

# Production specific overrides
DEBUG = False

# Make sure ALLOWED_HOSTS is loaded properly from env
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# For production, we would set up an actual SMTP backend here
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# ... production email configs ...
