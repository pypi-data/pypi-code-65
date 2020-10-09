class Test:
    def __init__(self, _):
        def swap(q1, q2):

            """
            launch the swap test
            params:
                q1, q2: iterable of qubits

            """

            q=zip(q1,q2)
            q0 = _.PREP()
            _.H(q0)

            for q1,q2 in q:
                _.gate_CSWAP(q0, q1, q2)
                print(_.MEAS(q1), _.MEAS(q2))

            _.H(q0)
            m = _.MEAS(q0)

            print ('q0 measure is ', m)

            return m

        self.swap = swap
