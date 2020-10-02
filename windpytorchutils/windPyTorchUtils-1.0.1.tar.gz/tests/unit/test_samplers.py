# -*- coding: UTF-8 -*-
""""
Created on 08.04.20
Unit tests for samplers
:author:     Martin Dočekal
"""
import os
import unittest
from typing import List, Any
from unittest import mock

from torch.utils.data import Dataset
from windpytorchutils.samplers import IndicesSubsampler, SlidingBatchSampler, ResumableSampler
import torch


class MockIntDataset(Dataset):
    """
    Mock up dataset for testing.
    """

    def __init__(self, lenOfDataset):
        """
        Initialization of dataset.

        :param lenOfDataset: Number of samples.
        :type lenOfDataset: int
        """

        self.lDataset = lenOfDataset

    def __len__(self):
        return self.lDataset

    def __getitem__(self, item):
        return item


class TestResumableSampler(unittest.TestCase):
    """
    Unit test of the ResumableSampler class.
    """

    pathToThisScriptFile = os.path.dirname(os.path.realpath(__file__))
    permPickleFile = os.path.join(pathToThisScriptFile, "tmp/resumable_sampler_perm.pickle")

    def setUp(self) -> None:
        self.sampler = ResumableSampler(MockIntDataset(10))
        self.samplerShuffle = ResumableSampler(MockIntDataset(10), shuffle=True)

        if os.path.exists(self.permPickleFile):
            os.remove(self.permPickleFile)

    def tearDown(self) -> None:
        if os.path.exists(self.permPickleFile):
            os.remove(self.permPickleFile)

    def test_actPerm(self):
        sampler = ResumableSampler(MockIntDataset(5), shuffle=True)

        with mock.patch("torch.randperm", lambda x: torch.tensor([1, 2, 0, 3, 4])):
            _ = next(iter(sampler))
            self.assertListEqual([1, 2, 0, 3, 4], sampler.actPerm)

    def test_resume(self):
        sampler = ResumableSampler(MockIntDataset(5), shuffle=False)
        sampler.resume([4, 3, 2, 1, 0], 0)
        self.assertListEqual(list(sampler), [4, 3, 2, 1, 0])
        self.assertListEqual(list(sampler), [0, 1, 2, 3, 4])

    def test_resume_shuffle(self):
        sampler = ResumableSampler(MockIntDataset(5), shuffle=True)
        sampler.resume([4, 3, 2, 1, 0], 2)
        self.assertListEqual(list(sampler), [2, 1, 0])

        with mock.patch("torch.randperm", lambda x: torch.tensor([0, 2, 4, 1, 3])):
            self.assertListEqual(list(sampler), [0, 2, 4, 1, 3])

    def test_len(self):
        self.assertEqual(len(self.sampler), 10)
        self.assertEqual(len(self.samplerShuffle), 10)

    def test_iterShuffle(self):
        with mock.patch("torch.randperm", lambda x: torch.tensor(list(reversed(range(x))))):
            self.assertListEqual(list(self.samplerShuffle), list(reversed(range(len(self.samplerShuffle)))))

    def test_iter(self):
        self.assertListEqual(list(self.sampler), list(range(len(self.sampler))))


class TestIndicesSubsampler(unittest.TestCase):
    """
    Unit test of the IndicesSubsampler class.
    """

    def test_sampling(self):
        """
        Test the IndicesSubsampler.
        """
        lDataset = 1000
        sampler = IndicesSubsampler(source=MockIntDataset(lDataset), subsetLen=20)

        o = [x for x in sampler]
        self.assertLess(max(o), lDataset)
        self.assertEqual(len(o), 20)
        self.assertEqual(len(set(o)), 20)


class TestSlidingBatchSampler(unittest.TestCase):
    """
    Unit test of the SlidingBatchSampler class.
    """

    def test_init(self):

        with self.assertRaises(ValueError):
            SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(10)), 0, 3, False)

        with self.assertRaises(ValueError):
            SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(10)), 10, -3, False)

        with self.assertRaises(ValueError):
            SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(10)), 10, 2, "False")

    def test_len(self):
        """
        Test the length method.
        """

        lDataset = 100
        batchSize = 3
        stride = 2

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), batchSize, stride, False)
        self.assertEqual(len(sampler), 50)

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), batchSize, stride, True)
        self.assertEqual(len(sampler), 49)

        lDataset = 0
        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), batchSize, stride, False)
        self.assertEqual(len(sampler), 0)

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), batchSize, stride,
                                      True)
        self.assertEqual(len(sampler), 0)

        lDataset = 1
        batchSize = 3
        stride = 1
        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), batchSize, stride,
                                      False)
        self.assertEqual(len(sampler), 1)

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), batchSize, stride,
                                      True)
        self.assertEqual(len(sampler), 0)

    def test_sampling(self):
        """
        Test the SlidingBatchSampler.
        """
        lDataset = 5

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 1, False)
        self.assertListEqual([x for x in sampler], [[0, 1], [1, 2], [2, 3], [3, 4]])

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 1, True)
        self.assertListEqual([x for x in sampler], [[0, 1], [1, 2], [2, 3], [3, 4]])

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 2, False)
        self.assertListEqual([x for x in sampler], [[0, 1], [2, 3], [4]])

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 2, True)
        self.assertListEqual([x for x in sampler], [[0, 1], [2, 3]])

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 3, 2, False)
        self.assertListEqual([x for x in sampler], [[0, 1, 2], [2, 3, 4]])

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 3, False)
        self.assertListEqual([x for x in sampler], [[0, 1], [3, 4]])

        lDataset = 0

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 3, False)
        self.assertListEqual([x for x in sampler], [])

        lDataset = 1

        sampler = SlidingBatchSampler(torch.utils.data.SequentialSampler(MockIntDataset(lDataset)), 2, 3, False)
        self.assertListEqual([x for x in sampler], [[0]])


if __name__ == '__main__':
    unittest.main()
