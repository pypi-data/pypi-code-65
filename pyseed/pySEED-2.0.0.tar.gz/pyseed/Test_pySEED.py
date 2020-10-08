"""
PySEED-EDA was created by Valentín Calzada-Ledesma and Juan de Anda-Suárez

How to cite:
J. De Anda-Suárez et al., "Symmetric-Approximation Energy-Based Estimation of Distribution (pySEED):
A Continuous Optimization Algorithm," in IEEE Access, vol. 7, pp. 154859-154871, 2019,
doi: 10.1109/ACCESS.2019.2948199.
"""

import pySEED
from Benchmark_functions import Sphere, Rosenbrock, Rastrigin, Ackley, Griewangk

# Parameters
population_size = 300
dimensions = 200
lower_limit = -10
upper_limit = 5
fitness_function = Sphere()
stopping_criterion = 1E-6
iterations = 1000

# Evolutionary process
SEED = pySEED.SEED_EDA(population_size, dimensions, lower_limit, upper_limit,
                       fitness_function, 1E8 - stopping_criterion, print_evolution=True)
Individuals = SEED.evolution(iterations)


'''
The pySEED-algorithm was designed to deal with maximization problems. For the minimization case, the
stopping criterion must be transformed using the next operation: 1E8 - stopping_criterion

In order to perform statistical analysis, the Optimize.evolution() method is able to return a list of the 
best-evolved individuals at each iteration. If you want to get the individual.chromosome and its corresponding 
fitness value, simply use the next code: 

for individual in Individuals:
    print("Chromosome:", individual.chromosome, "Fitness value:", 1E8 - individual.fitness_value)

Note that the pySEED-algorithm returns fitness values computed for the maximization case. So, in order to get the 
fitness values for a minimization case, those must be transformed using the next operation: 
1E8 - individual.fitness_value
'''
