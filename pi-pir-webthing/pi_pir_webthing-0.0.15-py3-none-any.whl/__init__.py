import argparse
import logging
from pi_pir_webthing.motionsensor_webthing import run_server
from pi_pir_webthing.unit import register, deregister, printlog, list_installed

PACKAGENAME = 'pi_pir_webthing'
ENTRY_POINT = "pir"
DESCRIPTION = "A web connected PIR motion sensor detecting movement running on Raspberry Pi"


def print_info():
    print("usage " + ENTRY_POINT + " --help for command options")
    print("examples")
    for service_info in list_installed(PACKAGENAME):
        port = service_info[1]
        is_active = service_info[2]
        print("sudo " + ENTRY_POINT + " --command log --port " + port)
        if is_active:
            print("sudo " + ENTRY_POINT + " --command deregister --port " + port)
        else:
            print("sudo " + ENTRY_POINT + " --command register --port " + port + " --gpio 14")
            print("sudo " + ENTRY_POINT + " --command listen --port " + port + " --gpio 14")

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--command', metavar='command', required=False, type=str, help='the command. Supported commands are: listen (run the webthing service), register (register and starts the webthing service as a systemd unit, deregister (deregisters the systemd unit), log (prints the log)')
    parser.add_argument('--port', metavar='port', required=False, type=int, help='the port of the webthing serivce')
    parser.add_argument('--gpio', metavar='gpio', required=False, type=int, help='the gpio number wired to the device')
    parser.add_argument('--name', metavar='name', required=False, type=str, default="", help='the name')
    args = parser.parse_args()

    if args.command is None:
        print_info()
    elif args.command == 'listen':
        if args.port is None:
            print("--port is mandatory")
        elif args.gpio is None:
            print("--gpio is mandatory")
        else:
            print("running " + PACKAGENAME + "/" + args.name + " on port " + str(args.port) + "/gpio " + str(args.gpio))
            run_server(int(args.port), int(args.gpio), args.name, DESCRIPTION)
    elif args.command == 'register':
        if args.port is None:
            print("--port is mandatory")
        elif args.gpio is None:
            print("--gpio is mandatory")
        else:
            print("register " + PACKAGENAME + "/" + args.name + " on port " + str(args.port) + "/gpio " + str(args.gpio) + " and starting it")
            register(PACKAGENAME, ENTRY_POINT, int(args.port), args.name, int(args.gpio))
    elif args.command == 'deregister':
        if args.port is None:
            print("--port is mandatory")
        else:
            deregister(PACKAGENAME, int(args.port))
    elif args.command == 'log':
        if args.port is None:
            print("--port is mandatory")
        else:
            printlog(PACKAGENAME, int(args.port))
    else:
        print("unsupported command")
        print_info()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

    main()

