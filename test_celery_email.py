import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderake_product_backend.settings.local')
django.setup()

from accounts.tasks import send_brevo_email

if __name__ == '__main__':
    print("Triggering Celery task: send_brevo_email...")
    result = send_brevo_email.delay(
        to_email="test@example.com",
        subject="Test Celery Email",
        html_content="<p>This is a test email sent from Celery.</p>"
    )
    print(f"Task triggered with ID: {result.id}")
    print(f"Task status: {result.status}")
