import json
from math import log, floor

from .database import Database
from .rpc import RPC
from .models import Election, Transaction

class Colorvote(object):
  """This is an interface class for the colorvote package.
  """

  def __init__(self, config):
    self.config = config

    self.db = Database(config['database'])
    self.rpc = RPC(config['rpc']['username'], config['rpc']['password'], \
      port=config['rpc']['port'], host=config['rpc']['host'])

    self.txfee = 1.0

    return

  def set_txfee(self, amount):
    """Set the transaction fee to use when building transactions.

    :param amount: The transaction fee
    :type amount: float
    """
    self.txfee = amount


  def create_id_tx(self, address, unit=1.0, meta=''):
    """Creates an identification transaction to register an election.

    To create an election we select an unspent output (UTXO) with specified
    address.  Then we create a transaction with that UTXO as input, and two
    outputs.  One to send the whole amount back to the same address, and one
    ``OP_RETURN`` output that contains the election metadata.

    :param address: The election address
    :type address: str
    :param unit: The currency value of a single vote
    :type unit: float, optional
    :param meta: A string of ASCII characters to include in transaction, up to \
    80 characters
    :type meta: str, optional

    :return: A list containing the inputs and outputs as accepted by the \
    createrawtransaction wallet command.
    :rtype: list
    """

    if any(ord(c) > 128 for c in meta):
      raise Exception("Meta string contains illegal characters")

    if len(meta) > 80:
      raise Exception("Meta string is too long")
    unspent = self.rpc.execute("listunspent")

    i = 0

    vote_value = self.encode_vote_value(unit)

    while i < len(unspent) and unspent[i]['address'] != address:
      i += 1

    if i >= len(unspent):
      raise Exception(
        "Could not find an unspent transaction output for given address")

    inputs = [
      {
        'txid': unspent[i]['txid'],
        'vout': unspent[i]['vout'],
        'sequence': 177 + 256*vote_value
      }
    ]

    outputs = {
      unspent[i]['address']: unspent[i]['amount'] - self.txfee,
      'data': meta.encode('ascii').hex()
    }

    return [inputs, outputs]


  def encode_vote_value(self, amount):
    """Encodes the value of one vote as defined by the protocol. The encoded
    value needs to be included in the nSequence field of an init transaction.
    
    :param amount: The amount in BTC to encode.
    :type amount: float

    :return: The integer value of the encoded byte.
    :rtype: int
    """
    unit = int(amount*10e8)
    n = floor(log(unit, 10))

    k = int(unit/10**n)

    if k*10**n != unit:
      raise Exception(
        "Supplied unit value cannot be encoded, see documentation")

    return k+16*n % 256


  def decode_vote_value(self, value):
    """Decodes the value of one vote as encoded in the second least significant
    byte of an init transaction.

    :param value: The integer value of the byte
    :type value: int

    :return: The vote value in BTC
    :rtype: float
    """
    k = value % 16
    n = floor(value/16)

    return k*10**n / 10e8


  def create_issue_tx(self, election, addresses, amounts):
    """Creates an issuing transaction to issue new votes for an existing \
    election.

    To issue coins we need to own an address that has made an identification
    transaction. The address is the color/ID of the election. This command looks
    up the identifiaction transaction to read the vote value (the amount of the
    currency that is equal to one vote). Then finds an unspent output with
    sufficient funds and sends them with an nSequence according to the protocol.

    :param election: Address of election
    :type election: str
    :param addresses: list of addresses to issue votes to
    :type addresses: list
    :param amounts: List of number of votes to issue to each address in \
    ``addresses``
    :type amounts: list

    :return: Transaction ID returned by wallet
    :rtype: str
    """

    election_info = self.db.get_election(election)

    if len(addresses) != len(amounts):
      raise Exception("Number of addresses doesn't match number of amounts")

    """
    if not election_info:
      raise Exception(
        "There is no election with this address, try rescanning the blockchain")
    """

    unit = election_info.unit

    vote_count = sum(amounts)

    # Search for an UTXO with enough funds
    unspent = self.rpc.execute("listunspent")

    utxo = None

    for u in unspent:
      if u['address'] == election and u['amount'] >= vote_count*unit+self.txfee:
        utxo = u
        break

    if not utxo:
      raise Exception(
        "Could not find an unspent output to use, needs {} plus {} txfee" \
          .format(vote_count*unit, self.txfee))

    # Create and send transaction 
    inputs = [
      {
        'txid': utxo['txid'],
        'vout': utxo['vout'],
        'sequence': 178
      }
    ]

    outputs = dict(zip(addresses, amounts))

    change = utxo['amount'] - vote_count*unit - self.txfee

    if change > 0:
      outputs[election] = change

    return [inputs, outputs]


  def create_transfer_tx(self, election, address, recepient, amount=1):
    """Creates a transfer transaction to send votes between addresses.

    NOTE: Currently does not support combining votes from multiple UTXOs.

    :param election: The election ID to vote in
    :type election: str
    :param address: Address that currently holds the votes in the wallet
    :type address: str
    :param recepient: Address of the recepient of the votes
    :type recepient: str
    :param amount: Number of votes to send
    :type amount: int

    :return: Transaction ID returned by wallet
    :rtype: str
    """

    # First step is to find wallet UTXOs associated with this election
    unspent = self.db.get_unspent(address)
    print("Found {} unspent outputs for this address".format(len(unspent)))

    vote_unit = self.db.get_election(election).unit

    vote_utxo = None

    for u in unspent:
      if u['amount'] >= amount*vote_unit:
        vote_utxo = u

    if not vote_utxo:
      raise Exception("This address doesn't hold sufficient votes")

    # Find an input to use for fees
    unspent = self.rpc.execute("listunspent")

    fee_utxo = None

    for u in unspent:
      if u['address'] != address and u['amount'] >= self.txfee:
        fee_utxo = u
        break

    if not fee_utxo:
      raise Exception("Can't find an additional UTXO to add fees")

    inputs = [
      {
        'txid': vote_utxo['txid'],
        'vout': vote_utxo['n'],
        'sequence': 179
      },
      {
        'txid': fee_utxo['txid'],
        'vout': fee_utxo['vout'],
      }
    ]

    outputs = dict()

    outputs[recepient] = amount*vote_unit

    # If not all votes are used then send remaining back
    if outputs[recepient] < vote_utxo['amount']:
      outputs[address] = vote_utxo['amount']-outputs[recepient]

    if fee_utxo['amount'] > self.txfee:
      outputs[fee_utxo['address']] = fee_utxo['amount'] - self.txfee

    return [inputs, outputs]


  def scan(self):
    """Iterates through the blockchain and finds colorvote transactions.
    """
    height = int(self.db.get_setting('height'))

    blocks = self.rpc.execute('getinfo')['blocks']

    print("Starting scan at block %s, blockchain height %s" % (height, blocks))

    for i in range(height, blocks+1):
      block_hash = self.rpc.execute("getblockhash", [i])
      block = self.rpc.execute("getblock", [block_hash])

      if i % 1000 == 0:
        print("Scanning %i - %i" % (i, i+999))
        self.db.set_setting('height', i)

      for tx in block['tx']:
        raw = self.rpc.execute("getrawtransaction", [tx])
        transaction = self.rpc.execute("decoderawtransaction", [raw])

        # The sequence tag should always be in the first input
        sequence = transaction['vin'][0]['sequence']

        if sequence == 4294967295 or sequence == 0:
          continue

        # Identification transaction
        if sequence % 256 == 177:
          id_tx = self.read_id_tx(block, transaction)

          if id_tx.unit == 0:
            # Vote unit should be nonzero
            continue

          if self.db.get_election(id_tx.address):
            # This address is already an election address
            continue

          print(id_tx)
          self.db.insert_election(id_tx)

        # Issuance transaction
        if sequence % 256 == 178:
          outs = self.read_issue_tx(block, transaction)

          for out in outs:
            if self.db.get_transaction(out.txid, out.n):
              continue

            print(out)
            self.db.insert_transaction(out)

        # Transfer transaction
        if sequence % 256 == 179:
          print("Found transfer transaction")
          outs = self.read_transfer_tx(block, transaction)

          for out in outs:
            if self.db.get_transaction(out.txid, out.n):
              continue

            print(out)
            self.db.insert_transaction(out)


    self.db.set_setting('height', blocks)
    return


  def read_id_tx(self, block, transaction):
    """Decode an identification transaction.

    :param transaction: A transaction as returned by the \
    ``decoderawtransaction`` wallet command
    :type transaction: dict

    :return: A tuple (address, unit, metadata)
    :rtype: tuple
    """
    sequence = transaction['vin'][0]['sequence']

    # Find the address that funded this transaction
    prev_tx = self.rpc.get_transaction(transaction['vin'][0]['txid'])

    vout_n = transaction['vin'][0]['vout']
    utxo = prev_tx['vout'][vout_n]

    if len(transaction['vout']) < 2:
      # init transactions always have two outputs
      return

    op_return = transaction['vout'][1]['scriptPubKey']

    if op_return['type'] != 'nulldata':
      # second output should be OP_RETURN data
      return

    election_meta = bytearray.fromhex(op_return['hex'][4:]).decode()
    election_address = utxo['scriptPubKey']['addresses'][0]
    election_unit = self.decode_vote_value(floor(sequence/256) % 256)

    return Election(
      time=block['time'],
      block=block['height'],
      txid=transaction['txid'],
      address=election_address, 
      unit=election_unit, 
      metadata=election_meta
    )


  def read_issue_tx(self, block, transaction):
    """Decode an issuing transaction.

    Currently the colorvote module only supports one input for issuing
    transactions although the protocol is more general (need to fix)

    :param transaction: A transaction as returned by the \
    ``decoderawtransaction`` wallet command
    :type transaction: dict

    :return: A list of tuples (election, address, txid, n, votes)
    :rtype: list
    """

    # Find the address that funded this transaction
    prev_tx = self.rpc.get_transaction(transaction['vin'][0]['txid'])

    vout_n = transaction['vin'][0]['vout']
    utxo = prev_tx['vout'][vout_n]

    election_address = utxo['scriptPubKey']['addresses'][0]

    election_info = self.db.get_election(election_address)

    if not election_info:
      # Not a valid election
      # return None
      print('ok')

    outputs = []

    # Put all vote outputs in list while not exceeding input amount
    for output in transaction['vout']:
      if output['scriptPubKey']['type'] == 'pubkeyhash':
        address = output['scriptPubKey']['addresses'][0]
        # Issuer can't issue votes to himself
        if address != election_address:
          outputs.append(Transaction(
            time=block['time'],
            block=block['height'],
            election=election_address,
            txtype='issue',
            address=address, 
            txid=transaction['txid'],
            n=output['n'],
            input_txid=None,
            input_vout=None,
            amount=output['value']
          ))

      if sum([out.amount for out in outputs]) > utxo['value']:
        outputs.pop()
        break

    return outputs


  def read_transfer_tx(self, block, transaction):
    """Decode a transfer transaction.

    Currently the colorvote module only supports one input for transfer
    transactions although the protocol is more general (need to fix)

    :param transaction: A transaction as returned by the \
    ``decoderawtransaction`` wallet command
    :type transaction: dict

    :return: A tuple (address, unit, metadata)
    :rtype: tuple
    """
 
    # Find the address that funded this transaction
    txid = transaction['vin'][0]['txid']
    n = transaction['vin'][0]['vout']

    prev_tx = self.db.get_transaction(txid, n)

    election_info = self.db.get_election(prev_tx['election'])

    if not election_info:
      # Not a valid election
      # return None
      print('ok')

    outputs = []

    # Put all vote outputs in list while not exceeding input amount
    for output in transaction['vout']:
      if output['scriptPubKey']['type'] == 'pubkeyhash':
        address = output['scriptPubKey']['addresses'][0]
        outputs.append(Transaction(
          time=block['time'],
          block=block['height'],
          election=prev_tx['election'],
          txtype='transfer',
          address=address, 
          txid=transaction['txid'],
          n=output['n'],
          input_txid=prev_tx['txid'],
          input_vout=prev_tx['n'],
          amount=output['value']
        ))

      if sum([out.amount for out in outputs]) > prev_tx['amount']:
        outputs.pop()
        break

    return outputs


  def is_db_synced(self):
    """Returns whether the database is up to date with latest blocks.
    """
    height = int(self.db.get_setting('height'))

    blocks = self.rpc.execute('getinfo')['blocks']

    return blocks == height


  def get_unspent():
    """Returns a list of unspent outputs from the wallet that have voting coins.
    """

    return

  def get_elections():
    """Returns a list of elections that have been found on the blockchain.
    """

    return

  def get_election():
    """Returns the current status of an election including number of votes.
    """

    return


  def generate_key(self):
    """Returns a randomly generated 256-bit integer.
    """
    return

  def create_commitment(self, key, message):
    """Returns a commitment for the given message based on the key.
    """
    return


