import boto3
from django.conf import settings
 

ses_client = boto3.client(
    "ses",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)


def send_email(to_email, subject, html_content):

    response = ses_client.send_email(
        Source=settings.AWS_SES_FROM_EMAIL,
        Destination={
            "ToAddresses": [to_email]
        },
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Html": {"Data": html_content}
            }
        }
    )

    return response



# shell testing code
# def send_email(to_email, subject, html_content):

    print("------ EMAIL MOCK ------")
    print("To:", to_email)
    print("Subject:", subject)
    print("Content:", html_content)
    print("------------------------")

    return {"status": "mock_email_sent"}