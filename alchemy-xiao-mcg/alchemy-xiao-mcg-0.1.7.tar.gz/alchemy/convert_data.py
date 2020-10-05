# Util script for converting a folder of wav and exp_pose to LMDB.
# Author: Xiao Li

import os
import lmdb
import pyarrow as pa
import numpy as np
import librosa
import pickle

import argparse

from multiprocessing import Process, Queue
from components.dataset import MFCCPoseExprLMDB

import warnings
warnings.filterwarnings("ignore")


def chunkIt(n, num, offset=0):
    avg = n / float(num)
    out = []
    last = 0.0

    while last < n:
        out.append([int(last + offset), int(last + offset + avg)])
        last += avg

    return out


def raw_reader(path: str):
    with open(path, 'rb') as f:
        bin_data = f.read()
    return bin_data


def dumps_pyarrow(obj):
    """
    Serialize an object.
    Returns:
        Implementation-dependent bytes-like object
    """
    return pa.serialize(obj).to_buffer()


def load_proc(file_list, metadata, pid, queue):
    print(f'Proc {pid} with {len(file_list)} items.')
    for file_dict in file_list:
        try:
            mfcc = MFCCPoseExprLMDB.audio_file_to_mfcc(file_dict['m4a'],
                                                       metadata['sr'],
                                                       metadata['win_size'],
                                                       metadata['win_interval'],
                                                       metadata['n_mfcc'])
        except:
            continue

        coeff_array = np.load(file_dict['3d_face'])
        expr_array = coeff_array[:, 80:144]
        pose_array = coeff_array[:, 224:227]

        raw_obj = dict(mfcc=mfcc, expr=expr_array, pose=pose_array)
        queue.put(raw_obj)
    queue.put(pid)


def list2lmdb(list_of_file: str, metadata: dict, write_frequency: int = 500, num_workers: int = 16):
    lmdb_path = metadata['lmdb']
    print("Generate LMDB to %s" % lmdb_path)
    isdir = os.path.isdir(lmdb_path)
    db = lmdb.open(lmdb_path, subdir=isdir,
                   map_size=1099511627776 * 2, readonly=False,
                   meminit=False, map_async=True)
    print(len(list_of_file))

    begin_ends = chunkIt(len(list_of_file), num_workers, 0)
    # Setup processes
    q = Queue(5000)
    p_list = []
    for i in range(num_workers):
        begin, end = begin_ends[i]
        p = Process(target=load_proc, args=(list_of_file[begin:end], metadata, i, q))
        p_list.append(p)
        p.start()

    txn = db.begin(write=True)
    p_finished = 0
    idx = 0
    while(True):
        if(p_finished == num_workers):
            break

        raw_obj = q.get()
        if(isinstance(raw_obj, int)):
            p_finished += 1
            continue

        txn.put(u'{}'.format(idx).encode('ascii'), dumps_pyarrow(raw_obj))
        if idx % write_frequency == 0:
            print("[%d/%d]" % (idx, len(list_of_file)))
            txn.commit()
            txn = db.begin(write=True)
        idx += 1

    # finish iterating through dataset
    txn.commit()
    keys = [u'{}'.format(k).encode('ascii') for k in range(idx + 1)]
    with db.begin(write=True) as txn:
        txn.put(b'__keys__', dumps_pyarrow(keys))
        txn.put(b'__len__', dumps_pyarrow(len(keys)))
        # Metadata
        txn.put(b'__metadata__', dumps_pyarrow(metadata))

    print("Flushing database ...")
    db.sync()
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_list", type=str)
    parser.add_argument('-p', '--procs', type=int, default=24)
    parser.add_argument("-l", "--lmdb", type=str)

    parser.add_argument("--sr", type=int, default=16000)
    parser.add_argument("--win_size", type=float, default=0.025)
    parser.add_argument("--win_interval", type=float, default=0.01)
    parser.add_argument("--n_mfcc", type=int, default=32)

    args = parser.parse_args()
    with open(args.file_list, 'rb') as f:
        file_list = pickle.load(f)

    list2lmdb(file_list, vars(args), num_workers=args.procs)
