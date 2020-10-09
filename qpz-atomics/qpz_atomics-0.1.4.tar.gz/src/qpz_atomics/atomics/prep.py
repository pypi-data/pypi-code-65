from functools import reduce

class Prep:
    def __init__(self, _): 
        def pauli(bit, base):
            """
            bit in 0,1 -> base in 1=X,2=Z,3=Y -> qubit in basis = base with value = bit
            Prepares a qubit in a Pauli eigenstate defined by a bit value (0 for +1 eigenvalue, 1 for -1 eigenvalue) and an integer 1,2,3 corresponding to the Pauli operator selected.
            """
            if base == 1: 
                if bit == 0 : q = _.H(_.PREP())
                elif bit == 1 : q = _.H(_.X(_.PREP()))
            elif base == 2: 
                if bit == 0 : q = _.PREP()
                elif bit == 1 : q = _.X(_.PREP())
            elif base == 3: 
                if bit == 0 : q = _.K(_.PREP())
                elif bit == 1 : q = _.K(_.X(_.PREP()))
            else: raise NameError(f"""Cannot prepare this state: basis must be 1=X, 2=Z or 3=Y. Currently:  {m}""")
            return q

        def ghz(nb_target_nodes):
            """
            nb_target_nodes -> array of qubits
            Prepares an n-party GHZ state
            """
            def add_one_qubit(q):
                __, r = _.CNOT(q, _.PREP())
                return r

            q = _.H(_.PREP())

            return [q] + [add_one_qubit(q) for _ in range(nb_target_nodes)]

        def equatorial(pi_over_4_multiple):
            """
            pi_over_4_multiple -> qubit
            Prepares a qubit in $Z(theta) \ket{+}$ where theta is a $\pi/4$ multiple
            """
            return reduce(lambda a, c: _.T(a), range(pi_over_4_multiple % 8), _.H(_.PREP())) 

        self.pauli = pauli
        self.equatorial = equatorial
        self.ghz = ghz
