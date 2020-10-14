import re
import time
from random import randrange
from typing import List, Callable
import os
from guerrillamail import GuerrillaMailSession

from gateways.email_utils.artifact_publisher import ArtifactPublisher
from gateways.email_utils.nada import Nada


#
# This implementation wrap the GuerrillaMail and GetNada functionality
# We may change it when staring to use a different mail service
#


class MailSession:
    def __init__(self, session):
        self.session = session

    def get_email_list(self):
        return self.session.get_email_list()

    def get_email(self, _id):
        return self.session.get_email(id)


class EmailMessage:
    def __init__(self, session: MailSession, email_id, subject, sender, datetime):
        self._id = email_id
        self.subject = subject
        self.sender = sender
        self.datetime = datetime
        self.body = None
        self._body_fetched = False
        self._session = session

    def __getattribute__(self, item):
        if item == "body":
            if not self._body_fetched:
                email = self._session.get_email(self._id)
                self.body = email.body
                self._body_fetched = True
        return super(EmailMessage, self).__getattribute__(item)


class EmailAccount:
    def __init__(self, session, email_address: str):
        self.email_address = email_address
        self._session = session

    def get_emails(self) -> List[EmailMessage]:
        all_items = []
        more = True
        while more:
            bulk_items = self._session.get_email_list()
            all_items.extend(bulk_items)
            more = len(bulk_items) >= 20

        return [
            EmailMessage(self._session, x.guid, x.subject, x.sender, x.datetime)
            for x in all_items
        ]


class EmailAccountFactory:
    @staticmethod
    def create_random(mail_type: str) -> EmailAccount:
        if mail_type == "Guerrilla":
            email_address = "{}@guerrillamailblock.com".format(
                str(randrange(9_999_999_999))
            )
            session = GuerrillaMailSession(email_address=email_address)
            assert session.get_session_state()["email_address"] == email_address
            return EmailAccount(session=session, email_address=email_address)
        if mail_type == "nada":
            session = Nada(None, "getnada.com")
            return EmailAccount(session=session, email_address=str(session))
        raise NotImplementedError(f"Unsupported mail_type: {mail_type}")


class InviteLink:
    def __init__(self, account, email, token):
        self.account = account
        self.email = email
        self.token = token


class EmailUtils:
    INTERVAL = 3
    MAX_RETRIES = 15
    COLONY_EMAIL_ADDRESS = "noreply@quali.com"

    @staticmethod
    def wait_for_new_account_email(email_account: EmailAccount) -> EmailMessage:
        results = EmailUtils._wait_for(
            email_account=email_account,
            email_type="for new account",
            body_filter=lambda body: "Jump right in to get started" in body,
        )
        return results[0]

    @staticmethod
    def wait_for_new_user_email(email_account: EmailAccount, first_name: str) -> EmailMessage:
        results = EmailUtils._wait_for(
            email_account=email_account,
            email_type="for new users",
            body_filter=lambda body: "Congratulations {}! on joining".format(first_name)
            in body,
        )
        return results[0]

    @staticmethod
    def wait_for_invite_email(email_account: EmailAccount) -> InviteLink:
        results = EmailUtils._wait_for(
            email_account=email_account,
            email_type="to invite users",
            body_filter=lambda body: "You’ve been invited" in body,
        )

        var = re.search(
            '"http.*/register?email=(.+)&account=(.+)&token=(.+)"', results[0].body
        )
        return InviteLink(email=var.group(1), account=var.group(2), token=var.group(3))

    @staticmethod
    def wait_for_active_sandbox_email(email_account: EmailAccount, sandbox_name: str) -> EmailMessage:
        results = EmailUtils._wait_for(
            email_account=email_account,
            email_type="saying the sandbox is active",
            body_filter=lambda body: f"About {sandbox_name}:"
            and "is active and ready for use" in body,
        )
        return results[0]

    @staticmethod
    def _wait_for(email_account: EmailAccount, email_type: str, body_filter: Callable) -> List[EmailMessage]:
        all_emails = []
        for current_attempt in range(0, EmailUtils.MAX_RETRIES):
            all_emails = email_account.get_emails()
            colony_emails = [
                e for e in all_emails if e.sender == EmailUtils.COLONY_EMAIL_ADDRESS
            ]
            wanted_emails = [e for e in colony_emails if body_filter(e.body)]
            found = len(wanted_emails) > 0

            from gateways.utils import Utils
            print(
                "[{TIMESTAMP} utc] Attempt {ATTEMPT}/{MAX_ATTEMPTS} {CHECK_RESULT} - "
                "{EMAIL} got {ALL_LEN} emails, "
                "{COLONY_LEN} from colony, {WANTED_LEN} {TYPE}".format(
                    TIMESTAMP=Utils.get_current_time_utc().strftime("%X"),
                    ATTEMPT=current_attempt,
                    MAX_ATTEMPTS=EmailUtils.MAX_RETRIES,
                    CHECK_RESULT="succeeded" if found else "failed",
                    EMAIL=email_account.email_address,
                    ALL_LEN=len(all_emails),
                    COLONY_LEN=len(colony_emails),
                    WANTED_LEN=len(wanted_emails),
                    TYPE=email_type,
                )
            )
            if found:
                return wanted_emails

            time.sleep(EmailUtils.INTERVAL)

        if all_emails:
            EmailUtils._write_email_to_files(all_emails)
            print(
                "Writing all {} emails to filesystem (see artifacts)".format(
                    len(all_emails)
                )
            )
        else:
            print("No email is written to filesystems")

        raise Exception(
            "Timeout: {MAX_ATTEMPTS} attempts were exhausted waiting for email {TYPE}".format(
                MAX_ATTEMPTS=EmailUtils.MAX_RETRIES, TYPE=email_type
            )
        )

    @staticmethod
    def _write_email_to_files(emails: List[EmailMessage]):
        for i, email in enumerate(emails):
            file_name = f"email-{i}.txt"
            content = (
                f"Date:    {email.datetime}\n"
                f"Subject: {email.subject}\n"
                f"Sender:  {email.sender}\n"
                f"Body:    {email.body}"
            )
            with open(os.path.join(ArtifactPublisher.current_test_path, file_name), "w") as text_file:
                print(content, file=text_file)
