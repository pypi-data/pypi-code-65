import math

class Complex(object):
    def __init__(self, real, imaginary):
        self.real = real
        self.imaginary = imaginary
        
    def __add__(self, no):
        return Complex(self.real + no.real, self.imaginary+no.imaginary)
        
    def __sub__(self, no):
        return Complex(self.real - no.real, self.imaginary - no.imaginary)
        
    def __mul__(self, no):
        return Complex(self.real*no.real - 
        self.imaginary*no.imaginary, self.imaginary*no.real + self.real*no.imaginary)

    def __truediv__(self, no):
        num = self*Complex(no.real, -no.imaginary)
        denom = no.real**2+no.imaginary**2
        return Complex(num.real/denom, num.imaginary/denom)

    def mod(self):
        return Complex(math.sqrt(self.real**2 + self.imaginary**2), 0)

    def __str__(self):
        if self.imaginary == 0:
            result = "%.2f+0.00i" % (self.real)
        elif self.real == 0:
            if self.imaginary >= 0:
                result = "0.00+%.2fi" % (self.imaginary)
            else:
                result = "0.00-%.2fi" % (abs(self.imaginary))
        elif self.imaginary > 0:
            result = "%.2f+%.2fi" % (self.real, self.imaginary)
        else:
            result = "%.2f-%.2fi" % (self.real, abs(self.imaginary))
        return result

    def angle(self):
        if self.real == 0 and self.imaginary == 0:
            raise Exception ('The given input is the origin and has no angle')
        if self.real > 0 and self.imaginary == 0:
            return 0
        if self.real == 0 and self.imaginary > 0:
            return math.pi/2
        if self.real < 0 and self.imaginary == 0:
            return math.pi
        if self.real == 0 and self.imaginary < 0:
            return 3*math.pi/2
            
        atan = math.atan(abs(self.imaginary)/abs(self.real))
        
        #quadrant 1
        if 0 < self.real and self.imaginary > 0:
            return atan
        #quadrant 2
        elif 0 > self.real and self.imaginary > 0:
            return (math.pi/2) + atan
        #quadrant 3
        elif 0 > self.real and 0 > self.imaginary:
            return math.pi + atan
        #quardant 4
        elif 0 < self.real and 0 > self.imaginary:
            return -atan

    def conjugate(self):
        return Complex(self.real,-1*self.imaginary)
    
    def log(self):
        return Complex(math.log(self.mod().real),self.angle())