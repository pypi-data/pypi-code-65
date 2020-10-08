from pycsp3 import *
from pycsp3.solvers.abscon import AbsConProcess
from itertools import chain, combinations


#python3 g7_todo/RuleminingTable.py -dataparser=g7_todo/Rulemining_Parser.py g7_todo/instances_rulemining/ecoli1d/ecoli1d.desc g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.training g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.test


attributes, prediction, individuals = data

positive_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 0] 
negative_individuals = [tuple(element[:-1]) for element in individuals if element[-1] == 1] 
class_individuals = [0 if element[-1] == 1 else 1 for element in individuals]
individuals = [tuple(element[:-1]) for element in individuals]


nb_attributes = len(attributes)-1
nb_individuals = len(positive_individuals) + len(negative_individuals)

# Rule mining problem (partial classification) A solution is a matrix s[i][j] that represents a disjunction of rules. Each line "i" is a rule and represents a conjunction of terms. Each position "j" of a term is associated to a attribut of the position "j" in the table attributes.  
# Note also that we fix the number of term to the number of attributs

max_rules = 2
max_terms_per_rule = nb_attributes
max_terms = max_rules * max_terms_per_rule
nb_operators = 3 # TODO For later
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
print("nb_operators: ", nb_operators)

#print(attributes)

# TODO the character " in the comment lines is incorrectly displayed in the xcsp3 file (xml file)

# s(r)(t) represents a disjunction of rules. Each line r is a rule and represents a conjunction of t terms.
s = VarArray(size=[max_rules, max_terms_per_rule], dom=lambda i, j: set(range(len(attributes[j].values))) | {-1})

# p(i,r) == 1 if the positive individual i satisfies the rule r else 0
p = VarArray(size=[nb_positive_individuals, max_rules], dom={0,1})

# n(i,r) == 1 if the negative individual i satisfies the rule r else 0
n = VarArray(size=[nb_negative_individuals, max_rules], dom={0,1})

# check(i) == 1 if the individual i satisfies any rule
p_check = VarArray(size=nb_positive_individuals, dom={0,1})

# check(i) == 1 if the individual i satisfies any rule
n_check = VarArray(size=nb_negative_individuals, dom={0,1})

# score(i) store if the individual is TP(0), FP(1) 
p_score = VarArray(size=nb_positive_individuals, dom={0,1})

# score(i) store if the individual is TP(0), FP(1) 
n_score = VarArray(size=nb_negative_individuals, dom={0,1})

#TP
tp = Var(dom=range(nb_individuals))

tn = Var(dom=range(nb_individuals))

#fp = Var(dom=range(nb_individuals))

#fn = Var(dom=range(nb_individuals))



# powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

# Calculate the table for the individual i
def positive_table(index):
    t = []
    subsets_positions = powerset(range(len(positive_individuals[index])))
    for subset_position in tuple(subsets_positions):
        if len(subset_position) == 0:
            continue
        new_tuple = [1]
        for i, ele in enumerate(positive_individuals[index]):
            new_tuple.append(ele if i in subset_position else -1)
        t.append(tuple(new_tuple))
    t.append((0,) + (ANY,) * nb_attributes)
    return t


def negative_table(index):
    tab = []
    print(negative_individuals[index])
    for i, _ in enumerate(negative_individuals[index]):
        position_term = 0
        term = 0
        new_tuple = [0]
        for j, t in enumerate(negative_individuals[index]):
            if i != j:
                new_tuple.append(ANY)
            else:
                new_tuple.append(t)
                position_t = j + 1
                term = t
        #print("1:", new_tuple)
        #print("pos", position_t)
        d = list(range(len(attributes[position_t].values)))
        for t1 in d:
            if t1 != term:
                new_tuple2 = new_tuple.copy()
                new_tuple2[position_t] = t1
                tab.append(tuple(new_tuple2))
    tab.append((1,) + (ANY,) * nb_attributes)
    print(tab)
    exit(0)
    
    return tab


def score_positive_table():
    return [(0,1),(1,0)]

def score_negative_table():
    return [(0,0),(1,1)]

def create_disjunction(id_individual, id_rules):
    conj = []
    for j in range(nb_attributes):
        conj.append((positive_individuals[id_individual][j] == s[id_rules][j])|(s[id_rules][j] == -1))
    return conjunction(*conj)

satisfy(

    # Link the solution and p(i,j)
    [(p[i][r], s[r]) in positive_table(i) for i in range(nb_positive_individuals) for r in range(max_rules)],

    # Link the solution and p(i,j)
    [(n[i][r], s[r]) in negative_table(i) for i in range(nb_negative_individuals) for r in range(max_rules)],

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

    #Count(p_score, value=1) == fn

    Count(n_score, value=0) == tn

    #Count(n_score, value=1) == fp,

)

maximize(
    Sum(tp + tn)
)

instance = compile()

solution = AbsConProcess().solve(instance, "limit=500s")
#solution = AbsConProcess().solve(instance)

def check_solution():
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for ii, i in enumerate(individuals):
        index = 0
        or_for_rules = False
        for rule in range(max_rules):
            and_for_terms = []
            for term in range(nb_attributes):
                sol = solution.values[index]
                if sol != "-1":
                    and_for_terms.append(int(i[term]) == int(sol))
                index = index + 1
            print(and_for_terms)
            if all(and_for_terms):
                or_for_rules = True
                break
        print("individual:")
        print(i)
        print("check: ", or_for_rules)
        if or_for_rules:
            if class_individuals[ii]:
                tp+=1
                print("TP")
            else:
                fp+=1
                print("FP")
        else:
            if class_individuals[ii]:
                fn+=1
                print("FN")
            else:
                tn+=1
                print("TN")
    print("tp:", tp)
    print("tn:", tn)
    print("fp:", fp)
    print("fn:", fn)

def print_solution():
    nb_sols = max_rules * nb_attributes
    solution_str = ""
    index = 0
    print()
    for rule in range(max_rules):
        solution_str += "Rule number " + str(rule) + ":\n"
        for term in range(nb_attributes):
            sol = solution.values[index]
            if sol != "-1":
                attr = attributes[term]
                sol = attr.values[int(sol)]
                solution_str += " " + str(term) + " " + attr.name + " = " + sol
            index = index + 1
        solution_str += "\n"
    print("solution:")
    print(solution_str)





check_solution()
print_solution()
print(solution)
