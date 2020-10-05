from qubovert.utils import QUBOMatrix

class QUBOMatrixStack:

    def __init__(self, max_variables=2048):
        self.quboMatrices = []
        self.max_variables = max_variables
        self.total_size = 0
        self.scales = []
        
    def stack(self, Q, scale=1.0):
        n = Q.max_index+1
        if self.total_size + n > self.max_variables:
            raise Exception(f'Cannot stack QUBOMatrix: Max. of {self.max_variables} variables exceeded!')
        
        self.quboMatrices.append(Q)
        self.total_size += n
        self.scales.append(scale)
        
    def unify(self):
        Q = QUBOMatrix()
        
        offset = 0
        for R in self.quboMatrices:
            for ij, w in R.items():
                offset_ij = tuple(map(lambda x: x+offset, ij))
                Q[offset_ij] = w
            offset += R.max_index+1
        
        return Q
    
    @property
    def num_binary_variables(self):
        return sum(Q.max_index+1 for Q in self.quboMatrices)
    
    def values(self, solution):
        values = []
        offset = 0
        for ix, Q in enumerate(self.quboMatrices):
            n = Q.max_index+1
            values.append(evaluate(Q, { i-offset: int(solution[i]) for i in range(offset, offset+n) }) / self.scales[ix])
            #values.append(Q.value({ i-offset: int(solution[i]) for i in range(offset, offset+n) }) / self.scales[ix])
            offset += n
            
        return values
    
    def clear(self):
        self.quboMatrices = []
        self.total_size = 0
        self.scales = []
