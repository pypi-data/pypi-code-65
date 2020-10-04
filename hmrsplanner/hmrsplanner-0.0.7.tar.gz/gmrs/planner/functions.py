
from .submodel import SubModel


def get_constant_fnc(p, t=1):
    assert p < 1 and p > 0
    return [(p, t), (1-p, t)]


def evaluations_iterator(subModel: SubModel):
    configs = subModel.get_configs()
    for config in configs:
        yield (config, subModel.eval(config))


def submodels_evaluations_combinations(*models):
    header_iter = evaluations_iterator(models[0])
    if len(models) == 1:
        # single configuration
        for model_eval in header_iter:
            yield model_eval
    else:
        # combined configurations
        for header_eval in header_iter:
            rest_iter = submodels_evaluations_combinations(*models[1:])
            for rest_eval in rest_iter:
                if isinstance(rest_eval, tuple):
                    yield (header_eval, *rest_eval)
                else:
                    yield (header_eval, rest_eval)
