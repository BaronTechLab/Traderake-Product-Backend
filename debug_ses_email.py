import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderake_product_backend.settings.local')
django.setup()

from accounts.notifications.email import send_activation_email

if __name__ == '__main__':
    print("Triggering SES activation email via Celery...")
    try:
        send_activation_email(
            email="test@example.com",
            activation_link="http://127.0.0.1:8000/api/accounts/users/activation/?uid=test&token=test"
        )
        print("Task successfully queued to Celery!")
    except Exception as e:
        print(f"Error occurred: {e}")
