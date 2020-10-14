from argparse import ArgumentParser
from collections import defaultdict
from functools import partial

from cpymad.madx import Madx, TwissFailed
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


parser = ArgumentParser(prog='python -m twissgrid')
parser.add_argument('script', help='File path to MADX script')
parser.add_argument('p1', help='Lattice parameter 1 (format: "label->attribute")')
parser.add_argument('p2', nargs='?', help='Lattice parameter 2 (format: "label->attribute")')
parser.add_argument('--p1lb', type=float, help='Parameter 1, lower boundary (defaults to --margin)')
parser.add_argument('--p1ub', type=float, help='Parameter 1, upper boundary (defaults to --margin)')
parser.add_argument('--p2lb', type=float, help='Parameter 2, lower boundary (defaults to --margin)')
parser.add_argument('--p2ub', type=float, help='Parameter 2, upper boundary (defaults to --margin)')
parser.add_argument('--margin', type=float, default=0.01,
                    help='Fraction of the current value to be used as a margin if a boundary is missing')
parser.add_argument('--n1', type=int, default=100, help='Number of grid points for parameter 1')
parser.add_argument('--n2', type=int, default=100, help='Number of grid points for parameter 2')
parser.add_argument('--funcs', type=str, nargs='+', default=('betx', 'bety'), help='Optics functions to plot')
parser.add_argument('--target', default='#e', help='Label of the target element where optics functions are observed')
parser.add_argument('--beta0', help='Label of BETA0 command (this must be part of the MADX script)')
parser.add_argument('--threshold', type=float, nargs='*', help='Plot threshold line on each optics plot')
parser.add_argument('--figsize', type=float, nargs=2, default=(14, 10), help='Figure size in inches')


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


def fill_boundaries(parameters, *, twiss, margin):
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
        if param['lb'] is None:
            param['lb'] = (1 - margin) * value
        if param['ub'] is None:
            param['ub'] = (1 + margin) * value


def create_grid(parameters):
    xs = [np.linspace(p['lb'], p['ub'], p['np']) for p in parameters]
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
    args = parser.parse_args()
    args.funcs = [f.lower() for f in args.funcs]
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
    twiss = madx.twiss(**kwargs)

    parameters = [
        dict(name=args.p1, lb=args.p1lb, ub=args.p1ub, np=args.n1),
        dict(name=args.p2, lb=args.p2lb, ub=args.p2ub, np=args.n2),
    ]
    if parameters[1]['name'] is None:
        del parameters[1]
    fill_boundaries(parameters, twiss=twiss, margin=args.margin)

    data = compute_optics(parameters, config=args, madx_input=madx.input, madx_twiss=partial(madx.twiss, **kwargs))
    plot_func = {1: plot_1d, 2: plot_2d}[len(parameters)]
    axes = plot_func(parameters, data=data, config=args)
    plt.show()
