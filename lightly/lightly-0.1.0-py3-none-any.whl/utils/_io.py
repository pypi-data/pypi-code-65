""" I/O Operations to Store Embeddings """

# Copyright (c) 2020. Lightly AG and its affiliates.
# All Rights Reserved

from typing import List

import numpy as np
import csv

def save_embeddings(path: str,
                    embeddings: np.ndarray,
                    labels: List[int],
                    filenames: List[str]):
    """Save embeddings in a csv file.

    Args:
        path: Path to the csv file
        embeddings: Numpy array of shape n x dim
        labels: List of integer labels
        filenames: List of filenames

    """
    n_embeddings = len(embeddings)
    n_filenames = len(filenames)
    n_labels = len(labels)
    
    if n_embeddings != n_labels or n_filenames != n_labels:
        msg = 'Length of embeddings, labels, and filenames should be equal '
        msg += f' but are not: ({n_embeddings}, {n_filenames}, {n_labels})'
        raise ValueError(msg)

    header = ['filenames']
    header = header + [f'embedding_{i}' for i in range(embeddings.shape[-1])]
    header = header + ['labels']
    with open(path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        for filename, embedding, label in zip(filenames, embeddings, labels):
            writer.writerow([filename] + list(embedding) + [label])


def load_embeddings(path: str):
    """Load embeddings from a csv file

    Args:
        path: Path to the csv file

    Returns:
        embeddings: Numpy array of shape n x dim (type: float32)
        labels: List of integer labels
        filenames: List of filenames

    """
    filenames, labels = [], []
    embeddings = []
    with open(path, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for i, row in enumerate(reader):
            # skip header
            if i == 0:
                continue
            # read filenames and labels
            filenames.append(row[0])
            labels.append(int(row[-1]))
            # read embeddings
            embeddings.append(row[1:-1])

    embeddings = np.array(embeddings).astype(np.float32)
    return embeddings, labels, filenames


def load_embeddings_as_dict(path: str,
                            embedding_name: str = 'default',
                            return_all: bool = False):
    """Load embeddings from csv and store it in a dictionary which
       is fit for transfer to the web-app.
    
    Args:
        path: Path to the csv file
        embedding_name: Name of the embedding for the platform
        return_all: If true, return embeddings, labels, and filenames too
    
    Returns:
        A dictionary containing the embedding information

    """
    embeddings, labels, filenames = load_embeddings(path)

    # build dictionary
    data = {}
    data['embeddingName'] = embedding_name
    data['embeddings'] = []
    for embedding, filename, label in zip(embeddings, filenames, labels):
        item = {}
        item['fileName'] = filename
        item['value'] = embedding.tolist()
        item['label'] = label
        data['embeddings'].append(item)

    # return embeddings along with dictionary
    if return_all:
        return data, embeddings, labels, filenames
    else:
        return data

