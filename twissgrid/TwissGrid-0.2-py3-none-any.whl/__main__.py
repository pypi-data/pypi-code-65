from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from collections import defaultdict
from functools import partial
import operator
import re

from cpymad.madx import Madx, TwissFailed
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


parser = ArgumentParser(prog='python -m twissgrid', formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('script', help='File path to MADX script')
parser.add_argument('p1', type=str.lower, help='Lattice parameter 1 (format: label[->attribute])')
parser.add_argument('p2', type=str.lower, nargs='?', help='Lattice parameter 2 (format: label[->attribute])')
groups = []
for i in (1, 2):
    group = parser.add_argument_group(f'Parameter {i}')
    group.add_argument(f'--p{i}lb', type=float, help='Lower boundary for parameter scan')
    group.add_argument(f'--p{i}ub', type=float, help='Upper boundary for parameter scan')
    group.add_argument(f'--p{i}delta', type=float, help='Compute missing boundaries as a distance to the current value '
                                                        '(i.e. "lb = value - delta" and "ub = value + delta"); '
                                                        '--delta takes precedence over --margin')
    group.add_argument(f'--p{i}margin', type=float, help='Compute missing boundaries as a fraction of the current value '
                                                         '(i.e. "lb = (1 - margin)*value" and "ub = (1 + margin)*value")',
                       default=0.01)
    group.add_argument(f'--p{i}n', type=int, default=100, help='Number of grid points for parameter scan')
    groups.append(group)
parser.add_argument('--funcs', type=str.lower, nargs='+', default=('betx', 'bety'), help='Optics functions to plot')
parser.add_argument('--target', type=str.lower, default='#e', help='Label of the target element where optics functions are observed')
parser.add_argument('--beta0', type=str.lower, help='Label of BETA0 command (this must be part of the MADX script)')
parser.add_argument('--threshold', type=float, nargs='*', help='Plot threshold line on each optics plot')
parser.add_argument('--figsize', type=float, nargs=2, default=(14, 10), help='Figure size in inches')


class GroupedNamespace(Namespace):
    prefix = 'p'
    blank = 'name'

    def __init__(self):
        super().__init__()
        self.groups = defaultdict(Namespace)

    def __setattr__(self, name, value):
        match = re.match(f'{self.prefix}([0-9]+)', name)
        if match is not None:
            setattr(self.groups[int(match.group(1))], name[match.end():] or self.blank, value)
        else:
            super().__setattr__(name, value)


DEFAULT_ATTRIBUTES = dict(quadrupole='k1', sextupole='k2')
UNITS = dict.fromkeys(('betx', 'bety', 'dx', 'dy'), 'm')
UNITS['k1'] = '1/m^2'
UNITS['k2'] = '1/m^3'


def with_unit(name):
    if '->' in name:
        key = name.split('->')[1]
    else:
        key = name
    try:
        unit = UNITS[key]
    except KeyError:
        return name
    else:
        return f'{name} [{unit}]'


def get_attribute_from_twiss(row, attr):
    try:
        return row[attr]
    except KeyError:
        if attr in ('k1', 'k2'):
            return row[f'{attr}l'] / row['l']
        else:
            raise ValueError(f'Unknown attribute: {attr}')


def fill_boundaries(parameters, *, twiss):
    def _set_default(par, key, *, ref):
        value, delta, margin = operator.itemgetter(key, 'delta', 'margin')(par)
        if value is None:
            op = dict(lb=operator.sub, ub=operator.add)[key]
            if delta is not None:
                value = op(ref, delta)
            elif margin is not None:
                value = ref * op(1, margin)
            else:
                raise ValueError(f'Either --{key} or --delta or --margin needs to be given')
            par[key] = value

    for param in parameters:
        try:
            label, attr = param['name'].split('->')
        except ValueError:
            label, attr = param['name'], None
        row = twiss.row(twiss.row_names().index(label))
        if attr is None:
            attr = DEFAULT_ATTRIBUTES[row['keyword'].lower()]
            param['name'] += f'->{attr}'
        value = get_attribute_from_twiss(row, attr)
        _set_default(param, 'lb', ref=value)
        _set_default(param, 'ub', ref=value)


def create_grid(parameters):
    xs = [np.linspace(p['lb'], p['ub'], p['n']) for p in parameters]
    return np.meshgrid(*xs)


def compute_optics(parameters, *, config, madx_input, madx_twiss):
    update_cmd = '; '.join(f'{p["name"]} = {{}}' for p in parameters) + ';'
    grid = create_grid(parameters)
    result = defaultdict(list)
    for xs in zip(*(x.ravel() for x in grid)):
        madx_input(update_cmd.format(*xs))
        try:
            twiss = madx_twiss()
        except TwissFailed:
            row = dict.fromkeys(config.funcs, float('nan'))
        else:
            row = twiss.row(twiss.row_names().index(config.target))
        for output in config.funcs:
            result[output].append(row[output])
    return grid, {k: np.array(v).reshape(grid[0].shape) for k, v in result.items()}


def plot_1d(parameters, *, data, config):
    x_data, y_data = data
    axes = []
    for name, values in y_data.items():
        fig, ax = plt.subplots(figsize=config.figsize)
        ax.set(title=f'{name} @ {config.target}'.upper(),
               xlabel=with_unit(parameters[0]['name']), ylabel=with_unit(name))
        ax.plot(*x_data, values, '-')
        if config.threshold[name] is not None:
            ax.axhline(config.threshold[name], ls='--', color='red')
        axes.append(ax)
    return axes


def plot_2d(parameters, *, data, config):
    x_data, y_data = data
    axes = []
    for name, values in y_data.items():
        fig = plt.figure(figsize=config.figsize)
        ax = fig.gca(projection='3d')
        ax.set(title=f'{name} @ {config.target}'.upper(),
               xlabel=with_unit(parameters[0]['name']), ylabel=with_unit(parameters[1]['name']))
        surf = ax.plot_surface(*x_data, values, cmap='coolwarm', linewidth=0, antialiased=False)
        cbar = fig.colorbar(surf, shrink=0.5, aspect=8)
        cbar.set_label(with_unit(name))
        axes.append(ax)
    return axes


if __name__ == '__main__':
    args = parser.parse_args(namespace=GroupedNamespace())
    if args.threshold is None:
        args.threshold = dict.fromkeys(args.funcs, None)
    elif len(args.threshold) == 1:
        args.threshold = dict.fromkeys(args.funcs, args.threshold[0])
    elif len(args.threshold) == len(args.funcs):
        args.threshold = dict(zip(args.funcs, args.threshold))
    else:
        raise ValueError('Threshold must be either a single value or match the number of --funcs')

    madx = Madx(stdout=False)
    madx.call(args.script)

    kwargs = {}
    if args.beta0 is not None:
        kwargs['beta0'] = args.beta0
    try:
        twiss = madx.twiss(**kwargs)
    except TwissFailed:
        raise RuntimeError('Failed to compute Twiss for original MADX script')

    parameters = [vars(g) for g in args.groups.values()]
    if parameters[1]['name'] is None:
        del parameters[1]
    fill_boundaries(parameters, twiss=twiss)

    data = compute_optics(parameters, config=args, madx_input=madx.input, madx_twiss=partial(madx.twiss, **kwargs))
    plot_func = {1: plot_1d, 2: plot_2d}[len(parameters)]
    axes = plot_func(parameters, data=data, config=args)
    plt.show()
