
# Rule mining problem (partial classification): A solution is a matrix s[i][j] that represents a disjunction of rules. Each line "i" is a rule and represents a conjunction of terms. Hence, each position "j" is a term and is associated to the attribute of the position "j" of the table called attributes. Note also that we fix the number of term to the number of attributs. Several heuristics allow to measure the quality of solutions. In this model, our objective is to maximize the number of both True Positive and True Negative individuals. When the solver found a solution, we calculate the F-mesure of the solution (decimal between [0, 1]). The closer the f-measurement of the solution is to 1, the better the solution is. 

#command: python3 pproblems/rulemining/RuleminingIntensionOrder.py -dataparser=pproblems/rulemining/Rulemining_Parser.py pproblems/rulemining/instances/ecoli1d/ecoli1d.desc pproblems/rulemining/instances/ecoli1d/ecoli1d.individuals.1.training pproblems/rulemining/instances/ecoli1d/ecoli1d.individuals.1.test

from pycsp3 import *
from pycsp3.solvers.abscon import AbsConProcess
from itertools import chain, combinations

attributes, prediction, individuals, nb_rules, nb_terms, solution_data, solution_type = data
max_rules = int(nb_rules)
max_terms_per_rule = int(nb_terms)
max_terms = max_rules * max_terms_per_rule



#positive_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 0] 
#negative_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 1]

index_prediction = [index for index, value in enumerate(prediction.attribute.values) if value.strip() == prediction.value.strip()][0]

class_individuals = [1 if element[-1][1] == index_prediction else 0 for element in individuals]
individuals = [tuple(element[:-1]) for element in individuals]
individuals_indexes = []
individuals_value = []
for indi in individuals:
    new_indi = []
    new_value = []
    for t in indi:
        new_indi.append(t[0])
        new_value.append(t[1])
    individuals_indexes.append(new_indi)
    individuals_value.append(new_value)
    

nb_attributes = len(attributes)-1
nb_individuals = len(individuals) 

nb_positive_individuals = len([ele for ele in class_individuals if ele == 0])
nb_negative_individuals = len([ele for ele in class_individuals if ele == 1])

attributes_domains_len = [len(attribute.values) for attribute in attributes]
max_attributes_domains = max(attributes_domains_len) 


print()
print("Modeling ...")
print("Number of attributes: ", nb_attributes)
print("Number of individuals: ", nb_individuals)
print("Number of positive individuals: ", nb_positive_individuals)
print("Number of negative individuals: ", nb_negative_individuals)

print("Max rules : ", max_rules)
print("max_terms_per_rule : ", max_terms_per_rule)
print("max_terms: ", max_terms)
print("solution_data: ", solution_data)
print("solution_type: ", solution_type)

def convert1Dto2D(data):
    new_data = []
    index = 0
    for r in range(max_rules):
        n = []
        for t in range(max_terms_per_rule):
            n.append(elements[index])
            index+=1 
        new_data.append(n)
    return new_data

if solution_data != "None":
    solution_data = solution_data.replace("[", "").replace("]", "").strip()
    elements = solution_data.split(",")
    s_attribute_data = convert1Dto2D(elements)
    elements = elements[max_rules*max_terms_per_rule:]
    s_value_data = convert1Dto2D(elements)
    elements = elements[max_rules*max_terms_per_rule:]
    s_operator_data = convert1Dto2D(elements)
    print("s_attribute_data: ", s_attribute_data)
        
EQ = 1 # =
LT = 2 # <
GT = 3 # >



# s(r)(t) represents a disjunction of rules. Each line r is a rule and represents a conjunction of t terms. 
s_attribute = VarArray(size=[max_rules, max_terms_per_rule], dom=range(nb_attributes))

# s_value(r)(t) is the value of the term t of the rule r
s_value = VarArray(size=[max_rules, max_terms_per_rule], dom=range(max_attributes_domains))

# s_operator(r)(t) 0: not used - EQ:1: == - LT:2: > - GT:3: <  
s_operator = VarArray(size=[max_rules, max_terms_per_rule], dom={-1, EQ, LT, GT})

# p(i,r,t) == 1 if the individual i satisfies the term t of the rule r 
satisfies_term = VarArray(size=[nb_individuals, max_rules, max_terms_per_rule], dom={0, 1})

# satisfies_rule(i,r) == 1 if the individual i validates the rule r 
satisfies_rule = VarArray(size=[nb_individuals, max_rules], dom={0,1})

# satisfies_ruleset(i) == 1 if the individual i satisfies any rule
satisfies_ruleset = VarArray(size=nb_individuals, dom={0,1})

# True positive (solution says positive and the individual is positive)
tp = Var(dom=range(nb_individuals))

# False positive (solution says positive but the individual is negative)
fp = Var(dom=range(nb_individuals))

def score_positive_table():
    return [(0,1),(1,0)]

def score_negative_table():
    return [(0,0),(1,1)]

# (satisfies_term[id_individual, id_rule, id_term], s_operator[id_rule, id_term], s[id_rule, id,term])
def create_table_satisfies_term(t, id_individual, id_rule, id_term):
    table = []
    for id_attribute,_ in enumerate(attributes):
        if id_attribute in individuals_indexes[id_individual]:
            index_value = individuals_indexes[id_individual].index(id_attribute)
            value = individuals_value[id_individual][index_value]
        else:
            value = 0  
        table.append((1, id_attribute, EQ, value))
        table.append((0, id_attribute, EQ, ne(value)))
        table.append((1, id_attribute, LT, lt(value)))
        table.append((0, id_attribute, LT, ge(value)))
        table.append((1, id_attribute, GT, gt(value)))
        table.append((0, id_attribute, GT, le(value)))
    table.append((1, ANY, -1, ANY))
    return table
        
satisfy(
    LexIncreasing(s_attribute, strict=True),
    
    [Count(s_operator[r], value=-1) < max_terms_per_rule for r in range(max_rules)],

    # Link the solution and satisfies_term(i,r,t)
    [(satisfies_term[i][r][t], s_attribute[r][t], s_operator[r][t], s_value[r][t]) in create_table_satisfies_term(individuals, i, r, t) 
        for i in range(nb_individuals) 
        for r in range(max_rules) 
        for t in range(max_terms_per_rule)],

    # Conjunction of rule for all individuals
    [conjunction(satisfies_term[i][r]) == satisfies_rule[i][r] for i in range(nb_individuals) for r in range(max_rules)],

    # An individual validates the solution if the disjunction of rules is true with the current solution
    [disjunction(satisfies_rule[i]) == satisfies_ruleset[i] for i in range(nb_individuals)],

    # TP
    Count([satisfies_ruleset[i] for i in range(nb_individuals) if class_individuals[i] == 1], value=1) == tp,

    # FP
    Count([satisfies_ruleset[i] for i in range(nb_individuals) if class_individuals[i] == 0], value=1) == fp
)

if solution_type == "Instantiation":
    satisfy(
        [s_attribute[r][t] == s_attribute_data[r][t] for r in range(max_rules) for t in range(max_terms_per_rule) if s_attribute_data[r][t] != "*"],

        [s_value[r][t] == s_value_data[r][t] for r in range(max_rules) for t in range(max_terms_per_rule) if s_value_data[r][t] != "*"],

        [s_operator[r][t] == s_operator_data[r][t] for r in range(max_rules) for t in range(max_terms_per_rule) if s_operator_data[r][t] != "*"],
            
    )

maximize(
    tp + nb_negative_individuals - fp
)

instance = compile()

result, solution = AbsConProcess().solve(instance, "limit=60s")
#solution = AbsConProcess().solve(instance)


def check_solution_order():
    tp, fp, fn, tn = 0, 0, 0, 0
    for index_individual, individual in enumerate(individuals):
        index_attributes = 0
        index_values = max_rules * max_terms_per_rule
        index_orders = (max_rules * max_terms_per_rule)*2
        or_for_rules = False
        for rule in range(max_rules):
            and_for_terms = []
            for term in range(max_terms_per_rule):
                attribute = solution.values[index_attributes] # Attribute
                value = solution.values[index_values + index_attributes]
                order = solution.values[index_orders + index_attributes]
                if int(order) != -1:
                    if int(attribute) in individuals_indexes[index_individual]:
                        position = individuals_indexes[index_individual].index(int(attribute))
                        value_individual = individuals_value[index_individual][position]
                    else:
                        value_individual = 0
                        
                    if int(order) == EQ:
                            and_for_terms.append(int(value) == int(value_individual))
                    elif int(order) == LT:
                            and_for_terms.append(int(value) < int(value_individual))
                    elif int(order) == GT:
                        and_for_terms.append(int(value) > int(value_individual))
                    else:
                        print("error: " + order + " not possible")
                        exit(0)

                index_attributes = index_attributes + 1
            #print(individual)
            if all(and_for_terms):
                or_for_rules = True
                break
        
        if or_for_rules:
            if class_individuals[index_individual]:
                #print("TP: ", individual)
                tp+=1
            else:
                #print("FP: ", individual)
                fp+=1
        else:
            if class_individuals[index_individual]:
                #print("FN: ", individual)
                fn+=1
            else:
                #print("TN: ", individual)
                tn+=1
    return tp, tn, fp, fn 
    

def print_solution_order():
    solution_str = ""
    index_attributes = 0
    index_values = max_rules * max_terms_per_rule
    index_orders = (max_rules * max_terms_per_rule)*2
    for rule in range(max_rules):
        solution_str += "Rule number " + str(rule) + ":\n"
        for term in range(max_terms_per_rule):
            attribute = solution.values[index_attributes] # Attribute
            attr = attributes[int(attribute)] 
            value = solution.values[index_values + index_attributes]
            sol = attr.values[int(value)]
            order = solution.values[index_orders + index_attributes]
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
                solution_str += " " + attr.name + " " + str_order + " " + str(sol)    
            index_attributes = index_attributes + 1
        solution_str += "\n"
    return solution_str
    
def sensitivity(tp, tn, fp, fn):
    return tp / (tp + fn)

def confidence(tp, tn, fp, fn):
    return tp / (tp + fp)

def fmeasure(s, c):
    return (2 * c * s) / (c + s)

print("Result:", result)

if result != "UNSAT":

    tp, tn, fp, fn = check_solution_order()
    print(solution)

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
