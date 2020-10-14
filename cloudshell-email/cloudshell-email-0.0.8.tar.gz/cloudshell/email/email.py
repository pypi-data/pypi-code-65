import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List

from cloudshell.email.email_config import EmailConfig

default_html = '''
<!DOCTYPE html>
<html lang="en">
<div>
    <h2 style="text-align: center;"><span style="color: #F76723;"><strong>Welcome to cloudshell-email</strong></span></h2>
</div>
<div>
    <p><span style="color: #000000;">This is the default html template using the cloudshell-email package.</span></p>
</div>
<div>
    <p><span style="color: #000000;">The cloudshell-email package can be used to send emails to users from orchestration scripts.</span></p>
</div>
<div>
    <p><span style="color: #000000;"><strong>You can view cloudshell-email usage guide here:</strong></span></p>
</div>
<div>
    <span style="color: #000000;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="https://github.com/QualiSystemsLab/cloudshell-email"> Github Repo </a>
    </span>
</div>
</body>
</html>
'''


class EmailService:

    def __init__(self, email_config: EmailConfig, logger: logging.Logger):
        self._email_config = email_config
        self._logger = logger

    def send_email(self, to_email_address: List[str], subject: str,
                   template_name: str = 'default',
                   template_parameters: Dict[str, str] = {},
                   cc_email_address: List[str] = []):

        if len(to_email_address) == 0:
            self._logger.exception('Empty list of email addresses')
            raise Exception('Empty list of email addresses')

        invalid_emails = []
        for email_address in to_email_address:
            if not self._is_valid_email_address(email_address):
                invalid_emails.append(email_address)

        for email_address in cc_email_address:
            if not self._is_valid_email_address(email_address):
                invalid_emails.append(email_address)

        invalid_string = ','.join(invalid_emails)

        if len(invalid_emails) == 1:
            self._logger.exception(f'{invalid_string} is not a valid email address')
            raise Exception(f'{invalid_string} is not a valid email address')
        elif len(invalid_emails) > 1:
            self._logger.exception(f'{invalid_string} are not valid email addresses')
            raise Exception(f'{invalid_string} are not valid email addresses')

        message = self._load_and_format_template(template_name, **template_parameters)

        self._send(to_email_address, subject, message, cc_email_address)

    def _is_valid_email_address(self, email):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        return re.search(regex, email)

    def _send(self, to_address, subject, message, cc=None):
        from_address = self._email_config.from_address
        msg = MIMEMultipart('alternative')
        msg['From'] = ';'.join(from_address) if isinstance(from_address, list) else from_address
        msg['To'] = ';'.join(to_address) if isinstance(to_address, list) else to_address
        msg['Subject'] = subject
        if cc:
            msg["Cc"] = ';'.join(cc) if isinstance(cc, list) else cc
        mess = MIMEText(message, 'html')
        msg.attach(mess)

        try:
            smtp = smtplib.SMTP(
                host=self._email_config.smtp_server,
                port=self._email_config.smtp_port
            )
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self._email_config.user, self._email_config.password)
            smtp.sendmail(
                from_addr=from_address,
                to_addrs=[to_address, cc] if cc else to_address,
                msg=msg.as_string()
            )
            smtp.close()
        except Exception:
            self._logger.exception(f'Failed to send email to {to_address}')
            raise Exception(f'Failed to send email to {to_address}')

    def _load_and_format_template(self, template_name, **extra_args):

        try:
            if template_name == 'default':
                content = default_html
            else:
                with open(template_name, 'r') as f:
                    html_string = f.read()
                    content = html_string.format(**extra_args)
        except Exception:
            self._logger.exception('Failed loading email template')
            raise Exception('Failed loading email template')

        return content
