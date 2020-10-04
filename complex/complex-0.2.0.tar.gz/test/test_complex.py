from complex import Complex

def test_complex():
	x, y = Complex(2, 1), Complex(5, 6)
	su, sub, mul, div, mod_x, mod_y, x_angle, y_angle, x_conjugate, y_conjugate, x_log, y_log = x+y, x-y, x*y, x/y, x.mod(), y.mod(), x.angle(), y.angle(), x.conjugate(), y.conjugate(), x.log(), y.log()
	assert su.__str__() == '7.00+7.00i'
	assert sub.__str__() == '-3.00-5.00i'
	assert mul.__str__() == '4.00+17.00i'
	assert div.__str__() == '0.26-0.11i'
	assert mod_x.__str__() == '2.24+0.00i'
	assert mod_y.__str__() == '7.81+0.00i'
	assert x_angle.__str__() == '0.4636476090008061'
	assert y_angle.__str__() == '0.8760580505981934'
	assert x_conjugate.__str__() == '2.00-1.00i'
	assert y_conjugate.__str__() == '5.00-6.00i'
	assert x_log.__str__() == '0.80+0.46i'
	assert y_log.__str__() == '2.06+0.88i'






