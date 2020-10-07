#/usr/bin/python

import numpy
import matplotlib.pyplot as plt

nb_correction = numpy.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])

der=dict()
der["ref"] = dict()
der["bic"] = dict()

der['ref']["ideal"] = numpy.array([0.34, 0.34, 0.34,0.34,0.34,0.51,0.86,1.33,1.74,2.21])
der['ref']["min"] = numpy.array([1.96,1.91,1.9,1.9,1.9,2.07,2.38,2.83,3.11,3.57])
der['ref']["max"] = numpy.array([4.03,3.57,3.3,2.9,2.52,1.92,1.39,1.89,2.23,2.74])
der['ref']["mean"] = numpy.array([3.05,3.05,2.44,2.11,1.65,1.4,1.44,1.92,2.24,2.69])

der['bic']["ideal"] = numpy.array([12.16,12.18,12.22,12.28,12.37,12.47,12.58,12.71,12.81,13.06])
der['bic']["min"] = numpy.array([13.1,13.03,13.06,13.1,13.15,13.24,13.37,13.48,13.61,13.81])
der['bic']["max"] = numpy.array([13.07,13.01,13.04,12.81,12.89,13.08,13.17,13.03,13.11,13.39])
der['bic']["mean"] = numpy.array([12.62,12.55,12.57,12.86,12.94,13.04,13.14,13.15,13.3,13.46])


plt.plot(nb_correction, der['ref']["ideal"])