import os
import logging
import argparse
from pi_lightsensor_webthing.lightsensor_webthing import run_server
from pi_lightsensor_webthing.unit import register, deregister, printlog

PACKAGENAME = 'pi_lightsensor_webthing'
ENTRY_POINT = "lightsensor"
DESCRIPTION = "A web connected digital light sensor measuring the intensity of ambient light on Raspberry Pi"


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--command', metavar='command', required=True, type=str, help='the command. Supported commands are: listen (run the webthing service), register (register and starts the webthing service as a systemd unit, deregister (deregisters the systemd unit), log (prints the log)')
    parser.add_argument('--port', metavar='port', required=True, type=int, help='the port of the webthing serivce')
    parser.add_argument('--gpio', metavar='gpio', required=False, type=int, help='the gpio number wired to the device')
    parser.add_argument('--name', metavar='name', required=False, type=str, default="", help='the name')
    args = parser.parse_args()

    if args.command == 'listen':
        print("running " + PACKAGENAME + " on port " + str(args.port) + "/gpio " + str(args.gpio))
        run_server(int(args.port), int(args.gpio), args.name, DESCRIPTION)
    elif args.command == 'register':
        print("register " + PACKAGENAME + " on port " + str(args.port) + "/gpio " + str(args.gpio) + " and starting it")
        register(PACKAGENAME, ENTRY_POINT, int(args.port), args.name, int(args.gpio))
    elif args.command == 'deregister':
        deregister(PACKAGENAME, int(args.port))
    elif args.command == 'log':
        printlog(PACKAGENAME, int(args.port))
    else:
        print("usage " + ENTRY_POINT + " --help")


if __name__ == '__main__':
    log_level = os.environ.get("LOGLEVEL", "INFO")
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=log_level, datefmt='%Y-%m-%d %H:%M:%S')

    main()

