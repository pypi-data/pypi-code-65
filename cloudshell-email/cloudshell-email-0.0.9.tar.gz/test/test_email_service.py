import unittest
from unittest.mock import patch, mock_open

from mock import Mock, ANY

from cloudshell.email.email import EmailService


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

arg_html = '''
<!DOCTYPE html>
<html lang="en">
<div>
    <h2 style="text-align: center;"><span style="color: #F76723;"><strong>Welcome to Training</strong></span></h2>
</div>
<div>
    <p><span style="color: #000000;">Please retain this email as it is how you will access your online lab environment. It also contains your credentials (if needed) and links to helpful materials.</span></p>
</div>
<div>
    <p><span style="color: #000000;">I&rsquo;m looking forward to our class together</span></p>
</div>
<div>
    <p><span style="color: #000000;"><strong>To access your CloudShell Environment please use the following:</strong></span></p>
</div>
<div>
    <span style="color: #000000;"><span style="color: #F76723;"><strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Environment details:</strong></span></span><br>
</div>
<div>
    <span style="color: #000000;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href="{sandbox_link}"> Environment Link </a>
    </span>
</div>
</body>
</html>
'''

not_default_html = '''
{sandbox_link}
'''

args_html = '''
{arg1}
{arg2}
{arg3}
'''


class TestEmailService(unittest.TestCase):

    def setUp(self) -> None:
        self.email_config = Mock()
        self.logger = Mock()
        self.email_service = EmailService(self.email_config, self.logger)

    def test_send_no_email_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()

        # act
        excepted = False
        try:
            self.email_service.send_email([], Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'Empty list of email addresses')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_send_email_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        invalid_email = 'aaa@bbb'

        #act
        excepted = False
        try:
            self.email_service.send_email([invalid_email], Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb is not a valid email address')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_send_email_valid_and_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'
        invalid_email = 'aaa@bbb'

        # act
        excepted = False
        try:
            self.email_service.send_email([valid_email, invalid_email], Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb is not a valid email address')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_send_email_mulitple_valid_and_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'
        valid_email2 = 'aaa2@bbb.com'
        valid_email3 = 'aaa3@bbb.com'
        invalid_email = 'aaa@bbb'
        invalid_email2 = 'aaa2@bbb'
        invalid_email3 = 'aaa3@bbb'

        emails = [invalid_email, invalid_email2, valid_email, valid_email2, invalid_email3, valid_email3]

        # act
        excepted = False
        try:
            self.email_service.send_email(emails, Mock())
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb,aaa2@bbb,aaa3@bbb are not valid email addresses')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_cc_send_email_mulitple_valid_and_invalid_address(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'
        valid_email2 = 'aaa2@bbb.com'
        valid_email3 = 'aaa3@bbb.com'
        invalid_email = 'aaa@bbb'
        invalid_email2 = 'aaa2@bbb'
        invalid_email3 = 'aaa3@bbb'

        emails = [invalid_email, invalid_email2, valid_email, valid_email2, invalid_email3, valid_email3]

        # act
        excepted = False
        try:
            self.email_service.send_email([valid_email], Mock(), cc_email_address=emails)
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'aaa@bbb,aaa2@bbb,aaa3@bbb are not valid email addresses')

        # assert
        self.assertTrue(excepted)
        self.email_service._load_and_format_template.assert_not_called()
        self.email_service._send.assert_not_called()

    def test_cc_send_email_valid(self):
        # arrange
        self.email_service._load_and_format_template = Mock()
        self.email_service._send = Mock()
        valid_email = 'aaa@bbb.com'

        # act
        self.email_service.send_email([valid_email], Mock())

        # assert
        self.email_service._load_and_format_template.assert_called_once()
        self.email_service._send.assert_called_once()

    def test_is_valid_email_address_pass(self):
        valid_email = 'aaa@bbb.com'

        self.assertTrue(self.email_service._is_valid_email_address(valid_email))

    def test_is_valid_email_address_fail(self):
        invalid_email = 'aaa@bbb'

        self.assertFalse(self.email_service._is_valid_email_address(invalid_email))

    def test_load_default_template(self):
        # arrange
        self.email_service._send = Mock()

        # act
        content = self.email_service._load_and_format_template('default')

        # assert
        self.assertEqual(content, default_html)

    def test_load_template(self):
        # arrange
        self.email_service._send = Mock()

        arg = dict()
        arg['sandbox_link'] = 'Portal Link'

        # act
        with patch("builtins.open", mock_open(read_data=not_default_html)) as mock_file:
            content = self.email_service._load_and_format_template('', **arg)

        # assert
        self.assertEqual(content, not_default_html.format(**arg))

    def test_load_template_with_args(self):
        # arrange
        self.email_service._send = Mock()

        extra_args = dict()
        extra_args['arg1'] = 'argument1'
        extra_args['arg2'] = 'argument2'
        extra_args['arg3'] = 'argument3'

        # act
        with patch("builtins.open", mock_open(read_data=args_html)) as mock_file:
            content = self.email_service._load_and_format_template('', **extra_args)

        # assert
        self.assertEqual(content, args_html.format(**extra_args))

    @patch('builtins.open', side_effect=Exception())
    def test_load_template_exception(self, mock_open):
        # arrange
        self.email_service._send = Mock()

        # act
        excepted = False
        try:
            self.email_service._load_and_format_template('')
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], 'Failed loading email template')
        self.assertTrue(excepted)

    @patch('smtplib.SMTP')
    def test_send(self, mock_smtp):
        # arrange
        email = 'aaa@bbb.com'
        self.email_service._email_config.from_address = 'aaa@bbb.com'

        smtp_obj = Mock()
        smtp_obj.ehlo = Mock()
        smtp_obj.starttls = Mock()
        smtp_obj.login = Mock()
        smtp_obj.sendmail = Mock()
        smtp_obj.close = Mock()

        mock_smtp.return_value = smtp_obj

        # act
        self.email_service._send([email], 'Default Subject', arg_html, [email])

        # assert
        mock_smtp.return_value.ehlo.assert_called_once()
        mock_smtp.return_value.starttls.assert_called_once()
        mock_smtp.return_value.login.assert_called_once()
        mock_smtp.return_value.sendmail.assert_called_once()
        mock_smtp.return_value.close.assert_called_once()

    @patch('smtplib.SMTP', side_effect=Exception())
    def test_send_exception(self, mock_smtp):
        # arrange
        email = 'aaa@bbb.com'
        self.email_service._email_config.from_address = email = 'aaa@bbb.com'

        # act
        excepted = False
        try:
            self.email_service._send([email], 'Default Subject', arg_html, [email])
        except Exception as e:
            excepted = True
            self.assertEqual(e.args[0], "Failed to send email to ['aaa@bbb.com']")
        self.assertTrue(excepted)



