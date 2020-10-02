# -*- coding: UTF-8 -*-
""""
Created on 03.11.19
Unit tests for torch utils module.

:author:     Martin Dočekal
"""
import unittest
import torch
from windpytorchutils.general import batch_tril_set, batch_triu_set, span_mask, proliferate


class TestTorchUtils(unittest.TestCase):
    """
    Unit test class for some of the torch utils.
    """

    def setUp(self) -> None:
        self.batch = torch.tensor([
            [
                [1.0, 2.0, 3.0],
                [1.0, 2.0, 3.0],
                [1.0, 2.0, 3.0]
            ],
            [
                [10, 11, 12],
                [13, 14, 15],
                [16, 17, 18],
            ]
        ])
        self.batchClone = self.batch.clone()

        self.batchRectangleShapeA = torch.tensor([
            [
                [1.0, 2.0, 3.0],
                [1.0, 2.0, 3.0]
            ],
            [
                [10, 11, 12],
                [13, 14, 15]
            ]
        ])
        self.batchRectangleShapeAClone = self.batchRectangleShapeA.clone()

        self.batchRectangleShapeB = torch.tensor([
            [
                [1.0, 2.0],
                [1.0, 2.0],
                [1.0, 2.0]
            ],
            [
                [10, 11],
                [13, 14],
                [16, 17],
            ]
        ])
        self.batchRectangleShapeBClone = self.batchRectangleShapeB.clone()

        self.trilRes = torch.tensor([
            [
                [0.0, 2.0, 3.0],
                [0.0, 0.0, 3.0],
                [0.0, 0.0, 0.0]
            ],
            [
                [0, 11, 12],
                [0, 0, 15],
                [0, 0, 0],
            ]
        ])
        self.trilResRecShapeA = torch.tensor([
            [
                [0.0, 2.0, 3.0],
                [0.0, 0.0, 3.0]
            ],
            [
                [0, 11, 12],
                [0, 0, 15]
            ]
        ])

        self.trilResRecShapeB = torch.tensor([
            [
                [0.0, 2.0],
                [0.0, 0.0],
                [0.0, 0.0]
            ],
            [
                [0, 11],
                [0, 0],
                [0, 0],
            ]
        ])

        self.trilWithoutDiagonalRes = torch.tensor([
            [
                [1.0, 2.0, 3.0],
                [0.0, 2.0, 3.0],
                [0.0, 0.0, 3.0]
            ],
            [
                [10, 11, 12],
                [0, 14, 15],
                [0, 0, 18],
            ]
        ])
        self.trilWithoutDiagonalResRecShapeA = torch.tensor([
            [
                [1.0, 2.0, 3.0],
                [0.0, 2.0, 3.0]
            ],
            [
                [10, 11, 12],
                [0, 14, 15]
            ]
        ])

        self.trilWithoutDiagonalResRecShapeB = torch.tensor([
            [
                [1.0, 2.0],
                [0.0, 2.0],
                [0.0, 0.0]
            ],
            [
                [10, 11],
                [0, 14],
                [0, 0],
            ]
        ])

        self.triuRes = torch.tensor([
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 2.0, 0.0]
            ],
            [
                [0, 0, 0],
                [13, 0, 0],
                [16, 17, 0],
            ]
        ])

        self.triuResRecShapeA = torch.tensor([
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0]
            ],
            [
                [0, 0, 0],
                [13, 0, 0]
            ]
        ])

        self.triuResRecShapeB = torch.tensor([
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [1.0, 2.0]
            ],
            [
                [0, 0],
                [13, 0],
                [16, 17],
            ]
        ])

        self.triuWithoutDiagonalRes = torch.tensor([
            [
                [1.0, 0.0, 0.0],
                [1.0, 2.0, 0.0],
                [1.0, 2.0, 3.0]
            ],
            [
                [10, 0, 0],
                [13, 14, 0],
                [16, 17, 18],
            ]
        ])

        self.triuWithoutDiagonalResRecShapeA = torch.tensor([
            [
                [1.0, 0.0, 0.0],
                [1.0, 2.0, 0.0]
            ],
            [
                [10, 0, 0],
                [13, 14, 0]
            ]
        ])

        self.triuWithoutDiagonalResRecShapeB = torch.tensor([
            [
                [1.0, 0.0],
                [1.0, 2.0],
                [1.0, 2.0]
            ],
            [
                [10, 0],
                [13, 14],
                [16, 17],
            ]
        ])

    def test_batch_tril_set(self):
        """
        Unit test for tril set util. This util should set lower triangular to given value
        """

        self.assertTrue(torch.equal(batch_tril_set(self.batch, 0.0), self.trilRes),
                        msg="Difference:\n{}".format(self.trilRes - batch_tril_set(self.batch, 0.0)))
        self.assertTrue(torch.equal(batch_tril_set(self.batchRectangleShapeA, 0.0), self.trilResRecShapeA),
                        msg="Difference:\n{}".format(
                            self.trilResRecShapeA - batch_tril_set(self.batchRectangleShapeA, 0.0)))
        self.assertTrue(torch.equal(batch_tril_set(self.batchRectangleShapeB, 0.0), self.trilResRecShapeB),
                        msg="Difference:\n{}".format(
                            self.trilResRecShapeB - batch_tril_set(self.batchRectangleShapeB, 0.0)))

        # check that original tensors don't changed
        self.assertTrue(torch.equal(self.batch, self.batchClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeA, self.batchRectangleShapeAClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeB, self.batchRectangleShapeBClone))

    def test_batch_tril_set_in_place(self):
        """
        Unit test for tril set util working in place. This util should set lower triangular to given value
        """

        batch = self.batch.clone()
        shapeA = self.batchRectangleShapeA.clone()
        shapeB = self.batchRectangleShapeB.clone()

        self.assertTrue(torch.equal(batch_tril_set(batch, 0.0, True, True), self.trilRes),
                        msg="Difference:\n{}".format(self.trilRes - batch_tril_set(batch, 0.0, True, True)))
        self.assertTrue(torch.equal(batch_tril_set(shapeA, 0.0, True, True), self.trilResRecShapeA),
                        msg="Difference:\n{}".format(self.trilResRecShapeA - batch_tril_set(shapeA, 0.0, True, True)))
        self.assertTrue(torch.equal(batch_tril_set(shapeB, 0.0, True, True), self.trilResRecShapeB),
                        msg="Difference:\n{}".format(self.trilResRecShapeB - batch_tril_set(shapeB, 0.0, True, True)))

        self.assertTrue(torch.equal(batch, self.trilRes),
                        msg="Difference:\n{}".format(self.trilRes - batch))
        self.assertTrue(torch.equal(shapeA, self.trilResRecShapeA),
                        msg="Difference:\n{}".format(self.trilResRecShapeA - shapeA))
        self.assertTrue(torch.equal(shapeB, self.trilResRecShapeB),
                        msg="Difference:\n{}".format(self.trilResRecShapeB - shapeB))

    def test_batch_tril_set_without_diagonal(self):
        """
        Unit test for tril set util. This util should set lower triangular to given value, this
        test tests setting whole lower triangular without the diagonal elements.
        """

        self.assertTrue(torch.equal(batch_tril_set(self.batch, 0.0, False), self.trilWithoutDiagonalRes),
                        msg="Difference:\n{}".format(
                            self.trilWithoutDiagonalRes - batch_tril_set(self.batch, 0.0, False)))
        self.assertTrue(
            torch.equal(batch_tril_set(self.batchRectangleShapeA, 0.0, False), self.trilWithoutDiagonalResRecShapeA),
            msg="Difference:\n{}".format(
                self.trilWithoutDiagonalResRecShapeA - batch_tril_set(self.batchRectangleShapeA, 0.0, False)))
        self.assertTrue(
            torch.equal(batch_tril_set(self.batchRectangleShapeB, 0.0, False), self.trilWithoutDiagonalResRecShapeB),
            msg="Difference:\n{}".format(
                self.trilWithoutDiagonalResRecShapeB - batch_tril_set(self.batchRectangleShapeB, 0.0, False)))

        # check that original tensors don't changed
        self.assertTrue(torch.equal(self.batch, self.batchClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeA, self.batchRectangleShapeAClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeB, self.batchRectangleShapeBClone))

    def test_batch_tril_set_without_diagonal_in_place(self):
        """
        Unit test for tril set util working in place. This util should set lower triangular to given value, this
        test tests setting whole lower triangular without the diagonal elements.
        """

        batch = self.batch.clone()
        shapeA = self.batchRectangleShapeA.clone()
        shapeB = self.batchRectangleShapeB.clone()

        self.assertTrue(torch.equal(batch_tril_set(batch, 0.0, False, True), self.trilWithoutDiagonalRes),
                        msg="Difference:\n{}".format(
                            self.trilWithoutDiagonalRes - batch_tril_set(batch, 0.0, False, True)))
        self.assertTrue(torch.equal(batch_tril_set(shapeA, 0.0, False, True), self.trilWithoutDiagonalResRecShapeA),
                        msg="Difference:\n{}".format(
                            self.trilWithoutDiagonalResRecShapeA - batch_tril_set(shapeA, 0.0, False, True)))
        self.assertTrue(torch.equal(batch_tril_set(shapeB, 0.0, False, True), self.trilWithoutDiagonalResRecShapeB),
                        msg="Difference:\n{}".format(
                            self.trilWithoutDiagonalResRecShapeB - batch_tril_set(shapeB, 0.0, False, True)))

        self.assertTrue(torch.equal(batch, self.trilWithoutDiagonalRes),
                        msg="Difference:\n{}".format(self.trilWithoutDiagonalRes - batch))
        self.assertTrue(torch.equal(shapeA, self.trilWithoutDiagonalResRecShapeA),
                        msg="Difference:\n{}".format(self.trilWithoutDiagonalResRecShapeA - shapeA))
        self.assertTrue(torch.equal(shapeB, self.trilWithoutDiagonalResRecShapeB),
                        msg="Difference:\n{}".format(self.trilWithoutDiagonalResRecShapeB - shapeB))

    def test_batch_triu_set(self):
        """
        Unit test for triu set util. This util should set upper triangular to given value
        """

        self.assertTrue(torch.equal(batch_triu_set(self.batch, 0.0), self.triuRes),
                        msg="Difference:\n{}".format(self.triuRes - batch_triu_set(self.batch, 0.0)))
        self.assertTrue(torch.equal(batch_triu_set(self.batchRectangleShapeA, 0.0), self.triuResRecShapeA),
                        msg="Difference:\n{}".format(
                            self.triuResRecShapeA - batch_triu_set(self.batchRectangleShapeA, 0.0)))
        self.assertTrue(torch.equal(batch_triu_set(self.batchRectangleShapeB, 0.0), self.triuResRecShapeB),
                        msg="Difference:\n{}".format(
                            self.triuResRecShapeB - batch_triu_set(self.batchRectangleShapeB, 0.0)))

        # check that original tensors don't changed
        self.assertTrue(torch.equal(self.batch, self.batchClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeA, self.batchRectangleShapeAClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeB, self.batchRectangleShapeBClone))

    def test_batch_triu_set_in_place(self):
        """
        Unit test for triu set util working in place. This util should set upper triangular to given value
        """

        batch = self.batch.clone()
        shapeA = self.batchRectangleShapeA.clone()
        shapeB = self.batchRectangleShapeB.clone()

        self.assertTrue(torch.equal(batch_triu_set(batch, 0.0, True, True), self.triuRes),
                        msg="Difference:\n{}".format(self.triuRes - batch_triu_set(batch, 0.0, True, True)))
        self.assertTrue(torch.equal(batch_triu_set(shapeA, 0.0, True, True), self.triuResRecShapeA),
                        msg="Difference:\n{}".format(
                            self.triuResRecShapeA - batch_triu_set(shapeA, 0.0, True, True)))
        self.assertTrue(torch.equal(batch_triu_set(shapeB, 0.0, True, True), self.triuResRecShapeB),
                        msg="Difference:\n{}".format(
                            self.triuResRecShapeB - batch_triu_set(shapeB, 0.0, True, True)))

        self.assertTrue(torch.equal(batch, self.triuRes), msg="Difference:\n{}".format(self.triuRes - batch))
        self.assertTrue(torch.equal(shapeA, self.triuResRecShapeA),
                        msg="Difference:\n{}".format(self.triuResRecShapeA - shapeA))
        self.assertTrue(torch.equal(shapeB, self.triuResRecShapeB),
                        msg="Difference:\n{}".format(self.triuResRecShapeB - shapeB))

    def test_batch_triu_set_without_diagonal(self):
        """
        Unit test for triu set util. This util should set upper triangular to given value, this
        test tests setting whole upper triangular without the diagonal elements.
        """

        self.assertTrue(torch.equal(batch_triu_set(self.batch, 0.0, False), self.triuWithoutDiagonalRes),
                        msg="Difference:\n{}".format(
                            self.triuWithoutDiagonalRes - batch_triu_set(self.batch, 0.0, False)))
        self.assertTrue(
            torch.equal(batch_triu_set(self.batchRectangleShapeA, 0.0, False), self.triuWithoutDiagonalResRecShapeA),
            msg="Difference:\n{}".format(
                self.triuWithoutDiagonalResRecShapeA - batch_triu_set(self.batchRectangleShapeA, 0.0, False)))
        self.assertTrue(
            torch.equal(batch_triu_set(self.batchRectangleShapeB, 0.0, False), self.triuWithoutDiagonalResRecShapeB),
            msg="Difference:\n{}".format(
                self.triuWithoutDiagonalResRecShapeB - batch_triu_set(self.batchRectangleShapeB, 0.0, False)))

        # check that original tensors don't changed
        self.assertTrue(torch.equal(self.batch, self.batchClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeA, self.batchRectangleShapeAClone))
        self.assertTrue(torch.equal(self.batchRectangleShapeB, self.batchRectangleShapeBClone))

    def test_batch_triu_set_without_diagonal_in_place(self):
        """
        Unit test for triu set util working in place. This util should set upper triangular to given value, this
        test tests setting whole upper triangular without the diagonal elements.
        """

        batch = self.batch.clone()
        shapeA = self.batchRectangleShapeA.clone()
        shapeB = self.batchRectangleShapeB.clone()

        self.assertTrue(torch.equal(batch_triu_set(batch, 0.0, False, True), self.triuWithoutDiagonalRes),
                        msg="Difference:\n{}".format(
                            self.triuWithoutDiagonalRes - batch_triu_set(batch, 0.0, False, True)))
        self.assertTrue(torch.equal(batch_triu_set(shapeA, 0.0, False, True), self.triuWithoutDiagonalResRecShapeA),
                        msg="Difference:\n{}".format(
                            self.triuWithoutDiagonalResRecShapeA - batch_triu_set(shapeA, 0.0, False, True)))
        self.assertTrue(torch.equal(batch_triu_set(shapeB, 0.0, False, True), self.triuWithoutDiagonalResRecShapeB),
                        msg="Difference:\n{}".format(
                            self.triuWithoutDiagonalResRecShapeB - batch_triu_set(shapeB, 0.0, False, True)))

        self.assertTrue(torch.equal(batch, self.triuWithoutDiagonalRes),
                        msg="Difference:\n{}".format(self.triuWithoutDiagonalRes - batch))
        self.assertTrue(torch.equal(shapeA, self.triuWithoutDiagonalResRecShapeA),
                        msg="Difference:\n{}".format(self.triuWithoutDiagonalResRecShapeA - shapeA))
        self.assertTrue(torch.equal(shapeB, self.triuWithoutDiagonalResRecShapeB),
                        msg="Difference:\n{}".format(self.triuWithoutDiagonalResRecShapeB - shapeB))

    def test_span_mask(self):
        """
        Unit test of span mask util.
        """
        res = span_mask(4, 3)
        self.assertTrue(
            torch.equal(res, torch.tensor([[0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [1, 3], [2, 2], [2, 3], [3, 3]])),
            msg=str(res))

        res = span_mask(3, 1)
        self.assertTrue(
            torch.equal(res, torch.tensor([[0, 0], [1, 1], [2, 2]])),
            msg=str(res))

        res = span_mask(3, 4)
        self.assertTrue(
            torch.equal(res, torch.tensor([[0, 0], [0, 1], [0, 2], [1, 1], [1, 2], [2, 2]])),
            msg=str(res))

        with self.assertRaises(AssertionError):
            span_mask(0, 1)
        with self.assertRaises(AssertionError):
            span_mask(1, 0)
        with self.assertRaises(AssertionError):
            span_mask(0, 0)


class TestProliferate(unittest.TestCase):
    """
    Test of the proliferate method.
    """

    def test_proliferate(self):
        """
        Base unit test of the proliferate
        """

        self.assertTrue(torch.equal(
            proliferate(torch.tensor([[1, 0], [0, 1]]), 1),
            torch.tensor([[1, 0], [0, 1]])
        ))

        with self.assertRaises(AssertionError):
            self.assertTrue(torch.equal(
                proliferate(torch.tensor([[1, 0], [0, 1]]), 0),
                torch.tensor([], dtype=torch.long)
            ))

        with self.assertRaises(AssertionError):
            proliferate(torch.tensor([[1, 0], [0, 1]]), -1)

        self.assertTrue(torch.equal(
            proliferate(torch.tensor([[1, 0], [0, 1]]), 4),
            torch.tensor([[1, 0],
                            [1, 0],
                            [1, 0],
                            [1, 0],
                            [0, 1],
                            [0, 1],
                            [0, 1],
                            [0, 1]])
        ))

        self.assertTrue(torch.equal(
            proliferate(torch.tensor([[1, 3], [0, 0], [0, 1]]), 3),
            torch.tensor([[1, 3],
                          [1, 3],
                          [1, 3],
                          [0, 0],
                          [0, 0],
                          [0, 0],
                          [0, 1],
                          [0, 1],
                          [0, 1]])
        ))

    def test_proliferate_multi_dim(self):
        """
        Tests proliferate on multi dim elements.
        """

        self.assertTrue(torch.equal(
            proliferate(torch.tensor([[[1, 0], [2, 0]], [[0, 1], [1, 1]]]), 4),
            torch.tensor(
                [
                    [[1, 0], [2, 0]],
                    [[1, 0], [2, 0]],
                    [[1, 0], [2, 0]],
                    [[1, 0], [2, 0]],
                    [[0, 1], [1, 1]],
                    [[0, 1], [1, 1]],
                    [[0, 1], [1, 1]],
                    [[0, 1], [1, 1]]
                ]
            ))
        )

    def test_proliferate_single(self):
        """
        Tests proliferate on elements that are no tensors but simple units.
        """

        self.assertTrue(torch.equal(
            proliferate(torch.tensor([1, 0, 3]), 3),
            torch.tensor(
                [
                    1, 1, 1, 0, 0, 0, 3, 3, 3
                ]
            ))
        )


if __name__ == '__main__':
    unittest.main()
