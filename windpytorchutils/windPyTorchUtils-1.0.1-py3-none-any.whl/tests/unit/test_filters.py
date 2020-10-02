# -*- coding: UTF-8 -*-
""""
Created on 15.05.20

:author:     Martin Dočekal
"""
import unittest
import torch
from windpytorchutils.filters import GrubbssFilter


class TestGrubbssFilter(unittest.TestCase):
    """
    Unit test class for some of the GrubbssFilter.
    """

    def setUp(self) -> None:
        self.noOutliers = torch.tensor([1.0, 2.0, 3.0, 2.5, 1.5, 3.0, 4.0, 1.0, 3.0])
        self.noOutliersBig = torch.full((130816,), 32.0024)

        self.outliersInMaxWatters = torch.tensor(
            [1.0, 2.0, 3.0, 2.5, 1.5, 3.0, 4.0, 1.0, 3.0, 1.0, 2.0, 3.0, 2.5, 1.5, 3.0, 4.0, 1.0, 3.0, 99.0, 100.0])
        self.outliersInMaxWattersOutliers = {99.0, 100.0}
        self.outliersInMaxWattersNoOutliers = set(self.outliersInMaxWatters.tolist()) - self.outliersInMaxWattersOutliers
        self.outliersInMaxWattersOutliersArgs = {18, 19}
        self.outliersInMaxWattersNoOutliersArgs = {x for x in range(self.outliersInMaxWatters.shape[0]-2)}

        self.outliersInMaxWattersBig = torch.cat([torch.full((130816,), 1.0), torch.tensor([100.0])])
        self.outliersInMaxWattersBigOutliers = {100.0}
        self.outliersInMaxWattersBigNoOutliers = set(self.outliersInMaxWattersBig.tolist()) - self.outliersInMaxWattersBigOutliers
        self.outliersInMaxWattersBigOutliersArgs = {130816}
        self.outliersInMaxWattersBigNoOutliersArgs = {x for x in range(0, self.outliersInMaxWattersBig.shape[0]-1)}

        self.outliersInMinWatters005 = torch.tensor(
            [97, 103.0, 102.5, 101.5, 103.0, 104.0, 101.0, 103.0, 101.0, 102.0, 103.0, 102.5, 101.5,
             103.0, 104.0, 101.0, 103.0, 99.0, 100.0])
        self.outliersInMinWattersOutliers005 = {97}
        self.outliersInMinWattersNoOutliers005 = set(self.outliersInMinWatters005.tolist()) - self.outliersInMinWattersOutliers005
        self.outliersInMinWattersOutliersArgs005 = {0}
        self.outliersInMinWattersNoOutliersArgs005 = {x for x in range(1, self.outliersInMinWatters005.shape[0])}

        self.outliersInBothWatters = torch.tensor(
            [-100.0, 1.0, 2.0, 3.0, 2.5, 1.5, 3.0, 4.0, 1.0, 3.0, 1.0, 2.0, 3.0, 2.5, 1.5, 3.0, 4.0, 1.0, 3.0, 100.0])
        self.outliersInBothWattersMinOutliers = {-100.0}
        self.outliersInBothWattersMinNoOutliers = set(self.outliersInBothWatters.tolist()) - self.outliersInBothWattersMinOutliers
        self.outliersInBothWattersMaxOutliers = {100.0}
        self.outliersInBothWattersMaxNoOutliers = set(self.outliersInBothWatters.tolist()) - self.outliersInBothWattersMaxOutliers
        self.outliersInBothWattersMinOutliersArgs = {0}
        self.outliersInBothWattersMinNoOutliersArgs = {x for x in range(1, self.outliersInBothWatters.shape[0])}
        self.outliersInBothWattersMaxOutliersArgs = {19}
        self.outliersInBothWattersMaxNoOutliersArgs = {x for x in range(0, self.outliersInBothWatters.shape[0]-1)}

        self.outliersInBothWattersBig = torch.cat(
            [torch.tensor([-100.0]), torch.full((130816,), 1.0), torch.tensor([100.0])])
        self.outliersInBothWattersBigMinOutliers = {-100.0}
        self.outliersInBothWattersBigMinNoOutliers = set(
            self.outliersInBothWattersBig.tolist()) - self.outliersInBothWattersBigMinOutliers
        self.outliersInBothWattersBigMaxOutliers = {100.0}
        self.outliersInBothWattersBigMaxNoOutliers = set(
            self.outliersInBothWattersBig.tolist()) - self.outliersInBothWattersBigMaxOutliers
        self.outliersInBothWattersBigMinOutliersArgs = {0}
        self.outliersInBothWattersBigMinNoOutliersArgs = {x for x in range(1, self.outliersInBothWattersBig.shape[0])}
        self.outliersInBothWattersBigMaxOutliersArgs = {130817}
        self.outliersInBothWattersBigMaxNoOutliersArgs = {x for x in range(0, self.outliersInBothWattersBig.shape[0] - 1)}

        self.filter = GrubbssFilter()  # default
        self.filter001Min = GrubbssFilter(alpha=0.01, outliers=True, sort=True, descending=False)
        self.filterMin = GrubbssFilter(outliers=True, sort=True, descending=False)

        self.filterNoOutliers = GrubbssFilter(outliers=False, sort=True, descending=True)
        self.filterNoOutliersMin = GrubbssFilter(outliers=False, sort=True, descending=False)

        self.filterPreSorted = GrubbssFilter(sort=False)
        self.filterPreSortedNoOutliers = GrubbssFilter(outliers=False, sort=False)

    def test_basic_call(self):
        # no outliers
        self.assertEqual(self.filter(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filter(self.noOutliersBig).shape[0], 0)
        self.assertEqual(self.filter001Min(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filter001Min(self.noOutliersBig).shape[0], 0)
        self.assertEqual(self.filterMin(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filterMin(self.noOutliersBig).shape[0], 0)
        self.assertEqual(set(self.filterNoOutliers(self.noOutliers).tolist()), set(self.noOutliers.tolist()))
        self.assertEqual(set(self.filterNoOutliers(self.noOutliersBig).tolist()), set(self.noOutliersBig.tolist()))
        self.assertEqual(set(self.filterNoOutliersMin(self.noOutliers).tolist()), set(self.noOutliers.tolist()))
        self.assertEqual(set(self.filterNoOutliersMin(self.noOutliersBig).tolist()), set(self.noOutliersBig.tolist()))
        self.assertEqual(self.filterPreSorted(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filterPreSorted(self.noOutliersBig).shape[0], 0)
        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.noOutliers, descending=True)[0]).tolist()), set(self.noOutliers.tolist()))
        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.noOutliersBig, descending=True)[0]).tolist()), set(self.noOutliersBig.tolist()))

        # outliers in max watters
        self.assertEqual(set(self.filter(self.outliersInMaxWatters).tolist()), self.outliersInMaxWattersOutliers)
        self.assertEqual(set(self.filter(self.outliersInMaxWattersBig).tolist()), self.outliersInMaxWattersBigOutliers)

        self.assertEqual(self.filter001Min(self.outliersInMaxWatters).shape[0], 0)
        self.assertEqual(self.filter001Min(self.outliersInMaxWattersBig).shape[0], 0)

        self.assertEqual(self.filterMin(self.outliersInMaxWatters).shape[0], 0)
        self.assertEqual(self.filterMin(self.outliersInMaxWattersBig).shape[0], 0)

        self.assertEqual(set(self.filterNoOutliers(self.outliersInMaxWatters).tolist()), self.outliersInMaxWattersNoOutliers)
        self.assertEqual(set(self.filterNoOutliers(self.outliersInMaxWattersBig).tolist()), self.outliersInMaxWattersBigNoOutliers)

        self.assertEqual(set(self.filterNoOutliersMin(self.outliersInMaxWatters).tolist()), set(self.outliersInMaxWatters.tolist()))
        self.assertEqual(set(self.filterNoOutliersMin(self.outliersInMaxWattersBig).tolist()), set(self.outliersInMaxWattersBig.tolist()))

        self.assertEqual(set(self.filterPreSorted(torch.sort(self.outliersInMaxWatters, descending=True)[0]).tolist()), self.outliersInMaxWattersOutliers)
        self.assertEqual(set(self.filterPreSorted(torch.sort(self.outliersInMaxWattersBig, descending=True)[0]).tolist()), self.outliersInMaxWattersBigOutliers)

        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.outliersInMaxWatters, descending=True)[0]).tolist()),
                         self.outliersInMaxWattersNoOutliers)
        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.outliersInMaxWattersBig, descending=True)[0]).tolist()),
                         self.outliersInMaxWattersBigNoOutliers)

        # outliers in min watters alpha = 0.05
        self.assertEqual(self.filter(self.outliersInMinWatters005).shape[0], 0)

        self.assertEqual(self.filter001Min(self.outliersInMinWatters005).shape[0], 0)

        self.assertEqual(set(self.filterMin(self.outliersInMinWatters005).tolist()), self.outliersInMinWattersOutliers005)

        self.assertEqual(set(self.filterNoOutliers(self.outliersInMinWatters005).tolist()), set(self.outliersInMinWatters005.tolist()))

        self.assertEqual(set(self.filterNoOutliersMin(self.outliersInMinWatters005).tolist()), self.outliersInMinWattersNoOutliers005)

        self.assertEqual(self.filterPreSorted(torch.sort(self.outliersInMinWatters005, descending=True)[0]).shape[0], 0)

        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.outliersInMinWatters005, descending=True)[0]).tolist()), set(self.outliersInMinWatters005.tolist()))

        # outliers on both sides
        self.assertEqual(set(self.filter(self.outliersInBothWatters).tolist()), self.outliersInBothWattersMaxOutliers)
        self.assertEqual(set(self.filter(self.outliersInBothWattersBig).tolist()), self.outliersInBothWattersBigMaxOutliers)

        self.assertEqual(set(self.filter001Min(self.outliersInBothWatters).tolist()), self.outliersInBothWattersMinOutliers)
        self.assertEqual(set(self.filter001Min(self.outliersInBothWattersBig).tolist()), self.outliersInBothWattersBigMinOutliers)

        self.assertEqual(set(self.filterMin(self.outliersInBothWatters).tolist()), self.outliersInBothWattersMinOutliers)
        self.assertEqual(set(self.filterMin(self.outliersInBothWattersBig).tolist()), self.outliersInBothWattersBigMinOutliers)

        self.assertEqual(set(self.filterNoOutliers(self.outliersInBothWatters).tolist()), self.outliersInBothWattersMaxNoOutliers)
        self.assertEqual(set(self.filterNoOutliers(self.outliersInBothWattersBig).tolist()), self.outliersInBothWattersBigMaxNoOutliers)

        self.assertEqual(set(self.filterNoOutliersMin(self.outliersInBothWatters).tolist()), self.outliersInBothWattersMinNoOutliers)
        self.assertEqual(set(self.filterNoOutliersMin(self.outliersInBothWattersBig).tolist()), self.outliersInBothWattersBigMinNoOutliers)

        self.assertEqual(set(self.filterPreSorted(torch.sort(self.outliersInBothWatters, descending=True)[0]).tolist()), self.outliersInBothWattersMaxOutliers)
        self.assertEqual(set(self.filterPreSorted(torch.sort(self.outliersInBothWattersBig, descending=True)[0]).tolist()), self.outliersInBothWattersBigMaxOutliers)

        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.outliersInBothWatters, descending=True)[0]).tolist()), self.outliersInBothWattersMaxNoOutliers)
        self.assertEqual(set(self.filterPreSortedNoOutliers(torch.sort(self.outliersInBothWattersBig, descending=True)[0]).tolist()), self.outliersInBothWattersBigMaxNoOutliers)

    def test_arg_sort(self):
        # no outliers
        self.assertEqual(self.filter.argFilter(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filter.argFilter(self.noOutliersBig).shape[0], 0)
        self.assertEqual(self.filter001Min.argFilter(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filter001Min.argFilter(self.noOutliersBig).shape[0], 0)
        self.assertEqual(self.filterMin.argFilter(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filterMin.argFilter(self.noOutliersBig).shape[0], 0)
        self.assertEqual(set(self.filterNoOutliers.argFilter(self.noOutliers).tolist()), set(x for x in range(len(self.noOutliers))))
        self.assertEqual(set(self.filterNoOutliers.argFilter(self.noOutliersBig).tolist()), set(x for x in range(len(self.noOutliersBig))))
        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.noOutliers).tolist()), set(x for x in range(len(self.noOutliers))))
        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.noOutliersBig).tolist()), set(x for x in range(len(self.noOutliersBig))))
        self.assertEqual(self.filterPreSorted.argFilter(self.noOutliers).shape[0], 0)
        self.assertEqual(self.filterPreSorted.argFilter(self.noOutliersBig).shape[0], 0)
        self.assertEqual(set(self.filterPreSortedNoOutliers.argFilter(torch.sort(self.noOutliers, descending=True)[0]).tolist()),
                         set(x for x in range(len(self.noOutliers))))
        self.assertEqual(
            set(self.filterPreSortedNoOutliers.argFilter(torch.sort(self.noOutliersBig, descending=True)[0]).tolist()),
            set(x for x in range(len(self.noOutliersBig))))

        # outliers in max watters
        self.assertEqual(set(self.filter.argFilter(self.outliersInMaxWatters).tolist()), self.outliersInMaxWattersOutliersArgs)
        self.assertEqual(set(self.filter.argFilter(self.outliersInMaxWattersBig).tolist()), self.outliersInMaxWattersBigOutliersArgs)

        self.assertEqual(self.filter001Min.argFilter(self.outliersInMaxWatters).shape[0], 0)
        self.assertEqual(self.filter001Min.argFilter(self.outliersInMaxWattersBig).shape[0], 0)

        self.assertEqual(self.filterMin.argFilter(self.outliersInMaxWatters).shape[0], 0)
        self.assertEqual(self.filterMin.argFilter(self.outliersInMaxWattersBig).shape[0], 0)

        self.assertEqual(set(self.filterNoOutliers.argFilter(self.outliersInMaxWatters).tolist()),
                         self.outliersInMaxWattersNoOutliersArgs)
        self.assertEqual(set(self.filterNoOutliers.argFilter(self.outliersInMaxWattersBig).tolist()),
                         self.outliersInMaxWattersBigNoOutliersArgs)

        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.outliersInMaxWatters).tolist()),
                         set(x for x in range(len(self.outliersInMaxWatters))))
        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.outliersInMaxWattersBig).tolist()),
                         set(x for x in range(len(self.outliersInMaxWattersBig))))

        vals, ind = torch.sort(self.outliersInMaxWatters, descending=True)
        self.assertEqual(set(ind[self.filterPreSorted.argFilter(vals)].tolist()),
                         self.outliersInMaxWattersOutliersArgs)

        vals, ind = torch.sort(self.outliersInMaxWattersBig, descending=True)
        self.assertEqual(
            set(ind[self.filterPreSorted.argFilter(vals)].tolist()),
            self.outliersInMaxWattersBigOutliersArgs)

        vals, ind = torch.sort(self.outliersInMaxWatters, descending=True)
        self.assertEqual(
            set(ind[self.filterPreSortedNoOutliers.argFilter(vals)].tolist()),
            self.outliersInMaxWattersNoOutliersArgs)

        vals, ind = torch.sort(self.outliersInMaxWattersBig, descending=True)
        self.assertEqual(
            set(ind[self.filterPreSortedNoOutliers.argFilter(vals)].tolist()),
            self.outliersInMaxWattersBigNoOutliersArgs)

        # outliers in min watters alpha = 0.05
        self.assertEqual(self.filter.argFilter(self.outliersInMinWatters005).shape[0], 0)

        self.assertEqual(self.filter001Min.argFilter(self.outliersInMinWatters005).shape[0], 0)

        self.assertEqual(set(self.filterMin.argFilter(self.outliersInMinWatters005).tolist()),
                         self.outliersInMinWattersOutliersArgs005)

        self.assertEqual(set(self.filterNoOutliers.argFilter(self.outliersInMinWatters005).tolist()),
                         set(x for x in range(len(self.outliersInMinWatters005))))

        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.outliersInMinWatters005).tolist()),
                         self.outliersInMinWattersNoOutliersArgs005)

        self.assertEqual(self.filterPreSorted.argFilter(torch.sort(self.outliersInMinWatters005, descending=True)[0]).shape[0], 0)

        vals, ind = torch.sort(self.outliersInMinWatters005, descending=True)
        self.assertEqual(
            set(ind[self.filterPreSortedNoOutliers.argFilter(vals)].tolist()),
            set(x for x in range(len(self.outliersInMinWatters005))))

        # outliers on both sides
        self.assertEqual(set(self.filter.argFilter(self.outliersInBothWatters).tolist()), self.outliersInBothWattersMaxOutliersArgs)
        self.assertEqual(set(self.filter.argFilter(self.outliersInBothWattersBig).tolist()),
                         self.outliersInBothWattersBigMaxOutliersArgs)

        self.assertEqual(set(self.filter001Min.argFilter(self.outliersInBothWatters).tolist()),
                         self.outliersInBothWattersMinOutliersArgs)
        self.assertEqual(set(self.filter001Min.argFilter(self.outliersInBothWattersBig).tolist()),
                         self.outliersInBothWattersBigMinOutliersArgs)

        self.assertEqual(set(self.filterMin.argFilter(self.outliersInBothWatters).tolist()),
                         self.outliersInBothWattersMinOutliersArgs)
        self.assertEqual(set(self.filterMin.argFilter(self.outliersInBothWattersBig).tolist()),
                         self.outliersInBothWattersBigMinOutliersArgs)

        self.assertEqual(set(self.filterNoOutliers.argFilter(self.outliersInBothWatters).tolist()),
                         self.outliersInBothWattersMaxNoOutliersArgs)
        self.assertEqual(set(self.filterNoOutliers.argFilter(self.outliersInBothWattersBig).tolist()),
                         self.outliersInBothWattersBigMaxNoOutliersArgs)

        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.outliersInBothWatters).tolist()),
                         self.outliersInBothWattersMinNoOutliersArgs)
        self.assertEqual(set(self.filterNoOutliersMin.argFilter(self.outliersInBothWattersBig).tolist()),
                         self.outliersInBothWattersBigMinNoOutliersArgs)

        vals, ind = torch.sort(self.outliersInBothWatters, descending=True)
        self.assertEqual(set(ind[self.filterPreSorted.argFilter(vals)].tolist()),
                         self.outliersInBothWattersMaxOutliersArgs)

        vals, ind = torch.sort(self.outliersInBothWattersBig, descending=True)
        self.assertEqual(set(ind[self.filterPreSorted.argFilter(vals)].tolist()),
                         self.outliersInBothWattersBigMaxOutliersArgs)

        vals, ind = torch.sort(self.outliersInBothWatters, descending=True)
        self.assertEqual(
            set(ind[self.filterPreSortedNoOutliers.argFilter(vals)].tolist()),
            self.outliersInBothWattersMaxNoOutliersArgs)

        vals, ind = torch.sort(self.outliersInBothWattersBig, descending=True)
        self.assertEqual(
            set(ind[self.filterPreSortedNoOutliers.argFilter(vals)].tolist()),
            self.outliersInBothWattersBigMaxNoOutliersArgs)


if __name__ == '__main__':
    unittest.main()
