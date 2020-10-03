import logging
import argparse
from pushgateway.gateway import run
from pushgateway.config import default_config_file
from pushgateway.unit import register, deregister, printlog

PACKAGENAME = 'pushgateway'
ENTRY_POINT = "pushgateway"
DESCRIPTION = "A push gateway sending webthing properties updates to a openhab server"


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--command', metavar='command', required=True, type=str, help='the command. Supported commands are: listen (run the service), register (register and starts the service as a systemd unit, deregister (deregisters the systemd unit), log (prints the log)')
    parser.add_argument('--filename', metavar='filename', required=False, type=str,  help='the config filename')
    args = parser.parse_args()

    if args.filename is None:
        filename = default_config_file()
    else:
        filename = args.filename

    if args.command == 'listen':
        logging.info("running " + PACKAGENAME + " with config " + filename)
        run(filename)
    elif args.command == 'register':
        logging.info("register " + PACKAGENAME + " with config " + filename)
        register(PACKAGENAME, ENTRY_POINT, filename)
    elif args.command == 'deregister':
        deregister(PACKAGENAME)
    elif args.command == 'log':
        printlog(PACKAGENAME)
    else:
        logging.info("usage " + ENTRY_POINT + " --help")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    main()

