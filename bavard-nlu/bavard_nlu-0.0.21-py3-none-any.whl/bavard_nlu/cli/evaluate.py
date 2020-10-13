import json

import click

from bavard_nlu.model import NLUModel


@click.command()
@click.option('--agent-data-file', type=click.Path(exists=True), help="Agent data file")
@click.option('--batch-size', type=int, default=4)
@click.option('--epochs', type=int, default=1)
@click.option('--auto', is_flag=True)
@click.option('--test-ratio', type=float, default=0.2)
def evaluate(agent_data_file: str,
             batch_size: int,
             epochs: int,
             auto: bool,
             test_ratio: float):

    with open(agent_data_file) as f:
        agent_data = json.load(f)

    model = NLUModel(agent_data=agent_data, max_seq_len=200)
    model.build_and_compile_model()
    train_performance, val_performance = model.evaluate(batch_size, epochs, auto, test_ratio)
    print("train performance:", train_performance)
    print("test performance:", val_performance)
