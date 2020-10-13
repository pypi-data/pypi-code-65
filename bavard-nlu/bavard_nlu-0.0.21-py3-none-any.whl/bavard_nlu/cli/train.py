import json

import click

from bavard_nlu.model import NLUModel


@click.command()
@click.option('--agent-data-file', type=click.Path(exists=True), help="Agent data file")
@click.option('--saved-model-dir', type=click.Path(exists=False), help="Directory in which to save model checkpoints")
@click.option('--batch-size', type=int, default=4)
@click.option('--epochs', type=int, default=1)
@click.option('--auto', is_flag=True)
def train(agent_data_file: str,
          saved_model_dir: str,
          batch_size: int,
          epochs: int,
          auto: bool):

    with open(agent_data_file) as f:
        agent_data = json.load(f)

    model = NLUModel(agent_data=agent_data,
                     max_seq_len=200,
                     saved_model_dir=saved_model_dir)
    model.build_and_compile_model()
    model.train(batch_size=batch_size, epochs=epochs, auto=auto)
