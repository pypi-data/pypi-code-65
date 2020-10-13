import os

main_folder = os.path.dirname(os.path.abspath(__file__))

propensity_params_path = os.path.join(main_folder, 'propensity.yaml')
__all__ = ['propensity_params_path']