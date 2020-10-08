# -*- coding: utf-8 -*-
"""Class file for working with Sendgrid."""

import os

from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import From, Mail, To, Subject
from sendgrid.helpers import mail


class SendGrid:
    """Class for working with Sendgrid."""

    def __init__(self, api_key):
        """Initialize a class instance."""
        self.api_key = api_key

        # create a sendgrid API client
        self.client = SendGridAPIClient(self.api_key)

    # pylint: disable=too-many-arguments
    @classmethod
    def create_email_message(
            cls,
            from_email_address,
            from_email_name,
            to_email_addresses,
            subject,
            html_content,
    ):
        """Return a Mail object that can be sent with Sendgrid."""
        # create the From address
        from_email = mail.From(from_email_address, from_email_name)

        # create Subject of the message
        subject = mail.Subject(subject)

        # create a list of To email address(es)
        to_emails = []
        for email in to_email_addresses:
            to_emails.append(mail.To(email=email))

        # return a mail object
        return mail.Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=html_content
        )

    def send_email_message(self, message):
        """Send an email message using Sendgrid."""
        # send the email
        try:
            response = self.client.send(message)
        except Exception as sendgrid_error:
            print(f"ERROR: Failed sending Sendgrid email: {sendgrid_error}")
            return None

        return response
