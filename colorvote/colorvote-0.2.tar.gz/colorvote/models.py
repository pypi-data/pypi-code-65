from collections import namedtuple

Election = namedtuple('Election', ['time', 'block', 'txid', 'address', 'unit',
  'metadata'])

Transaction = namedtuple('Transaction', ['time', 'block', 'election', 'txtype',
  'address', 'txid', 'n', 'input_txid', 'input_vout', 'amount'])


