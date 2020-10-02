import requests
import json

class RPC(object):
  """This is an interface class for talking to a wallet with JSON RPC.
  """
  def __init__(self, username, password, port=14242, host='localhost'):
    """
    :param username: Username for RPC interface
    :type username: str
    :param password: Password for RPC interface
    :type password: str
    :param port: Port for RPC interface, default is 14242
    :type port: int, optional
    :param host: Host for RPC interface, default is localhost
    :type host: str, optional
    """
    self.session = requests.Session()
    self.headers = {'content-type': 'text/plain'}
    self.url = "http://{}:{}@{}:{}".format(username, password, host, port)

  def execute(self, cmd, params = []):
    """Send a command to the wallet.

    :param cmd: The command to execute
    :type cmd: str
    :param params: A list of arguments for the command, default is empty
    :type params: list, optional

    :return: The result returned by the wallet.
    :rtype: str
    """
    payload = {"method": cmd, "jsonrpc": "1.0", "params": params}

    response = self.session.post(self.url, headers=self.headers, 
      data=json.dumps(payload))
    responseJSON = response.json()

    return responseJSON['result']

  def get_transaction(self, txid):
    """Get a decoded transaction by ID.

    :param txid: The transaction ID
    :type txid: str

    :return: A decoded transaction as returned by ``decoderawtransaction``
    """
    raw = self.execute("getrawtransaction", [txid])
    tx = self.execute("decoderawtransaction", [raw])

    return tx

  def send_transaction(self, params):
    """Sign and send a transaction to the blockchain.

    :param params: A list [inputs, outputs] of the parameters as accepted by \
    the createrawtransaction wallet command.
    :type params: list

    :return: The txid of the transaction that was sent.
    :rtype: str
    """

    tx = self.execute("createrawtransaction", params)
    signed = self.execute("signrawtransaction", [tx])
    txid = self.execute("sendrawtransaction", [signed['hex']])
 
    return txid

