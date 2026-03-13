from accounts.tasks import send_email_task


def send_activation_email(email, activation_link):

    subject = "Activate your TradeRake account"

    html_content = f"""
    <h2>Welcome to TradeRake</h2>

    <p>Please click the link below to activate your account:</p>

    <a href="{activation_link}">
        Activate Account
    </a>

    <p>This link will expire soon.</p>
    """

    send_email_task.delay(email, subject, html_content)


def send_password_reset_email(email, reset_link):

    subject = "Reset your TradeRake password"

    html_content = f"""
    <h2>TradeRake Password Reset</h2>

    <p>You're receiving this email because you requested a password reset for your user account at TradeRake.</p>
    <p>Please go to the following page and choose a new password:</p>

    <a href="{reset_link}">
        Reset Password
    </a>

    <p>If you didn't request a password reset, you can safely ignore this email.</p>
    """

    send_email_task.delay(email, subject, html_content)
