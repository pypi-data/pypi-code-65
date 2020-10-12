import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ddconst.plotting.colors import blue, red, blue_light
from sklearn.base import clone
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score
from sklearn.model_selection import BaseCrossValidator

_dpi = 120
_lim = (-.05, 1.05)


def draw_roc_prc_cv(estimator, X, y, cv, groups=None,
                    roc_ax=None, prc_ax=None,
                    roc_auc_average='weighted', ap_average='weighted'):
    """Run k-fold cross-validation and draw the receiver operating characteristic (ROC)
    as well as the precision-recall (PR) curves for each fold. Mean ROC and PR curves and area +-1 std. dev. are
    plotted as well.

        Parameters
        ----------
        estimator : {sklearn estimator}
            The estimator with specific hyperparameters

        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples and n_features is the number of features

        y : array-like, shape (n_samples,)
            Target values - class labels

        cv : cross-validation generator
            Generator of indices for splitting the dataset into train/test set

        groups : array-like, with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into train/test set.

        roc_ax : matplotlib Axes, default None
            Axes to draw the ROC figure on

        prc_ax : matplotlib Axes, default None
            Axes to draw the PR figure on

        roc_auc_average : {None, 'weighted', 'macro', 'micro', 'samples'}, optional, default 'weighted'
            The type of averaging performed on the data when calculating AUROC score

        ap_average : {None, 'weighted', 'macro', 'micro', 'samples'}, optional, default 'weighted'
            The type of averaging performed on the data when calculating AUPRC score

        Returns
        -------
        self : None
    """
    _check_input(estimator, cv)

    if not roc_ax or not prc_ax:
        fig, (roc_ax, prc_ac) = plt.subplots(1, 2, figsize=(6, 4), dpi=_dpi)

    fprs, tprs = [], []
    precs, recls = [], []
    aucs, aps = [], []

    for train_idxs, test_idxs in cv.split(X, y, groups):
        X_train = X.iloc[train_idxs] if isinstance(X, pd.DataFrame) else X[train_idxs]
        X_test = X.iloc[test_idxs] if isinstance(X, pd.DataFrame) else X[test_idxs]
        le = clone(estimator).fit(X_train, y[train_idxs])
        y_proba = le.predict_proba(X_test)

        # ROC
        fpr, tpr, _ = roc_curve(y_true=y[test_idxs], y_score=y_proba[:, 1])
        auc = roc_auc_score(y_true=y[test_idxs], y_score=y_proba[:, 1], average=roc_auc_average)
        aucs.append(auc)
        fprs.append(fpr)
        tprs.append(tpr)

        # PRC
        prec, rec, _ = precision_recall_curve(y_true=y[test_idxs], probas_pred=y_proba[:, 1])
        ap = average_precision_score(y_true=y[test_idxs], y_score=y_proba[:, 1], average=ap_average)
        aps.append(ap)
        precs.append(prec)
        recls.append(rec)

    _draw_roc(fprs, tprs, aucs, roc_ax)
    _draw_prc(precs, recls, aps, prc_ax)


def draw_roc_cv(estimator, X, y, cv, groups=None, roc_auc_average='weighted', ax=None):
    """Run k-fold cross-validation and draw the ROC curves for each fold as well as the mean ROC curve.

        Parameters
        ----------
        estimator : {sklearn estimator}
            The estimator with specific hyperparameters that will be fitted and used for prediction on the test set

        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples
            and n_features is the number of features.

        y : array-like, shape (n_samples,)
            Target values - class labels

        cv : cross-validation generator
            Generator of indices for splitting the dataset into train/test set

        groups : array-like, with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into train/test set.

        roc_auc_average : {None, 'weighted', 'macro', 'micro', 'samples'}, optional, default 'weighted'
            The type of averaging performed on the data when calculating AUROC score

        ax : matplotlib Axes, default None
            Matplotlib

        Returns
        -------
        self : None
        """
    _check_input(estimator, cv)

    if not ax:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=_dpi)

    fprs, tprs, aucs = [], [], []
    for train_idxs, test_idxs in cv.split(X, y, groups):
        X_train = X.iloc[train_idxs] if isinstance(X, pd.DataFrame) else X[train_idxs]
        X_test = X.iloc[test_idxs] if isinstance(X, pd.DataFrame) else X[test_idxs]

        # fit local estimator and predict the probabilities
        y_proba = clone(estimator).fit(X_train, y[train_idxs]).predict_proba(X_test)
        fpr, tpr, _ = roc_curve(y_true=y[test_idxs], y_score=y_proba[:, 1])
        auc = roc_auc_score(y_true=y[test_idxs], y_score=y_proba[:, 1], average=roc_auc_average)
        fprs.append(fpr)
        tprs.append(tpr)
        aucs.append(auc)

    _draw_roc(fprs, tprs, aucs, ax)


def draw_prc_cv(estimator, X, y, cv, groups=None, ap_average='weighted', ax=None):
    """Run k-fold cross-validation and draw the precision-recall curves for each fold as well as the mean
    precision-recall curve.

        Parameters
        ----------
        estimator : {sklearn estimator}
            The estimator with specific hyperparameters that will be fitted and used for prediction on the test set

        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            Training vectors, where n_samples is the number of samples and n_features is the number of features

        y : array-like, shape (n_samples,)
            Target values - class labels

        cv : cross-validation generator
            Generator of indices for splitting the dataset into train/test set

        groups : array-like, with shape (n_samples,), optional
            Group labels for the samples used while splitting the dataset into train/test set.

        ap_average : {None, 'weighted', 'macro', 'micro', 'samples'}, optional, default 'weighted'
            The type of averaging performed on the data when calculating AUPRC score

        ax : matplotlib Axes, default None
            Axes to draw the figure on

        Returns
        -------
        self : None
    """
    _check_input(estimator, cv)

    if not ax:
        fig, ax = plt.subplots(figsize=(6, 4), dpi=_dpi)

    precs, recls, aps = [], [], []
    for train_idxs, test_idxs in cv.split(X, y, groups):
        X_train = X.iloc[train_idxs] if isinstance(X, pd.DataFrame) else X[train_idxs]
        X_test = X.iloc[test_idxs] if isinstance(X, pd.DataFrame) else X[test_idxs]
        y_proba = clone(estimator).fit(X_train, y[train_idxs]).predict_proba(X_test)

        prec, rec, _ = precision_recall_curve(y_true=y[test_idxs], probas_pred=y_proba[:, 1])
        ap = average_precision_score(y_true=y[test_idxs], y_score=y_proba[:, 1], average=ap_average)
        precs.append(prec)
        recls.append(rec)
        aps.append(ap)

    _draw_prc(precs, recls, aps, ax)


def _draw_roc(fprs: list, tprs: list, aucs: list, ax):
    major_loc = mpl.ticker.MultipleLocator(.5)
    minor_loc = mpl.ticker.MultipleLocator(.1)

    std_factor = 1  # color area +- std_factor * std. dev

    # draw the individual curves
    for fpr, tpr in zip(fprs, tprs):
        ax.plot(fpr, tpr, linewidth=.5, c=blue, alpha=.25)

    # draw the worst case
    ax.plot([0, 1], [0, 1], '--', c=red, linewidth=.5)

    # interpolate fpr and tpr values
    i_tprs = []
    mean_fpr = np.linspace(0, 1, num=100)
    for fpr, tpr in zip(fprs, tprs):
        i_tpr = np.interp(mean_fpr, fpr, tpr)
        i_tpr[0] = 0.
        i_tprs.append(i_tpr)

    mean_tpr = np.mean(i_tprs, axis=0)
    std_tpr = np.std(i_tprs, axis=0)
    ax.plot(mean_fpr, mean_tpr,
            c=blue, linewidth=1., label=r'Mean ROC (AUC={:.2f} $\pm{:.2f}$)'.format(np.mean(aucs), np.std(aucs)))
    lower = np.maximum(mean_tpr - (std_factor * std_tpr), 0)
    upper = np.minimum(mean_tpr + (std_factor * std_tpr), 1)
    ax.fill_between(mean_fpr, lower, upper,
                    color=blue_light, linewidth=0, alpha=.25, label=r'$\pm{:d}$ std. dev.'.format(std_factor))

    ax.set(title='Receiver operating characteristic', xlabel='False Positive Rate', ylabel='True Positive Rate',
           aspect='equal', xlim=_lim, ylim=_lim)
    ax.xaxis.set(major_locator=major_loc, minor_locator=minor_loc)
    ax.yaxis.set(major_locator=major_loc, minor_locator=minor_loc)
    ax.legend()


def _draw_prc(precs: list, recls: list, aps: list, ax):
    major_loc = mpl.ticker.MultipleLocator(.5)
    minor_loc = mpl.ticker.MultipleLocator(.1)

    std_factor = 1  # color area +- std_factor * std. dev

    # PRC
    for prec, rec in zip(precs, recls):
        ax.plot(rec, prec, linewidth=.5, c=blue, alpha=.25)

    mean_rec = np.linspace(0, 1, num=100)
    # This is a tricky part, solved by a heuristic
    i_precs = [np.interp(mean_rec, 1 - rec, prec)[::-1] for prec, rec in zip(precs, recls)]

    mean_prec = np.mean(i_precs, axis=0)
    std_prec = np.std(i_precs, axis=0)
    ax.plot(mean_rec, mean_prec,
            c=blue, linewidth=1, label=r'Mean AP={:.2f} $\pm{:.2f}$'.format(np.mean(aps), np.std(aps)))
    lower = np.maximum(mean_prec - (std_factor * std_prec), 0)
    upper = np.minimum(mean_prec + (std_factor * std_prec), 1)
    ax.fill_between(mean_rec, lower, upper,
                    color=blue_light, linewidth=0, alpha=.25, label=r'$\pm{:d}$ std. dev'.format(std_factor))

    ax.set(title='Precision-recall curve', xlabel='Recall', ylabel='Precision',
           aspect='equal', xlim=_lim, ylim=_lim)
    ax.xaxis.set(major_locator=major_loc, minor_locator=minor_loc)
    ax.yaxis.set(major_locator=major_loc, minor_locator=minor_loc)
    ax.legend(loc='lower left')


def _check_input(estimator, cv):
    if not hasattr(estimator, 'fit'):
        raise ValueError("The received estimator of type `{}` does not support `fit` method".format(type(estimator)))
    if not isinstance(cv, BaseCrossValidator):
        raise ValueError("cv must be a cross-validator, got `{}`".format(type(cv)))
