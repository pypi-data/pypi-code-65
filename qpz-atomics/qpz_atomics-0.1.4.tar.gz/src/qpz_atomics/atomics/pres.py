class Pres:
    def __init__(self, _):
        def qotp(block, key):
            """
            Quantum One Time Pad Encryption/Decryption

            Qubit Iterable -> Integer Iterable -> Qubit Iterable

            Applies Quantum One Time Pad to an iterable of qubits and a iterable of ints  in 0..3 (0=I, 1=X, 2=Z, 3=Y). 
            Returns an iterable of qubits.
            Needs X,Y,Z operations.

            Tests: 
              - operation is self inverse 
              - output states are random
            """

            for q, k in zip(block, key):
                if k == 0: pass
                if k == 1: _.X(q)
                if k == 2: _.Z(q)
                if k == 3: _.Y(q)
                yield q

        self.qotp = qotp
