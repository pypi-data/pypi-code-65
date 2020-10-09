from .new_instance import NewInstance


def create(subparsers, parents):
    parser = subparsers.add_parser('new',
                                   parents=parents,
                                   help='Provision a new transfer instance. This will create an EBS volume and attach it to the host system.')
    parser.add_argument('ec2_instance_id',
                        metavar='ec2-instance-id',
                        help='The EC2 instance ID to provision for. This is the ID of the host system.')
    parser.add_argument('bucket_name',
                        metavar='bucket-name',
                        help='The name of the S3 bucket to transfer data from.')
    parser.add_argument('size',
                        type=int,
                        help='The size (in GiB) of the EBS volume that will be created.')
    parser.add_argument('-z', '--zone',
                        default=NewInstance.DEFAULT_ZONE,
                        help='The availability zone to create the EBS volume in. This should match the host system\'s zone.')
    parser.add_argument('--profile',
                        default=None,
                        help='The name of the AWS profile to use from your ~/.aws settings.')
    parser.set_defaults(_execute=execute)


def execute(args):
    NewInstance(
        args.ec2_instance_id,
        args.bucket_name,
        args.size,
        zone=args.zone,
        profile=args.profile
    ).execute()
