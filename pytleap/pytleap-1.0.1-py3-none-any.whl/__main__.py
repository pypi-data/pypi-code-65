"""Provide a CLI for PyTLEAP."""
import argparse
import asyncio
from pprint import pprint

from .eap import Eap

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the EAP",
    )
    parser.add_argument(
        "--user",
        "-u",
        type=str,
        required=True,
        help="Username to access the EAP",
    )
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        required=True,
        help="Password to access the EAP",
    )

    args = parser.parse_args()

    loop = asyncio.get_event_loop_policy().new_event_loop()

    eap = Eap(args.url, args.user, args.password)
    loop.run_until_complete(eap.connect())

    clients = loop.run_until_complete(eap.get_wifi_clients())

    loop.run_until_complete(eap.disconnect())

    print(f"{len(clients)} connected clients:")
    pprint([f"{c.mac_address} ({c.hostname}): {c.ip}" for c in clients])

    loop.close()
