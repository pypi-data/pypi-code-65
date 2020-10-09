from .list_local import ListLocal


def create(subparsers, parents):
    parser = subparsers.add_parser('list-local',
                                   parents=parents,
                                   help='List all the folders and files with their size and MD5.')
    parser.add_argument('path',
                        help='The root of the path to list.')
    parser.add_argument('--skip-md5',
                        default=False,
                        action='store_true',
                        help='This will skip the MD5 calculation. This will make the list faster.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the results to. This will be in CSV format.')
    parser.set_defaults(_execute=execute)


def execute(args):
    ListLocal(
        args.path,
        out_path=args.out_path,
        skip_md5=args.skip_md5
    ).execute()
