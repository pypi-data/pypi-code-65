import click

from bavard_nlu.cli.predict import predict
from bavard_nlu.cli.train import train


@click.group()
def cli():
    pass


cli.add_command(train)
cli.add_command(predict)


def main():
    cli()


if __name__ == '__main__':
    main()
