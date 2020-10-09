from .compare_s3 import CompareS3


def create(subparsers, parents):
    parser = subparsers.add_parser('compare-s3',
                                   parents=parents,
                                   help='Compare a local directory against an S3 bucket.')
    parser.add_argument('path',
                        help='The root of the local path to compare.')
    parser.add_argument('bucket',
                        help='The S3 bucket to compare against.')
    parser.add_argument('-p', '--prefix',
                        default=None,
                        help='Prefix within the bucket to compare against.')
    parser.add_argument('--profile',
                        default=None,
                        help='The name of the AWS profile to use from your ~/.aws settings.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the results to. This will be in CSV format.')
    parser.set_defaults(_execute=execute)


def execute(args):
    CompareS3(
        args.path,
        args.bucket,
        prefix=args.prefix,
        out_path=args.out_path,
        profile=args.profile
    ).execute()
