"""
PySEED-EDA was created by Valentín Calzada-Ledesma and Juan de Anda-Suárez

How to cite:
J. De Anda-Suárez et al., "Symmetric-Approximation Energy-Based Estimation of Distribution (pySEED):
A Continuous Optimization Algorithm," in IEEE Access, vol. 7, pp. 154859-154871, 2019,
doi: 10.1109/ACCESS.2019.2948199.
"""

import math
import numpy as np


class SEED_EDA:
    def __init__(self, n, dimension, lower_limit, upper_limit, fitness_function, criterion, print_evolution):
        self.n = n
        self.dimension = dimension
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.fitness_function = fitness_function
        self.criterion = criterion
        self.population = []
        self.best_evolved = []
        self.selected = None
        self.best = None
        self.mu = []
        self.nu = []
        self.teta = None
        self.t = None
        self.print_evolution = print_evolution

    def evolution(self, generations):
        print("Here comes the Evolution...")
        self.initialize_population()
        self.best = self.population[0]
        if self.print_evolution:
            print("i: 0", " Fitness value:", 1E8 - self.best.fitness_value)

        for i in range(generations):
            self.t = i
            self.selection_method()
            self.compute_mu_nu()
            self.sample_new_population()

            if self.best.fitness_value >= self.population[0].fitness_value:
                self.population[0] = self.best
            self.best_evolved.append(self.population[0])
            self.best = self.population[0]
            if self.print_evolution:
                print("i:", i + 1, " Fitness value:", 1E8 - self.best.fitness_value)
            if self.population[0].fitness_value >= self.criterion:
                break
        return self.best_evolved

    def initialize_population(self):
        for i in range(self.n):
            individual = Individual(self.fitness_function)
            individual.initialize(self.lower_limit, self.upper_limit, self.dimension)
            individual.evaluate()
            self.population.append(individual)
        self.population.sort(key=lambda f: f.fitness_value, reverse=True)

    def selection_method(self):
        if self.t == 0:
            self.teta = self.population[-1]
        else:
            population_aux = [ind for ind in self.population if ind.fitness_value >= self.teta.fitness_value]
            g_min = population_aux[-1]
            g_mid = self.population[round(self.n / 2) - 1]
            if g_min.fitness_value >= g_mid.fitness_value:
                self.teta = g_min
            else:
                self.teta = g_mid
        self.selected = [ind for ind in self.population if ind.fitness_value >= self.teta.fitness_value]

    def compute_mu_nu(self):
        best_fitness = self.selected[0].fitness_value
        worst_fitness = self.selected[-1].fitness_value
        m = len(self.selected)
        a = self.lower_limit
        b = self.upper_limit
        sum_exp_beta_gx = 0
        sum_exp_beta_gx_xi = 0
        sum_gx_xi = 0
        sum_gx = 0
        for ind in self.selected:
            hx = ind.fitness_value - worst_fitness + 1
            sum_exp_beta_gx += math.exp((1 / best_fitness) * hx)
            sum_exp_beta_gx_xi += math.exp((1 / best_fitness) * hx) * ind.chromosome
            sum_gx_xi += hx * ind.chromosome
            sum_gx += hx
        Z = m / ((b - a) * sum_exp_beta_gx)
        self.mu = (1 / Z * (1 / best_fitness) * sum_exp_beta_gx_xi + sum_gx_xi) / \
                  ((m / ((1 / best_fitness) * (b - a))) + sum_gx)
        sum_exp_beta_gx_xi_mu_2 = 0
        sum_gx_xi_mu_2 = 0
        for ind in self.selected:
            hx = ind.fitness_value - worst_fitness + 1
            sum_exp_beta_gx_xi_mu_2 += math.exp((1 / best_fitness) * hx) * ((ind.chromosome - self.mu) ** 2)
            sum_gx_xi_mu_2 += hx * ((ind.chromosome - self.mu) ** 2)
        self.nu = (1 / Z * (1 / best_fitness) * sum_exp_beta_gx_xi_mu_2 + sum_gx_xi_mu_2) / sum_gx

    def sample_new_population(self):
        self.population.clear()
        for i in range(self.n):
            individual = Individual(self.fitness_function)
            individual.chromosome = np.random.normal(self.mu, np.sqrt(self.nu), self.dimension)
            individual.evaluate()
            self.population.append(individual)
        self.population.sort(key=lambda f: f.fitness_value, reverse=True)


class Individual:
    def __init__(self, fitness_function):
        self.fitness_function = fitness_function

    def initialize(self, lim_inf, lim_sup, dimension):
        self.chromosome = np.random.uniform(lim_inf, lim_sup, size=dimension)

    def evaluate(self):
        self.fitness_value = self.fitness_function.evaluate(self.chromosome)