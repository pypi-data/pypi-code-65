import click

from bavard_nlu.cli.predict import predict
from bavard_nlu.cli.train import train
from bavard_nlu.cli.evaluate import evaluate


@click.group()
def cli():
    pass


cli.add_command(train)
cli.add_command(predict)
cli.add_command(evaluate)


def main():
    cli()


if __name__ == '__main__':
    main()
