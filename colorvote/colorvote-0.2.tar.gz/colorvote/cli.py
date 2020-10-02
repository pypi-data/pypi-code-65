import argparse
import json
import sys
import os

from json.decoder import JSONDecodeError

from .config import read_config, exists_config, initialize_config

from .colorvote import Colorvote

DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), '.colorvote')

def main():
  parser = argparse.ArgumentParser(description='Colorvote CLI tool',
      prog='colorvote')

  subparser = parser.add_subparsers(title='subcommands',
      description='list of valid subcommands',
      dest='cmd',
      required=True)

  parser.add_argument('-d', '--datadir', 
    help='path to configuration and data directory')
  parser.add_argument('-n', '--nosend', action='store_true', 
    help='don\'t execute commands in wallet')
  parser.add_argument('-v', '--verbose', action='store_true', 
    help='print the JSON RPC wallet commands')

  parser_create = subparser.add_parser('create', help='create a new election')
  parser_create.add_argument('address', help='issuing transaction')
  parser_create.add_argument('meta', 
    help='string to include in genesis transaction')
  parser_create.add_argument('--unit', type=float, 
    help='value of a single vote (default 1 BTC)', default=1)

  parser_issue = subparser.add_parser('issue', help='issue new votes')
  parser_issue.add_argument('election', help='address of election')
  parser_issue.add_argument('addresses', 
    help='JSON list of addresses to receive votes')
  parser_issue.add_argument('amounts', 
    help='JSON list of vote count to issue to each address')

  parser_send = subparser.add_parser('send', help='send a vote')
  parser_send.add_argument('election', help='address of election')
  parser_send.add_argument('address', help='address that holds the vote')
  parser_send.add_argument('recepient', help='address of candidate')
  parser_send.add_argument('amount', type=int, help='number of votes')

  parser_balance = subparser.add_parser('balance', 
    help='get unspent voting coins in wallet (or by address)')
  parser_balance.add_argument('--address', help='address to show balance for')

  parser_list = subparser.add_parser('list', 
    help='list all elections on blockchain')
  parser_list.add_argument('--count', type=int, 
    help='number of results to return')

  parser_scan = subparser.add_parser('scan', 
    help='scan blockchain for new votes')
  parser_scan.add_argument('--full', action='store_true', 
    help='truncate local database and rescan blockchain')

  parser_trace = subparser.add_parser('trace', 
    help='trace a vote to issuing transaction')

  parser_count = subparser.add_parser('count', 
    help='count votes for an election')
  parser_count.add_argument('election', help='address of election')
  parser_count.add_argument('--count', type=int, 
    help='number of results to return')

  parsed = parser.parse_args()

  # check and load the config
  config_dir = parsed.datadir if parsed.datadir else DEFAULT_CONFIG_DIR

  if exists_config(config_dir):
    config = read_config(config_dir)

  else:
    if input(("Could not find configuration. Would you like to initialize "
    "it at %s (y/N)? ") % (config_dir)).lower() == 'y':
      initialize_config(config_dir)
      print("Configuration initialized.")

    return

  config['database'] = os.path.join(config_dir, 'database.sqlite3')

  colorvote = Colorvote(config)

  # Check if database is synced for relevant commands
  if parsed.cmd in ['create', 'issue', 'send']:
    if not colorvote.is_db_synced():
      print("Database is not in sync, run colorvote.py scan first")

      return

  if parsed.cmd == 'create':
    tx = colorvote.create_id_tx(parsed.address, parsed.unit, parsed.meta)

    if parsed.verbose:
      print(json.dumps(tx, indent=2))

    if not parsed.nosend:
      txid = colorvote.rpc.send_transaction(tx)
      print(txid)

  elif parsed.cmd == 'issue':
    tx = colorvote.create_issue_tx(
      parsed.election, 
      json.loads(parsed.addresses),
      json.loads(parsed.amounts)
    )

    if parsed.verbose:
      print(json.dumps(tx, indent=2))

    if not parsed.nosend:
      txid = colorvote.rpc.send_transaction(tx)
      print(txid)

  elif parsed.cmd == 'send':
    tx = colorvote.create_transfer_tx(
      parsed.election,
      parsed.address,
      parsed.recepient,
      parsed.amount
    )

    if parsed.verbose:
      print(json.dumps(tx, indent=2))

    if not parsed.nosend:
      txid = colorvote.rpc.send_transaction(tx)
      print(txid)


  elif parsed.cmd == 'scan':
    colorvote.scan()

