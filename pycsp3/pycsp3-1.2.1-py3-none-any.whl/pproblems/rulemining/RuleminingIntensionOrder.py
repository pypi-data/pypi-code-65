
# Rule mining problem (partial classification): A solution is a matrix s[i][j] that represents a disjunction of rules. Each line "i" is a rule and represents a conjunction of terms. Hence, each position "j" is a term and is associated to the attribute of the position "j" of the table called attributes. Note also that we fix the number of term to the number of attributs. Several heuristics allows to measure the quality of solutions. In this model, our objective is to maximize the number of both True Positive and True Negative individuals. When the solver found a solution, we calculate the F-mesure of the solution (decimal between [0, 1]). The closer the f-measurement of the solution is to 1, the better the solution is. 

#command: python3 pproblems/rulemining/RuleminingIntensionOrder.py -dataparser=pproblems/rulemining/Rulemining_Parser.py pproblems/rulemining/instances/ecoli1d/ecoli1d.desc pproblems/rulemining/instances/ecoli1d/ecoli1d.individuals.1.training pproblems/rulemining/instances/ecoli1d/ecoli1d.individuals.1.test

from pycsp3 import *
from pycsp3.solvers.abscon import AbsConProcess
from itertools import chain, combinations

attributes, prediction, individuals = data

positive_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 0] 
negative_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 1] 
class_individuals = [0 if element[-1] == 1 else 1 for element in individuals]
individuals = [tuple(element[:-1]) for element in individuals]
nb_attributes = len(attributes)-1
nb_individuals = len(positive_individuals) + len(negative_individuals)

max_rules = 2
max_terms_per_rule = nb_attributes
max_terms = max_rules * max_terms_per_rule
nb_positive_individuals = len(positive_individuals)
nb_negative_individuals = len(negative_individuals)
print()
print("Modeling ...")
print("Number of attributes: ", nb_attributes)
print("Number of individuals: ", nb_individuals)
print("Number of positive individuals: ", nb_positive_individuals)
print("Number of negative individuals: ", nb_negative_individuals)

print("Max rules : ", max_rules)
print("max_terms_per_rule : ", nb_attributes)
print("max_terms: ", max_terms)

EQ = 1 # =
LT = 2 # < 
GT = 3 # >

# TODO the character " in the comment lines is incorrectly displayed in the xcsp3 file (xml file)

# s(r)(t) represents a disjunction of rules. Each line r is a rule and represents a conjunction of t terms.
s = VarArray(size=[max_rules, max_terms_per_rule], dom=lambda i, j: set(range(len(attributes[j].values))) | {-1})

# s_order(r)(t) 0: not used - EQ:1: == - LT:2: > - GT:3: <  
s_order = VarArray(size=[max_rules, max_terms_per_rule], dom={LT, EQ, GT})

# p(i,r) == 0 if the positive individual i satisfies the rule r 
p = VarArray(size=[nb_positive_individuals, max_rules], dom={0, 1})

# n(i,r) == 1 if the negative individual i satisfies the rule r 
n = VarArray(size=[nb_negative_individuals, max_rules], dom={0, 1})

# check(i) == 1 if the individual i satisfies any rule
p_check = VarArray(size=nb_positive_individuals, dom={0,1})

# check(i) == 1 if the individual i satisfies any rule
n_check = VarArray(size=nb_negative_individuals, dom={0,1})

# score(i) store if the individual is TP(0), FP(1) 
p_score = VarArray(size=nb_positive_individuals, dom={0,1})

# score(i) store if the individual is TP(0), FP(1) 
n_score = VarArray(size=nb_negative_individuals, dom={0,1})

# True positive
tp = Var(dom=range(nb_individuals))

# True negative
tn = Var(dom=range(nb_individuals))


def score_positive_table():
    return [(0,1),(1,0)]

def score_negative_table():
    return [(0,0),(1,1)]

def create_conjunction(t, id_individual, id_rules):
    conj = []
    for j in range(nb_attributes):
        disj = []
        disj.append(s[id_rules][j] == -1)
        disj.append(conjunction(s_order[id_rules][j] == EQ, s[id_rules][j] == t[id_individual][j]))
        disj.append(conjunction(s_order[id_rules][j] == LT, s[id_rules][j] < t[id_individual][j]))
        disj.append(conjunction(s_order[id_rules][j] == GT, s[id_rules][j] > t[id_individual][j]))
        disj = disjunction(*disj)
        conj.append(disj)
    return conjunction(*conj)
    
satisfy(
    Count(s, value=-1) < (max_rules * max_terms_per_rule),

    # Conjunction of rule for positive individual
    [iff(create_conjunction(positive_individuals, i, r), p[i][r] == 1) for i in range(nb_positive_individuals) for r in range(max_rules)],

    # Conjunction of rule for negative individual
    [iff(create_conjunction(negative_individuals, i, r), n[i][r] == 1) for i in range(nb_negative_individuals) for r in range(max_rules)],


    # An individual check the solution if the disjunction of rules is true with the current solution
    [iff(disjunction(p[i]) == 1, p_check[i] == 1) for i in range(nb_positive_individuals)],

    # An individual check the solution if the disjunction of rules is true with the current solution
    [iff(disjunction(n[i]) == 1, n_check[i] == 1) for i in range(nb_negative_individuals)],

    # Complete score for each individual TP(0), FN(1)
    [(p_score[i], p_check[i]) in score_positive_table() for i in range(nb_positive_individuals)], 

    # Complete score for each individual TN(0), FP(1)
    [(n_score[i], n_check[i]) in score_negative_table() for i in range(nb_negative_individuals)], 

    # TP
    Count(p_score, value=0) == tp,

    # TN
    Count(n_score, value=0) == tn
)

maximize(
    Sum(tp + tn)
)

instance = compile()

solution = AbsConProcess().solve(instance, "limit=60s,v")
#solution = AbsConProcess().solve(instance)


def check_solution_order():
    tp, fp, fn, tn = 0, 0, 0, 0
    for index_individual, individual in enumerate(individuals):
        index = 0
        index_order = max_rules * max_terms_per_rule
        or_for_rules = False
        for rule in range(max_rules):
            and_for_terms = []
            for term in range(nb_attributes):
                sol = solution.values[index]
                if sol != "-1":
                    order = solution.values[index_order + index]
                    if int(order) == EQ:
                        and_for_terms.append(int(individual[term]) == int(sol))
                    elif int(order) == LT:
                        and_for_terms.append(int(sol) < int(individual[term]))
                    elif int(order) == GT:
                        and_for_terms.append(int(sol) > int(individual[term]))
                    else:
                        print("error: " + order + " not possible")
                        exit(0)
                index = index + 1
            if all(and_for_terms):
                or_for_rules = True
                break
        if or_for_rules:
            if class_individuals[index_individual]:
                tp+=1
            else:
                fp+=1
        else:
            if class_individuals[index_individual]:
                fn+=1
            else:
                tn+=1
    return tp, tn, fp, fn 
    

def print_solution_order():
    nb_sols = max_rules * nb_attributes
    solution_str = ""
    index = 0
    index_order = max_rules * max_terms_per_rule
    print()
    for rule in range(max_rules):
        solution_str += "Rule number " + str(rule) + ":\n"
        for term in range(nb_attributes):
            sol = solution.values[index]
            if sol != "-1":
                attr = attributes[term]
                isol = int(sol)
                sol = attr.values[int(sol)]
                order = solution.values[index_order + index]
                if int(order) == EQ:
                    str_order = "="
                elif int(order) == LT:
                    str_order = "<"
                elif int(order) == GT:
                    str_order = ">"
                else:
                    print("error: " + order + " not possible")
                    exit(0)
                solution_str += " " + attr.name + " " + str_order + " " + sol + " (" + str(term) + " " + str_order + " " + str(isol) + ")"
            index = index + 1
        solution_str += "\n"
    return solution_str
    print("solution:")
    print(solution_str)

def sensitivity(tp, tn, fp, fn):
    return tp / (tp + fn)

def confidence(tp, tn, fp, fn):
    return tp / (tp + fp)

def fmeasure(s, c):
    return (2 * c * s) / (c + s)

tp, tn, fp, fn = check_solution_order()

print("tp:", tp)
print("tn:", tn)
print("fp:", fp)
print("fn:", fn)
s = sensitivity(tp, tn, fp, fn)
c = confidence(tp, tn, fp, fn)
f = fmeasure(s, c)
print("sensitivity:", s)
print("confidence:", c)
print("fmeasure:", f)

print(print_solution_order())
print(solution)
