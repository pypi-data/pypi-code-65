import itertools

import .qubo


class FileFormatException(Exception):
    pass


class MarkovQUBO(QUBO):
    pass # TODO

    # make specific encoding invisible to user

    def decode_state(self, solution):
        pass # TODO

    def encode_state(self, state):
        pass # TODO

    def random_state(self):
        """
        Generate random encoded state; can be used for
        fixing variables for the WISH algorithm.
        """
        pass # TODO



def __tokens(filename):
    """
    Tokenize file by splitting at whitespaces and linebreaks.
    """
    with open(filename, 'r') as f:
        for line in f:
            for token in line.split():
                yield token.strip()


def fromUAI(filename, encoding='optimal'):
    """
    Create MarkovQUBO object from a .UAI file containing a Markov model.

        :filename: name of file containing Markov model in UAI format
        :encoding: Possible values are 'parameter', 'variable' and 'optimal'
    """

    # tokenize file contents, ignoring spaces and newlines
    ts = __tokens(filename)

    if next(ts) != 'MARKOV':
        raise FileFormatException('File does not start with \'MARKOV\' keyword')

    n      = int(next(ts))
    states = list(map(int, itertools.islice(ts, None, n)))
    
    n_cliques = int(next(ts))
    cliques   = []
    for i in range(n_cliques):
        size = int(next(ts))
        cliques.append(tuple(map(int, itertools.islice(ts, None, size))))

    tables = []
    for i in range(n_cliques):
        table_size = int(next(ts))
        table = np.fromiter(ts, dtype=np.float64, count=table_size)
        table.reshape((states[k] for k in cliques[i]))
        tables.append(table)

    # TODO: Create MarkovQUBO instance, optimally without saving all the
    #       tables in the previous step..
    raise NotImplementedError()
