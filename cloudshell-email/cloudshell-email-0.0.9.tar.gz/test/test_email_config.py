import unittest
from unittest.mock import patch, mock_open

from mock import Mock, ANY

from cloudshell.email.email_config import EmailConfig


class TestEmailConfig(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_initialize_default_port(self):
        self.email_config = EmailConfig('SMTP Host', 'user', 'pass', 'from address')

        self.assertEqual(self.email_config.smtp_server, 'SMTP Host')
        self.assertEqual(self.email_config.user, 'user')
        self.assertEqual(self.email_config.password, 'pass')
        self.assertEqual(self.email_config.from_address, 'from address')
        self.assertEqual(self.email_config.smtp_port, 587)

    def test_initialize_non_default_port(self):
        self.email_config = EmailConfig('SMTP Host', 'user', 'pass', 'from address', 9000)

        self.assertEqual(self.email_config.smtp_server, 'SMTP Host')
        self.assertEqual(self.email_config.user, 'user')
        self.assertEqual(self.email_config.password, 'pass')
        self.assertEqual(self.email_config.from_address, 'from address')
        self.assertEqual(self.email_config.smtp_port, 9000)