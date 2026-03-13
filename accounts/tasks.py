from celery import shared_task
from .services.aws_ses import send_email
from .services.aws_sns import send_sms


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
def send_email_task(self, to_email, subject, html_content):
    """
    Optimized Celery task to send a transactional email via AWS SES.
    Utilizes connection pooling and exponential backoff for retries.
    """
    response = send_email(to_email, subject, html_content)
    return response

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
def send_sms_task(self, phone_number, message):
    """
    Celery task to send a transactional SMS via AWS SNS.
    Utilizes connection pooling and exponential backoff for retries.
    """
    response = send_sms(phone_number, message)
    return response



# for console test for email send
# from celery import shared_task
# from .services.aws_ses import send_email


# @shared_task
# def send_email_task(to_email, subject, html_content):

#     return send_email(to_email, subject, html_content)



