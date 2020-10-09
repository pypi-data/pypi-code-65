class Gate:
    def __init__(self, _):
        def CZ(c,t):
            """
            Control-Z gate implementation from CNOT
            qubit -> qubit -> (qubit, qubit)
            first qubit is control
            second is target
            return tuple (control, target)
            """
            _.H(t)
            _.CNOT(c,t)
            _.H(t)
            return (c,t)

        def CSWAP(q0, q1, q2):        
            """
            Control SWAP on two qubits q1 and q2, q0 is the control qubit.
            Implementation from https://www.mathstat.dal.ca/~selinger/quipper/doc/Quipper-Libraries-GateDecompositions.html
            params : 
            q0,q1,q2: qubits

            """
            _.CNOT(q2,q1)
            _.H(q2)
            _.T(q0)
            _.T(q1)
            _.T(q2)
            _.CNOT(q1,q0)
            _.CNOT(q2,q1)
            _.CNOT(q0,q2)
            _.Tinv(q1)
            _.T(q2)
            _.CNOT(q0,q1)
            _.Tinv(q0)
            _.Tinv(q1)
            _.CNOT(q2,q1)
            _.CNOT(q0,q2)
            _.CNOT(q1,q0)
            _.H(q2)
            _.CNOT(q2,q1)
            return (q0, q1, q2)

        self.CSWAP = CSWAP
        self.CZ = CZ
