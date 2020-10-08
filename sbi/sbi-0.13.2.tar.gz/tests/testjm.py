import torch
from torch import zeros, ones, eye
from torch.distributions import MultivariateNormal

import sbi.utils as utils
from sbi.inference.snpe.snpe_b import SnpeB
from sbi.inference.snpe.snpe_c import SnpeC
from sbi.simulators.linear_gaussian import (
    get_true_posterior_samples_linear_gaussian_mvn_prior,
    get_true_posterior_samples_linear_gaussian_uniform_prior,
    linear_gaussian,
)
from sbi.user_input.user_input_checks import prepare_sbi_problem

# Use cpu by default.
torch.set_default_tensor_type("torch.FloatTensor")


def test_snpe_on_linearGaussian_based_on_mmd(
    num_dim: int, prior_str: str, algorithm_str: str, simulation_batch_size: int,
):
    """Test whether SNPE B/C infer well a simple example with available round truth.
    This test is seeded using the set_seed fixture defined in tests/conftest.py.
    Args:
        set_seed: fixture for manual seeding, see tests/conftest.py
    """

    print("HHHH")
    x_o = zeros(1, num_dim)
    num_samples = 100

    prior = MultivariateNormal(loc=zeros(num_dim), covariance_matrix=eye(num_dim))

    simulator, prior, x_o = prepare_sbi_problem(linear_gaussian, prior, x_o)

    snpe_common_args = dict(
        simulator=simulator,
        x_o=x_o,
        density_estimator=None,  # Use default MAF.
        prior=prior,
        z_score_x=True,
        simulation_batch_size=simulation_batch_size,
        retrain_from_scratch_each_round=False,
        discard_prior_samples=False,
    )

    if algorithm_str == "snpe_b":
        infer = SnpeB(**snpe_common_args)
    elif algorithm_str == "snpe_c":
        infer = SnpeC(num_atoms=None, sample_with_mcmc=False, **snpe_common_args)

    posterior = infer(
        num_rounds=1, num_simulations_per_round=2000, batch_size=50, max_num_epochs=30
    )
    samples = posterior.sample(num_samples)


if __name__ == "__main__":
    test_snpe_on_linearGaussian_based_on_mmd(2, "gaussian", "snpe_c", 10)
