import numpy as np
import pickle
from core import QuickEncode

with open("all_bootstrap_5_0.5combo_mICA_n100.pkl", "rb") as data_pkl:
    dataset = pickle.load(data_pkl)

sequences = []
for subject, data_bundle in dataset.items():
    if len(sequences) > 1000:
        break

    time_series = data_bundle["timeseries"]
    if data_bundle["timeseries"].shape[1] == 88:
        sequences.extend(time_series.tolist())

encoder, decoder, embeddings, f_loss = QuickEncode(
    sequences,
    embedding_dim=50,
    logging=True,
    epochs=500
)

with open("embeddings.pkl", "wb") as embeddings_pkl:
    pickle.dump(embeddings, embeddings_pkl)

with open("encoder.pkl", "wb") as encoder_pkl:
    pickle.dump(encoder, encoder_pkl)

with open("decoder.pkl", "wb") as decoder_pkl:
    pickle.dump(decoder, decoder_pkl)
