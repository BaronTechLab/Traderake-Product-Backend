import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'traderake_product_backend.settings.local')
django.setup()

from accounts.tasks import send_brevo_email

if __name__ == '__main__':
    print("Executing Celery task synchronously for debugging...")
    try:
        # Call the function directly to bypass Celery broker and see errors inline
        from accounts.tasks import brevo_session
        print(f"API Key Length in Headers: {len(brevo_session.headers.get('api-key', ''))}")
        result = send_brevo_email(
            to_email="test@example.com",
            subject="Test Celery Email Debug",
            html_content="<p>This is a test email sent synchronously.</p>"
        )
        print(f"Task result: {result}")
    except Exception as e:
        print(f"Error occurred: {e}")
