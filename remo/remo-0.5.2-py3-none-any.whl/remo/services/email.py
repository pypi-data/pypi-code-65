import logging

from typing import List
from sendgrid import SendGridAPIClient, HtmlContent, Mail, Attachment

logger = logging.getLogger('remo_app')


def send_email(
        subject: str, content: str,
        from_email: str = None, to_emails: List[str] = None,
        attachment: Attachment = None
) -> bool:
    from django.conf import settings
    if not from_email:
        from_email = settings.REMO_EMAIL
    if not to_emails:
        to_emails = settings.EMAIL_LIST

    mail = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=HtmlContent(content),
    )

    if attachment:
        mail.attachment = attachment

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(mail)
    except Exception as err:
        logger.error(f'Failed to send email: {err}')
        return False

    return True


def compose_msg(req, resp):
    return f"""
<html>
    <body>
        <p>Failed to register user: </br>
        Request: {req}. </br>
        Response: {resp}</p>
    </body>
</html>
"""
