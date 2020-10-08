
import logging

def set_log_parser_args(parser):
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable info logging")
    parser.add_argument("-vv", "--extra_verbose", action="store_true", help="Enable debug logging")

def eval_log_parser_args(args, msgFormat="%(asctime)s %(levelname)s:  %(message)s"):
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format=msgFormat)
    elif args.extra_verbose:
        logging.basicConfig(level=logging.DEBUG, format=msgFormat)
    else:
        logging.basicConfig(level=logging.WARN, format=msgFormat)