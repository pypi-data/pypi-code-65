from pycsp3 import *
from pycsp3.solvers.abscon import AbsConProcess

#python3 g7_todo/Rulemining.py -dataparser=g7_todo/Rulemining_Parser.py g7_todo/instances_rulemining/ecoli1d/ecoli1d.desc g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.training g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.test

attributes, prediction, individuals = data

positive_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 0] 
negative_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 1] 
individuals = [tuple(element) for element in individuals]

nb_attributes = len(attributes)-1
nb_individuals = len(positive_individuals) + len(negative_individuals)

# Rule mining problem (partial classification) A solution is a matrix [i][j] that represents a conjonction of rules. Each line "i" is a rule and represents a disjontion of terms. Each position "j" of a term is associated to a attribut of the position "j" in the table attributes.  
# Note also that we fix the number of term to the number of attributs

max_rules = 2
max_terms_per_rule = nb_attributes
max_terms = max_rules * max_terms_per_rule
nb_operators = 3 # TODO For later

print()
print("Modeling ...")


print("Number of attributes: ", nb_attributes)
print("Number of individuals: ", nb_individuals)
print("Number of positive individuals: ", len(positive_individuals))
print("Number of negative individuals: ", len(negative_individuals))

print("Max rules : ", max_rules)
print("max_terms_per_rule : ", nb_attributes)
print("max_terms: ", max_terms)
print("nb_operators: ", nb_operators)

#print(attributes)
print(positive_individuals)

# TODO the character " in the comment lines is incorrectly displayed in the xcsp3 file (xml file)

# the solution: a matrix [i][j] that represents a conjonction of rules. Each line "i" is a rule and represents a disjontion of terms.
s = VarArray(size=[max_rules, max_terms_per_rule], dom=lambda i, j: set(range(len(attributes[j].values))) | {-1})

# matrix of positive individuals in relation to the solution 
positive_matrix = VarArray(size=[max_rules, len(positive_individuals), nb_attributes], dom={0,1})

# the number of variables not used in the solution
nb_not_used = VarArray(size=max_rules, dom=range(max_terms+1))

# matrix i, j: Represent the number if the individuals j is positive for the rule i 
tp_individual = VarArray(size=[max_rules, len(positive_individuals)], dom=range(len(attributes)))

tp_individual_or = VarArray(size=[max_rules, len(positive_individuals)], dom={0,1})

tp_individual_all_rules = VarArray(size=len(positive_individuals), dom=range(max_terms))

tp = Var(dom=range(len(positive_individuals)+1))

satisfy(
    # Ensure that the rules are differents
    [AllDifferent([s[i][j] for i in range(max_rules)], excepting=-1) for j in range(nb_attributes)],

    # Count the number of variables not used in the solution
    [Count(s[i], value=-1) == nb_not_used[i] for i in range(max_rules)],

    # Constraint on the number of variable not used
    [nb_not_used[i] < 7 for i in range(max_rules)],

    # Link the solution and the positive_matrix
    [iff(positive_individuals[i][j] == s[k][j], positive_matrix[k][i][j] == 1) 
    for i in range(len(positive_individuals)) for j in range(nb_attributes) for k in range(max_rules)],

    # Force the number of value >= 1 for each positive individual (or operator)
    #[Count(positive_matrix[k][i], value=1) >= 2 for i in range(len(positive_individuals)) for k in range(max_rules)],
    #May be Clause() for this one ?

    # Link positive_matrix[k][i][j] and tp_individual
    [Count(positive_matrix[k][i], value=1) == tp_individual[k][i] for k in range(max_rules) for i in range(len(positive_individuals))],

    [iff(tp_individual[k][i] >= 1, tp_individual_or[k][i] == 1) for k in range(max_rules) for i in range(len(positive_individuals))],

    [Count([tp_individual_or[i][j] for i in range(max_rules)], value=1) == tp_individual_all_rules[j] for j in range(len(positive_individuals))],

    Count(tp_individual_all_rules, value=max_rules) == tp
)

maximize(Sum(tp, nb_not_used))

instance = compile()

solution = AbsConProcess().solve(instance, "[limit=10s]")

print("solution:")

print(solution)

nb_sols = max_rules * nb_attributes
solution_str = ""
index = 0
print()
for rule in range(max_rules):
    for term in range(nb_attributes):
        
        sol = solution.values[index]

        #print(sol, index, term)
        if sol != "-1":
            attr = attributes[term]
            sol = attr.values[int(sol)]
            solution_str += " " + str(term) + " " + attr.name + " = " + sol
        index = index + 1
    solution_str += "\n"
print(solution_str)


