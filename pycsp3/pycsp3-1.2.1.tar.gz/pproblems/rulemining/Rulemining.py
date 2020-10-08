from pycsp3 import *
from pycsp3.solvers.abscon import AbsConProcess

#python3 g7_todo/Rulemining.py -dataparser=g7_todo/Rulemining_Parser.py g7_todo/instances_rulemining/ecoli1d/ecoli1d.desc g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.training g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.test

attributes, prediction, individuals = data

positive_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 0] 
negative_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 1] 
nb_attributes = len(attributes)-1
nb_individuals = len(positive_individuals) + len(negative_individuals)

#print(attributes)
#print(positive_individuals)

max_rules = 10
max_terms = 9

print()
print("Modeling ...")
print("Number of attributes: ", nb_attributes)
print("Number of individuals: ", nb_individuals)
print("Number of positive individuals: ", len(positive_individuals))
print("Number of negative individuals: ", len(negative_individuals))

individuals = [tuple(element) for element in individuals]

# solution 
s = VarArray(   size=nb_attributes, 
                dom=[list(range(len(attribute.values)))+[-1] for attribute in attributes[:-1]])

# matrix of positive individuals in relation to the solution
positive_matrix = VarArray(size=[len(positive_individuals), nb_attributes], dom={0,1})

tp_individuals = VarArray(size=len(positive_individuals), dom=range(nb_attributes+7))

tp = Var(dom=range(len(positive_individuals)+100))

nb_not_used = Var(dom=range(nb_attributes+1))

satisfy(
    # Count the number of variable not used in the solution
    Count(s, value=-1) == nb_not_used,   

    # Constraint on the number of variable not used
    nb_not_used < 6,

    # Link the solution and the positive_matrix
    [iff((positive_individuals[i][j] == s[j]) | (s[j] == -1), positive_matrix[i][j] == 1) 
    for i in range(len(positive_individuals)) for j in range(nb_attributes)],
    
    # Count the number of value to 1 for each positive individual and store it in tp_individuals
    [Count(positive_matrix[i], value=1) == 1 for i in range(len(positive_individuals))],
    
    # Count the number of individual in tp_individuals with the maximal value (nb_attributes)
    Count(tp_individuals, value=nb_attributes) == tp
)

maximize(Sum(tp, nb_not_used))

instance = compile()

solution = AbsConProcess().solve(instance)

print("solution:")

print(solution)

solution_str = ""
for i, sol in enumerate(solution.values[:7]):
    if sol != "-1":
        attr = attributes[i]
        sol = attr.values[int(sol)]
        solution_str += " " + str(i) + " " + attr.name + " " + sol

print(solution_str)

# Bug: if -solve + AbsConProcess().solve then the instance is solved twice