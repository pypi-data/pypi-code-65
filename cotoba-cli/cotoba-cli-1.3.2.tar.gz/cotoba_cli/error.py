import click
import http.client


class ApiResponseError(click.ClickException):
    exit_code = 3

    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def format_message(self):
        return f'Api response error: {self.error_status()}'

    def __str__(self):
        return self.format_message()

    def show(self):
        # This method is just for testing.
        # DO NOT call from production code.
        click.secho(self.format_message(), err=True, fg='red')
        click.echo(self.body)

    def error_status(self):
        status_text = http.client.responses[self.status_code]
        return f'{self.status_code} {status_text}'
