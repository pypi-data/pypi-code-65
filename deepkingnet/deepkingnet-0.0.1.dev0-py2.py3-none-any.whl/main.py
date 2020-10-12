import click
import gzip
from deepkingnet import *
from deepkingnet.help import CustomHelp
from Bio import SeqIO
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from os.path import join
import numpy as np
import random

def onehot_encode(seq, size, padding='right'):
  vec = np.zeros((size, 4))
  if not isinstance(seq, str):
    seq = ''
  for i, c in enumerate(seq.upper()):
    if padding == 'left':
      i = i + size - len(seq)
    if c == 'A':
      vec[i, 0] = 1
    elif c == 'C':
      vec[i, 1] = 1
    elif c == 'G':
      vec[i, 2] = 1
    elif c == 'T':
      vec[i, 3] = 1
  
  return vec


def recall_m(y_true, y_pred):
	true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
	possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
	recall = true_positives / (possible_positives + K.epsilon())
	return recall

def precision_m(y_true, y_pred):
	true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
	predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
	precision = true_positives / (predicted_positives + K.epsilon())
	return precision

def f1_m(y_true, y_pred):
	precision = precision_m(y_true, y_pred)
	recall = recall_m(y_true, y_pred)
	return 2*((precision*recall)/(precision+recall+K.epsilon()))

@click.group(cls=CustomHelp)
def cli():
    """Command-line tool to predict and annotate small protein sequences in genomic sequencing data"""
    pass


@cli.command(short_help='Run DeepKingNet on a specific position in a FASTA file', help_priority=1)
@click.argument('fasta', type=click.Path(exists=True))
@click.argument('loc', nargs=-1)
def site(fasta, loc):
    """A click access point for the run module. This is used for creating the command line interface."""
    log_params(command='site', fasta=fasta, loc=loc)
    _site(fasta, loc)

def _site(fasta, loc, header=True):

    if fasta.endswith(".gz"):
        fasta = {rec.id:str(rec.seq) for rec in SeqIO.parse(gzip.open(fasta, 'rt'), 'fasta')}
    else:
        fasta = {rec.id:str(rec.seq) for rec in SeqIO.parse(fasta, 'fasta')}

    if header:
        print('loc', 'seqlen', 'origin', 'prob', 'perc_N', sep='\t')
    loaded_models = dict()
    for l in loc:
        contig = fasta[l.split(':')[0]]
        position = int(l.split(':')[1])
        toplength = 0
        for seqlen in [100, 200, 300, 500, 1000, 2000, 3000, 4000, 5000, 10000]:
            if position - (seqlen/2) < 0:
                break
            if position + (seqlen/2) > len(contig):
                break
            toplength = seqlen
        
        if toplength == 0:
            print(l, '0bp', "NA", "NA", "NA", sep='\t')
            continue

        cutseq = contig[int(position - (toplength/2)):int(position + (toplength/2))].upper()

        modsize = None
        if toplength == 100:
            modsize = '100bp'
        elif toplength == 200:
            modsize = '200bp'
        elif toplength == 300:
            modsize = '300bp'
        elif toplength == 500:
            modsize = '500bp'
        elif toplength == 1000:
            modsize = '1kb'
        elif toplength == 2000:
            modsize = '2kb'
        elif toplength == 3000:
            modsize = '3kb'
        elif toplength == 4000:
            modsize = '4kb'
        elif toplength == 5000:
            modsize = '5kb'
        elif toplength == 10000:
            modsize = '10kb'
    
        if modsize in loaded_models:
            model = loaded_models[modsize]
        else:
            model = load_model(join(DATA_PATH, modsize+'.model.h5'), custom_objects={'recall_m':recall_m, 'precision_m': precision_m, 'f1_m': f1_m})
            loaded_models[modsize] = model

        pred = model.predict(np.array([onehot_encode(cutseq, toplength)]))
        prob = pred[0][0]
        origin = 'eukaryotic'
        if prob <= 0.5:
            origin = 'prokaryotic'
        print(l, modsize, origin, prob, (cutseq.count("N")/toplength)*100, sep='\t')


@cli.command(short_help='Run DeepKingNet on a specific contig in a FASTA file', help_priority=1)
@click.argument('fasta', type=click.Path(exists=True))
@click.argument('loc', nargs=-1)
@click.option('--samples', '-s', default=20)
def contig(fasta, loc, samples):
    """A click access point for the run module. This is used for creating the command line interface."""
    log_params(command='site', fasta=fasta, loc=loc, samples=samples)
    
    if fasta.endswith(".gz"):
        genome = {rec.id:str(rec.seq) for rec in SeqIO.parse(gzip.open(fasta, 'rt'), 'fasta')}
    else:
        genome = {rec.id:str(rec.seq) for rec in SeqIO.parse(fasta, 'fasta')}

    print('loc', 'seqlen', 'origin', 'prob', 'perc_N', sep='\t')
    for l in loc:
        contig_length = len(genome[l])
        positions = (random.choices(list(range(50, contig_length-50)), k=samples))
        locs = [l+':'+str(pos) for pos in positions]
        _site(fasta, locs, header=False)


def log_params(**kwargs):
    click.echo("#### PARAMETERS ####")
    click.echo('\n'.join(list(map(lambda x: ': '.join(list(map(str, x))), kwargs.items()))))
    click.echo("####################")

if __name__ == '__main__':

    cli()
