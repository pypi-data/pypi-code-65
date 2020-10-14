# coding=utf-8
# The MIT License (MIT)

# Copyright (c) Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import logging
import glob
import argparse
import math
import random
from tqdm import tqdm, trange
import pickle
import numpy as np
import torch
from torch.utils.data import DataLoader, RandomSampler
from torch.utils.data.distributed import DistributedSampler

from tokenization_unilm import UnilmTokenizer, WhitespaceTokenizer
from transformers import AdamW, get_linear_schedule_with_warmup
from modeling_unilm import UnilmForSeq2SeqDecode, UnilmConfig
# from transformers import (UnilmTokenizer, WhitespaceTokenizer,
#                           UnilmForSeq2SeqDecode, AdamW, UnilmConfig)


import utils_seq2seq

ALL_MODELS = sum((tuple(conf.pretrained_config_archive_map.keys())
                  for conf in (UnilmConfig,)), ())
MODEL_CLASSES = {
    'unilm': (UnilmConfig, UnilmForSeq2SeqDecode, UnilmTokenizer)
}

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def detokenize(tk_list):
    r_list = []
    for tk in tk_list:
        if tk.startswith('##') and len(r_list) > 0:
            r_list[-1] = r_list[-1] + tk[2:]
        else:
            r_list.append(tk)
    return r_list


def main(model_type,model_name_or_path,model_recover_path,input_file,output_file,batch_size):

    config_name=""
    tokenizer_name=""
    max_seq_length=512
    subset=0
    fp16_opt_level='01'
    split=""
    seed=123
    beam_size=5
    length_penalty=0
    forbid_ignore_word=None
    min_len=None
    ngram_size=3
    max_tgt_length=128
    fp16=False
    tokenized_input=False
    do_lower_case=True
    forbid_duplicate_ngrams=False
    need_score_traces=False
  

    if need_score_traces and beam_size <= 1:
        raise ValueError(
            "Score trace is only available for beam search with beam size > 1.")
    if max_tgt_length >= max_seq_length - 2:
        raise ValueError("Maximum tgt length exceeds max seq length - 2.")

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu")
    n_gpu = torch.cuda.device_count()

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(seed)

    model_type = model_type.lower()
    config_class, model_class, tokenizer_class = MODEL_CLASSES[model_type]
    config = config_class.from_pretrained(
        config_name if config_name else model_name_or_path, max_position_embeddings=max_seq_length)
    tokenizer = tokenizer_class.from_pretrained(
        tokenizer_name if tokenizer_name else model_name_or_path, do_lower_case=do_lower_case)

    bi_uni_pipeline = []
    bi_uni_pipeline.append(utils_seq2seq.Preprocess4Seq2seqDecode(list(tokenizer.vocab.keys()), tokenizer.convert_tokens_to_ids,
                                                                  max_seq_length, max_tgt_length=max_tgt_length))

    # Prepare model
    mask_word_id, eos_word_ids, sos_word_id = tokenizer.convert_tokens_to_ids(
        ["[MASK]", "[SEP]", "[S2S_SOS]"])
    forbid_ignore_set = None
    if forbid_ignore_word:
        w_list = []
        for w in forbid_ignore_word.split('|'):
            if w.startswith('[') and w.endswith(']'):
                w_list.append(w.upper())
            else:
                w_list.append(w)
        forbid_ignore_set = set(tokenizer.convert_tokens_to_ids(w_list))
    print(model_recover_path)
    for model_recover_path in glob.glob(model_recover_path.strip()):
        logger.info("***** Recover model: %s *****", model_recover_path)
        model_recover = torch.load(model_recover_path)
        model = model_class.from_pretrained(model_name_or_path, state_dict=model_recover, config=config, mask_word_id=mask_word_id, search_beam_size=beam_size, length_penalty=length_penalty,
                                            eos_id=eos_word_ids, sos_id=sos_word_id, forbid_duplicate_ngrams=forbid_duplicate_ngrams, forbid_ignore_set=forbid_ignore_set, ngram_size=ngram_size, min_len=min_len)
        del model_recover

        model.to(device)

        if fp16:
            try:
                from apex import amp
            except ImportError:
                raise ImportError(
                    "Please install apex from https://www.github.com/nvidia/apex to use fp16 training.")
            model = amp.initialize(model, opt_level=fp16_opt_level)

        if n_gpu > 1:
            model = torch.nn.DataParallel(model)

        torch.cuda.empty_cache()
        model.eval()
        next_i = 0
        max_src_length = max_seq_length - 2 - max_tgt_length

        with open(input_file, encoding="utf-8") as fin:
            input_lines = [x.strip() for x in fin.readlines()]
            if subset > 0:
                logger.info("Decoding subset: %d", subset)
                input_lines = input_lines[:subset]
        data_tokenizer = WhitespaceTokenizer() if tokenized_input else tokenizer
        input_lines = [data_tokenizer.tokenize(
            x)[:max_src_length] for x in input_lines]
        input_lines = sorted(list(enumerate(input_lines)),
                             key=lambda x: -len(x[1]))
        output_lines = [""] * len(input_lines)
        score_trace_list = [None] * len(input_lines)
        total_batch = math.ceil(len(input_lines) / batch_size)

        with tqdm(total=total_batch) as pbar:
            while next_i < len(input_lines):
                _chunk = input_lines[next_i:next_i + batch_size]
                buf_id = [x[0] for x in _chunk]
                buf = [x[1] for x in _chunk]
                next_i += batch_size
                max_a_len = max([len(x) for x in buf])
                instances = []
                for instance in [(x, max_a_len) for x in buf]:
                    for proc in bi_uni_pipeline:
                        instances.append(proc(instance))
                with torch.no_grad():
                    batch = utils_seq2seq.batch_list_to_batch_tensors(
                        instances)
                    batch = [
                        t.to(device) if t is not None else None for t in batch]
                    input_ids, token_type_ids, position_ids, input_mask = batch
                    traces = model(input_ids, token_type_ids,
                                   position_ids, input_mask)
                    if beam_size > 1:
                        traces = {k: v.tolist() for k, v in traces.items()}
                        output_ids = traces['pred_seq']
                    else:
                        output_ids = traces.tolist()
                    for i in range(len(buf)):
                        w_ids = output_ids[i]
                        output_buf = tokenizer.convert_ids_to_tokens(w_ids)
                        output_tokens = []
                        for t in output_buf:
                            if t in ("[SEP]", "[PAD]"):
                                break
                            output_tokens.append(t)
                        output_sequence = ' '.join(detokenize(output_tokens))
                        output_lines[buf_id[i]] = output_sequence
                        if need_score_traces:
                            score_trace_list[buf_id[i]] = {
                                'scores': traces['scores'][i], 'wids': traces['wids'][i], 'ptrs': traces['ptrs'][i]}
                pbar.update(1)
        if output_file:
            fn_out = output_file
        else:
            fn_out = model_recover_path+'.'+split
        with open(fn_out, "w", encoding="utf-8") as fout:
            for l in output_lines:
                fout.write(l)
                fout.write("\n")

        if need_score_traces:
            with open(fn_out + ".trace.pickle", "wb") as fout_trace:
                pickle.dump(
                    {"version": 0.0, "num_samples": len(input_lines)}, fout_trace)
                for x in score_trace_list:
                    pickle.dump(x, fout_trace)


if __name__ == "__main__":
    main()
