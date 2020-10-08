from __future__ import print_function
import argparse
from .random_csv import RandCSV


def parse_args(*args):
    """Argument parser.
    """
    # Create the parser.
    mkcsv_parser = argparse.ArgumentParser(
        description="Generate random CSVs."
    )

    # Add arguments
    mkcsv_parser.add_argument(
        '--rows',
        '-m',
        action='store',
        type=int,
        required=True,
        help='Number of rows the desired CSV file contains.'
    )
    mkcsv_parser.add_argument(
        '--cols',
        '-n',
        action='store',
        type=int,
        required=True,
        help='Number of columns the desired CSV file contains.'
    )
    mkcsv_parser.add_argument(
        '--output',
        '-o',
        action='store',
        type=str,
        required=False,
        default="rand.csv",
        help='Output file name.'
    )
    mkcsv_parser.add_argument(
        '--data-types',
        '-d',
        action='store',
        nargs='+',
        required=False,
        default=['integer'],
        help='Data types present in the desired CSV file. Supported data types are: integer, float, token.'
    )
    mkcsv_parser.add_argument(
        '--nan-freq',
        '-a',
        action='store',
        type=float,
        required=False,
        default=.0,
        help='Approx. frequency of NaN values contained in desired CSV file.'
    )
    mkcsv_parser.add_argument(
        '--empty-freq',
        '-e',
        action='store',
        type=float,
        required=False,
        default=.0,
        help='Approx. frequency of empty values contained in desired CSV file.'
    )
    mkcsv_parser.add_argument(
        '--index-col',
        '-i',
        action='store_true',
        dest='index_col',
        help='Flag, the left most column should be a row index (ascending integer).'
    )
    mkcsv_parser.set_defaults(index=False)
    mkcsv_parser.add_argument(
        '--title-row',
        '-t',
        action='store_true',
        dest='title_row',
        help='Flag, the top most row should be a column index (ascending integer).'
    )
    mkcsv_parser.set_defaults(title=False)
    mkcsv_parser.add_argument(
        '--byte-size',
        '-b',
        action='store',
        type=int,
        required=False,
        default=8,
        help='Character length of the individual random values.'
    )
    return mkcsv_parser.parse_args(*args)


def cli(*args):
    """CLI entry point.
    """
    if len(args):
        args = parse_args(*args)
    else:
        # pipx returns here
        args = parse_args()
    csv = RandCSV(
        rows=args.rows,
        cols=args.cols,
        byte_size=args.byte_size,
        data_types=args.data_types,
        nan_freq=args.nan_freq,
        empty_freq=args.empty_freq,
        index_col=args.index_col,
        title_row=args.title_row,
        )
    csv.to_file(args.output)
    print(f'generated CSV file: {args.output}')
    return None
