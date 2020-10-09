from .list_s3 import ListS3


def create(subparsers, parents):
    parser = subparsers.add_parser('list-s3',
                                   parents=parents,
                                   help='List all the files in an S3 bucket with their file size.')
    parser.add_argument('bucket',
                        help='The S3 bucket to list.')
    parser.add_argument('-p', '--prefix',
                        default=None,
                        help='Prefix within the bucket to list.')
    parser.add_argument('--profile',
                        default=None,
                        help='The name of the AWS profile to use from your ~/.aws settings.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the results to. This will be in CSV format.')
    parser.set_defaults(_execute=execute)


def execute(args):
    ListS3(
        args.bucket,
        prefix=args.prefix,
        out_path=args.out_path,
        profile=args.profile
    ).execute()
