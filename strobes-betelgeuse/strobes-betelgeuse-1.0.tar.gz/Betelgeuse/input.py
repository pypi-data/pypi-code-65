from argparse import ArgumentParser, ArgumentTypeError


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        "--Host",
        metavar='Host',
        dest='Host',
        required=True,
        type=str,
        help="Give hostname where Strobes is hosted")

    parser.add_argument(
        "--Port",
        metavar='Port',
        dest='Port',
        default=443,
        type=int,
        help="Give Port where Strobes is hosted")

    parser.add_argument(
        "-s",
        metavar='Scheme',
        dest='Scheme',
        default="https",
        type=str,
        help="HTTP or HTTPS")

    parser.add_argument(
        "-p",
        metavar='Path',
        dest='Path',
        default="/v1",
        type=str,
        help="/api/v1")

    parser.add_argument(
        "-w",
        dest="Wait",
        required=False,
        type=str2bool,
        nargs='?',
        default=True,
        help="If wait is required or not")

    parser.add_argument(
        "-v",
        dest='Log_level',
        type=str,
        default='error',
        help="Enter the log level required(debug, info, warning, error or critical)")

    parser.add_argument(
        "-a",
        dest="Authorization",
        required=True,
        help="Authorization token")

    parser.add_argument(
        "-r",
        dest="Remote_access",
        required=True,
        help="Provide configuration Remote token")

    parser.add_argument(
        "-e",
        dest="Exit",
        required=False,
        type=str2bool,
        default=True,
        help="Raise exception on build fail")

    parser.add_argument(
        "-t",
        dest="Target",
        required=False,
        type=str,
        help="Target for scanning.")

    args = parser.parse_args()

    return args
