from .base import *

# Local development specific overrides
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Keeping console email backend for local dev
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
 