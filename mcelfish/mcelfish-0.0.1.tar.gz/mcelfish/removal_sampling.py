"""Removal sampling.

Maximum Likelihood (ML) estimates for estimating population size (N)
for a constant probability of capture model.
"""

import sys
import statistics
import random

import numpy as np
import pymc3 as pm
import matplotlib.pyplot as plt


def exit_with_usage():
    msg = """Usage:
removal_sampling.py --plot --testcase 3
removal_sampling.py --data 25 10 2 3 0 1 0 0
removal_sampling.py --samples 1000 --data 25 10 2 3 0 1 0 0
removal_sampling.py --tuning 5000 --data 25 10 2 3 0 1 0 0
removal_sampling.py --savefig --data 25 10 2 3 0 1 0 0
removal_sampling.py --beta --data 25 10 2 3 0 1 0 0
"""
    exit(msg)


def _savefig(pfx=""):
    fnameid = random.randint(10 ** 12, 10 ** 15)
    fname = f"{pfx}{fnameid}.svg"
    plt.savefig(fname)
    plt.clf()
    return fname


def _get_testcase(n):
    from .testdata import catches

    return catches[n].data


def run(samples=None, tune=None, data=None, testcase=None):
    if samples is None:
        samples = 5000
    if tune is None:
        tune = 1000
    if data is None and testcase is None:
        raise ValueError("Specify data or testcase")
    if testcase is not None:
        case = _get_testcase(testcase)
    else:
        case = list(data)

    print(f"data    = {case}")
    print(f"samples = {samples}")
    print(f"tunings = {tune}")

    rm_model = pm.Model()

    with rm_model:

        N = pm.DiscreteUniform("N", lower=0, upper=500)
        p = pm.Uniform("p", lower=0, upper=1)

        observations = case
        catch = []
        for idx, c in enumerate(observations):
            q = pm.Binomial(f"q{idx}", N - sum(catch), p, observed=[c])
            catch.append(q)
        trace = pm.sample(draws=samples, tune=tune)
    return rm_model, trace


def summary(model, trace):
    with model:
        sorted_N = sorted(trace["N"])
        len_N = len(trace["N"])

        quantiles = statistics.quantiles(sorted_N)
        quantiles_s = [25, 50, 75]
        print(
            "   ".join(
                [f"{i}% = {round(q, 1)}" for q, i in zip(quantiles, quantiles_s)]
            )
        )

        return pm.summary(trace), sorted_N


def _plot(model, trace, savefig=False):
    with model:

        pm.traceplot(trace, ["N", "p"])
        if savefig:
            return _savefig("smry")
        else:
            plt.show()


def _get_arg(args, arg):
    if arg == "--data" and arg in args:
        idx = args.index(arg)
        return [int(x.rstrip(",").lstrip(",")) for x in args[idx + 1 :]]
    if arg in args:
        return int(args[args.index(arg) + 1])
    return None


def _beta(data, plot=False, savefig=False):
    try:
        from scipy.stats import beta
    except ImportError:
        exit("--beta needs scipy")

    tens = len(data) // 50
    data = data[tens:-tens]

    alpha_, beta_, loc_, scale_ = [round(x, 3) for x in beta.fit(data)]
    print(f"X = Beta(alpha={alpha_}, beta={beta_}, loc={loc_}, scale={scale_})")
    print(f"E[X] = a/(a+b) = {alpha_/(alpha_+beta_)+loc_}")

    if not (plot or savefig):
        return alpha_, beta_, loc_, scale_

    x = np.linspace(
        beta.ppf(0.01, alpha_, beta_, loc_, scale_),
        beta.ppf(0.99, alpha_, beta_, loc_, scale_),
        100,
    )

    plt.plot(
        x,
        beta.pdf(x, alpha_, beta_, loc=loc_, scale=scale_),
        label=f"Beta({alpha_}, {beta_})",
    )
    plt.hist(
        data, alpha=0.75, color="green", bins=min(200, len(set(data))), density=True
    )
    if savefig:
        return (alpha_, beta_, loc_, scale_), _savefig("beta")
    plt.show()
    return alpha_, beta_, loc_, scale_


def main():
    args = sys.argv
    if len(args) == 1:
        exit_with_usage()

    if "--testcase" in args and "--data" in args:
        exit_with_usage()

    testcase = _get_arg(args, "--testcase")
    data = _get_arg(args, "--data")
    samples = _get_arg(args, "--samples")
    tune = _get_arg(args, "--tune")

    model, trace = run(testcase=testcase, samples=samples, tune=tune, data=data)
    smry, sorted_N = summary(model, trace)
    print(smry)
    if "--plot" in args:
        _plot(model, trace)
    elif "--savefig" in args:
        fname = _plot(model, trace, savefig=True)
        print(f"wrote {fname}")

    if "--beta" in args:
        retval = _beta(sorted_N, plot="--plot" in args, savefig="--savefig" in args)
        if len(retval) == 2:
            fname = retval[1]
            retval = retval[0]
            print(f"wrote {fname}")
        print(f"Beta({retval})")


if __name__ == "__main__":
    main()
