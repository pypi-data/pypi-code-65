"""
Command line utility for reading/writing/modifying board configuration
"""
# Python 3 compatibility for Python 2
from __future__ import print_function

from .backend import Backend
from .pydebuggerconfig_errors import PydebuggerconfigError, PydebuggerconfigToolConnectionError

try:
    from .version import VERSION, BUILD_DATE, COMMIT_ID
except ImportError:
    VERSION = "0.0.0"
    COMMIT_ID = "N/A"
    BUILD_DATE = "N/A"

TOOL = 'nEDBG CMSIS-DAP'

STATUS_SUCCESS = 0
STATUS_FAILURE = 1


def print_diff(diff_in, diff_out):
    """
    Print the line difference in given inputs

    :param diff_in: First string to compare
    :param diff_out: Second string to compare
    :return:
    """
    if isinstance(diff_in, str):
        diff_in = diff_in.split('\n')

    if isinstance(diff_out, str):
        diff_out = diff_out.split('\n')

    diff_set = [("Specification:", "Data read from board:")]
    for num, item in enumerate(diff_in):
        if num >= len(diff_out):
            # Reached end of diff_out, just add empty strings instead
            diff_set.append((diff_in[num], ''))
        elif item != diff_out[num]:
            diff_set.append((diff_in[num], diff_out[num]))
    max_len = max(len(x[0]) for x in diff_set)
    diff_set.insert(1, ("-" * max_len, "-" * max_len))
    if len(diff_set) > 2:
        for diff_xml, diff_read in diff_set:
            print("{} {} {}".format(diff_xml, ' ' * (max_len - len(diff_xml)), diff_read))
    else:
        print("No difference detected.")
    print("")


def pydebuggerconfig(args):
    """
    Main entry point (after argparsing)

    :param args: command line arguments
    """
    if args.version or args.release_info:
        print("pydebuggerconfig version {}".format(VERSION))
        if args.release_info:
            print("Build date: {}".format(BUILD_DATE))
            print("Commit ID:  {}".format(COMMIT_ID))
        return STATUS_SUCCESS

    backend = Backend(args.serialnumber)

    if args.action == "generate-hex":
        return _action_generate_hex(backend, args)
    if args.action == "show":
        return _action_show(backend, args)
    if args.action == "read":
        return _action_read(backend, args)
    if args.action == "write":
        return _action_write(backend, args)
    if args.action == "verify":
        return _action_verify(backend, args)
    if args.action == "replace":
        return _action_replace(backend, args)
    if args.action == "restore":
        return _action_restore(backend)
    if args.action == "version-update":
        return _action_version_update(backend)

    print("Unknown command '{0:s}'".format(args.action))
    return STATUS_FAILURE


def _action_generate_hex(backend, args):
    if args.board is None and args.device is None:
        print("Error: either board- or device-config XML files are required.")
        return STATUS_FAILURE

    filename = backend.generate_hex(args.board, args.device)

    print("Written data to '{0:s}'".format(filename))
    return STATUS_SUCCESS


def _action_show(backend, args):
    if args.board is not None:
        # Open the product xml file
        board_xml = backend.get_board_config_as_string(args.board)
        print(board_xml)

    if args.device is not None:
        # Open the device xml file
        device_xml = backend.get_device_config_as_string(args.device)
        print(device_xml)

    if args.board is None and args.device is None:
        print("No board or device config supplied for show.")

    return STATUS_SUCCESS


def _action_read(backend, args):
    try:
        board_config_str = backend.read_board_config_as_string(factory_config=args.factory)
        device_config_str = backend.read_device_config_as_string()
    except PydebuggerconfigToolConnectionError as e_message:
        print(e_message)
        return STATUS_FAILURE

    if args.factory:
        print("FACTORY CONFIGURATION")
    print("----- Board Configuration read from the board: -----")
    print(board_config_str)
    print("----- Device Configuration read from the board: -----")
    print(device_config_str)

    return STATUS_SUCCESS


def _action_write(backend, args):
    if args.board is not None:
        try:
            board_config_str = backend.write_board_config(board_xml_file=args.board,
                                                          factory_config=args.factory,
                                                          serialnumber=args.config_serialnumber,
                                                          preserve=args.preserve)
        except PydebuggerconfigToolConnectionError as e_message:
            print(e_message)
            return STATUS_FAILURE
        except PydebuggerconfigError as e_message:
            print("ERROR: {}".format(e_message))
            return STATUS_FAILURE

        # Human readable config
        print("----- Written user {}board configuration from {}: -----"
              .format("and factory " if args.factory else "", args.board))
        print(board_config_str)
    else:
        print("No board configuration provided. SKIPPING.")

    if args.device is not None:
        try:
            device_config_str = backend.write_device_config(args.device)
        except PydebuggerconfigToolConnectionError as e_message:
            print(e_message)
            return STATUS_FAILURE

        # Human readable config
        print("----- Written device configuration from {}: -----".format(args.device))
        print(device_config_str)
    else:
        print("No device configuration provided. SKIPPING.")

    return STATUS_SUCCESS


def _action_verify(backend, args):
    if args.board is not None:
        # Open the product xml file
        board_xml = backend.get_board_config_as_string(args.board)

        try:
            board_read = backend.read_board_config_as_string(factory_config=args.factory)
        except PydebuggerconfigToolConnectionError as e_message:
            print(e_message)
            return STATUS_FAILURE

        print("\nComparing board data to specification ({}):".format(args.board))
        print_diff(board_xml, board_read)

    if args.device is not None:
        # Open the device xml file
        device_xml = backend.get_device_config_as_string(args.device)

        try:
            device_read = backend.read_device_config_as_string()
        except PydebuggerconfigToolConnectionError as e_message:
            print(e_message)
            return STATUS_FAILURE

        print("\nComparing device data to specification ({}):".format(args.device))
        print_diff(device_xml, device_read)

    if args.board is None and args.device is None:
        print("No board or device config supplied for verification.")

    return STATUS_SUCCESS


def _action_replace(backend, args):
    if args.register is not None:
        registers_dict = {}
        for param in args.register:
            if param.count('='):
                reg, value = param.split('=', 1)
                print("Writing {} into register {}...".format(value, reg))
                registers_dict[reg] = value
            else:
                print("Invalid parameter given: {}".format(param))
        try:
            # Replace the values
            backend.replace(registers_dict, args.factory)
        except PydebuggerconfigToolConnectionError as e_message:
            print(e_message)
            return STATUS_FAILURE
        except PydebuggerconfigError as e_message:
            print("ERROR: {}".format(e_message))
            return STATUS_FAILURE
    else:
        print("No register specified. Use the -r flag to specify register.")

    return STATUS_SUCCESS


def _action_restore(backend):
    print("Restoring factory board configuration")
    try:
        backend.restore_board_config()
    except PydebuggerconfigToolConnectionError as e_message:
        print(e_message)
        return STATUS_FAILURE

    return STATUS_SUCCESS


def _action_version_update(backend):
    try:
        (update_found, latest_version) = backend.update_board_config_version()
    except PydebuggerconfigToolConnectionError as e_message:
        print(e_message)
        return STATUS_FAILURE
    if update_found:
        print("Updated board config (user) version to {}".format(latest_version))
    else:
        print("Board config specification is up to date, {}".format(latest_version))

    return STATUS_SUCCESS
