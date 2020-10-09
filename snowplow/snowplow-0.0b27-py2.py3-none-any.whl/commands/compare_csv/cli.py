from .compare_csv import CompareCsv


def create(subparsers, parents):
    parser = subparsers.add_parser('compare-csv',
                                   parents=parents,
                                   help='Compare a CSV file from the list-local command with a local directory.')
    parser.add_argument('path',
                        help='The root of the path to compare.')
    parser.add_argument('csv',
                        help='The CSV file generated from the list-local command.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the results to. This will be in CSV format.')
    parser.set_defaults(_execute=execute)


def execute(args):
    CompareCsv(
        args.path,
        args.csv,
        out_path=args.out_path
    ).execute()
