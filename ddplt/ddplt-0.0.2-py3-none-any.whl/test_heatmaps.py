import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.svm import SVC

from ddplt.heatmaps import plot_correlation_heatmap, draw_confusion_heatmap
from .test_base import TestBase

# set this to true if you want to see the plots
interactive = False


class TestHeatmaps(TestBase):

    def setUp(self) -> None:
        super(TestHeatmaps, self).setUp()

        # Run classifier, using a model that is regularized way too much (C too low)
        # to see the impact on the results
        self.y_pred = SVC(kernel='linear', C=0.01).fit(self.X_train, self.y_train).predict(self.X_test)

    def test_confusion_heatmap(self):
        """Test correctness of confusion heatmap creation.

        Set `interactive = True` if you want to see the created plot
        """
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))
        ax, cm = draw_confusion_heatmap(self.y_test, self.y_pred, self.class_names, title="The confusion matrix",
                                        normalize=True, ax=ax[0])

        self.assertIsNone(  # return None if the arrays are almost equal, raise AssertionError otherwise
            np.testing.assert_allclose(cm, np.array([[1., 0., 0.], [0., 0.625, 0.375], [0., 0., 1.]])))
        if interactive:
            fig.tight_layout()
            plt.show()

    def test_corr_heatmap(self):
        """Test correctness of correlation heatmap.

        :return:
        """
        df = pd.DataFrame(data=self.X[:30], columns=self.feature_names)
        plot_correlation_heatmap(df)
        # todo - write tests
