class Meas:
    def __init__(self, _): 
        def pauli(qubit, base):
            """
            qubit -> base in 1=X,2=Z,3=Y -> bit: measurement result
            """
            if base == 1: m = _.MEAS(_.H(qubit))
            elif base == 2: m = _.MEAS(qubit)
            elif base == 3: m = _.MEAS(_.K(qubit))
            else: raise NameError(f"""Cannot prepare this state: basis must be 1=X, 2=Z or 3=Y. Currently:  {m}""")
            return m

        def equatorial(qubit, pi_over_4_multiple):
            """
            qubit -> pi/4 multiple -> bit 
            Measures a qubit in the equatorial plane at angles multiple of pi over 4.
            """
            return _.MEAS(_.H(reduce(lambda a, c: _.Tinv(a), range(pi_over_4_multiple %8), qubit)))
        
        self.pauli = pauli

        
