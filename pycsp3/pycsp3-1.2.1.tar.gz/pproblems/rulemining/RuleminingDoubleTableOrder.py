
# Rule mining problem (partial classification): A solution is a matrix s[i][j] that represents a disjunction of rules. Each line "i" is a rule and represents a conjunction of terms. Hence, each position "j" is a term and is associated to the attribute of the position "j" of the table called attributes. Note also that we fix the number of term to the number of attributs. Several heuristics allow to measure the quality of solutions. In this model, our objective is to maximize the number of both True Positive and True Negative individuals. When the solver found a solution, we calculate the F-mesure of the solution (decimal between [0, 1]). The closer the f-measurement of the solution is to 1, the better the solution is. 

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
s = VarArray(size=[max_rules, max_terms_per_rule], dom=lambda i, j: set(range(len(attributes[j].values))))

# s_order(r)(t) 0: not used - EQ:1: == - LT:2: > - GT:3: <  
s_order = VarArray(size=[max_rules, max_terms_per_rule], dom={-1, EQ, LT, GT})

# p(i,r,t) == 1 if the individual i satisfies the term t of the rule r 
p = VarArray(size=[nb_individuals, max_rules, max_terms_per_rule], dom={0, 1})

# p_rules(i,r) is the number of term to 1 for the individual i and the rule r 
p_rules = VarArray(size=[nb_individuals, max_rules], dom={0,1})

# check(i) == 1 if the individual i satisfies any rule
p_check = VarArray(size=nb_individuals, dom={0,1})

# True positive (solution says positive and the individual is positive)
tp = Var(dom=range(nb_individuals))

# False positive (solution says positive but the individual is negative)
fp = Var(dom=range(nb_individuals))


def score_positive_table():
    return [(0,1),(1,0)]

def score_negative_table():
    return [(0,0),(1,1)]

# (p[id_individual, id_rule, id_term], s_order[id_rule, id_term], s[id_rule, id,term])
def create_table_p(t, id_individual, id_rule, id_term):
    table = []
    table.append((1, -1, ANY)) #Case -1
    table.append((1, EQ, t[id_individual][id_term])) #Case ==
    table.append((1, LT, lt(t[id_individual][id_term]))) #Case <
    table.append((1, GT, gt(t[id_individual][id_term]))) #Case >
    table.append((0, EQ, ne(t[id_individual][id_term])))
    table.append((0, LT, ge(t[id_individual][id_term])))
    table.append((0, GT, le(t[id_individual][id_term])))
    return table

# (p_rules[i][r], p[i][r]) for the conjunction, (p_check[i], p_rules[i]) for disjunction 
def create_table_of_intension(conjunction=True):
    table=[]
    value = 1 if conjunction else 0
    opposite_value = 0 if conjunction else 1
    nb_elements = max_terms_per_rule if conjunction else max_rules
    table.append((value,)*(nb_elements+1))
    for i in range(nb_elements):
        new_t = [opposite_value]
        for j in range(nb_elements):
            new_t.append(opposite_value if j == i else ANY)
        table.append(tuple(new_t))
    return table

print(create_table_of_intension())
print(create_table_of_intension(False))
print((p_check[0], p_rules[0]))

satisfy(
    #LexIncreasing(s, strict=True),

    [Count(s_order[r], value=-1) < max_terms_per_rule for r in range(max_rules)],

    # Link the solution and p(i,r,t)
    [(p[i][r][t], s_order[r][t], s[r][t]) in create_table_p(individuals, i, r, t) for i in range(nb_individuals) for r in range(max_rules) for t in range(max_terms_per_rule)],

    # Conjunction of rule for positive individual
    #[iff(conjunction(p[i][r]) == 1, p_rules[i][r] == 1) for i in range(nb_individuals) for r in range(max_rules)],

    [(p_rules[i][r], p[i][r]) in create_table_of_intension() for i in range(nb_individuals) for r in range(max_rules)],

    [(p_check[i], p_rules[i]) in create_table_of_intension(False) for i in range(nb_individuals)],

    
    # TP
    Count([p_check[i] for i in range(nb_individuals) if class_individuals[i] == 1], value=1) == tp,

    # TP
    Count([p_check[i] for i in range(nb_individuals) if class_individuals[i] == 0], value=1) == fp


)

maximize(
    tp + nb_negative_individuals - fp
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
                order = solution.values[index_order + index]
                
                if int(order) != -1:
                    if int(order) == EQ:
                        and_for_terms.append(int(individual[term]) == int(sol))
                    elif int(order) == LT:
                        print("HERE:", int(sol), int(individual[term]))
                        and_for_terms.append(int(sol) < int(individual[term]))
                    
                    elif int(order) == GT:
                        and_for_terms.append(int(sol) > int(individual[term]))
                    else:
                        print("error: " + order + " not possible")
                        exit(0)
                index = index + 1
            print(and_for_terms)
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
            attr = attributes[term]
            isol = int(sol)
            sol = attr.values[int(sol)]
            order = solution.values[index_order + index]
            if int(order) != -1:
                if int(order) == EQ:
                    str_order = "="
                elif int(order) == LT:
                    str_order = ">"
                elif int(order) == GT:
                    str_order = "<"
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
print(solution)

tp, tn, fp, fn = check_solution_order()
print(solution)

print(print_solution_order())

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

