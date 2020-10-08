import os
import subprocess
from lxml import etree

class Instantiation:
    def __init__(self, pretty_solution, variables, values):
        self.pretty_solution = pretty_solution
        self.variables = variables
        self.values = values

    def __repr__(self):
        return self.variables, self.values

    def __str__(self):
        return str(self.pretty_solution)

class Rulemining():

    def __init__(self, instance_desc, instance_training, instance_test, nb_rules=1, nb_terms=1, data_solution=None, type_solution=None):
        self.instance_desc = instance_desc
        self.instance_training = instance_training
        self.instance_test = instance_test
        self.nb_rules = nb_rules
        self.nb_terms = nb_terms
        self.data_solution = data_solution
        self.type_solution = type_solution
        self.nb_individuals = 0
        self.f_measure = 0
        self.time_pycsp3 = 0
        self.time_solver = 0
        self.result = None

        
    def start(self):
        cmd = "python3 pproblems/rulemining/RuleminingTableOrderVariable.py -dataparser=pproblems/rulemining/Rulemining_Parser.py"
        cmd += " " + self.instance_desc
        cmd += " " + self.instance_training
        cmd += " " + self.instance_test
        cmd += " " + str(self.nb_rules)
        cmd += " " + str(self.nb_terms)
        cmd += " '" + str(self.data_solution) + "'"
        cmd += " " + str(self.type_solution) 
        self.result = subprocess.check_output(cmd, shell=True, encoding="utf-8")
        

    def get_information_from_result(self, pattern, *, position=-1):
        stdout = self.result
        if stdout.find(pattern) != -1:
            index = stdout.find(pattern)
            line = stdout[index:]
            line = line.split("\n")[0]
            line = line.split(" ")[position].strip()
            return line 
        return None
        
    def solution(self):
        stdout = self.result
        #print("_____________________________________________________")
        #print(stdout)
        self.nb_individuals = int(self.get_information_from_result("Number of individuals:"))
        self.f_measure = float(self.get_information_from_result("fmeasure:"))
        self.time_pycsp3 = float(self.get_information_from_result("Total wall clock time:", position=-2))
        self.time_solver = float(self.get_information_from_result("* Solved by AbsCon in", position=-2))
        if stdout.find("<unsatisfiable") != -1 or stdout.find("s UNSATISFIABLE") != -1:
            return Instantiation("unsatisfiable", None, None)
        if stdout.find("<instantiation") == -1 or stdout.find("</instantiation>") == -1:
            print("  Actually, the instance was not solved")
            return None
        left, right = stdout.rfind("<instantiation"), stdout.rfind("</instantiation>")
        s = stdout[left:right + len("</instantiation>")].replace("\nv", "")
        root = etree.fromstring(s, etree.XMLParser(remove_blank_text=True))
        variables = []
        for token in root[0].text.split():
            variables.append(token)
        values = root[1].text.split()  # a list with all values given as strings (possibly '*')
        pretty_solution = etree.tostring(root, pretty_print=True, xml_declaration=False).decode("UTF-8").strip()
        return Instantiation(pretty_solution, variables, values)

    def increase_dimension_solution(self, solution, new_nb_rules, new_nb_terms):
        nb_variables_s = self.nb_rules * self.nb_terms
        old_solution = solution.values
        new_solution = []

        # for the variable s
        solution_s_attribute, old_solution = old_solution[:nb_variables_s], old_solution[nb_variables_s:]
        #print("solution_s_attribute:", solution_s_attribute)
        new_variable_s = self.increase_dimension_s(solution_s_attribute, new_nb_rules, new_nb_terms)
        new_solution.extend(new_variable_s)

        # for the variable s_values
        solution_s_value, old_solution = old_solution[:nb_variables_s], old_solution[nb_variables_s:]
        #print("solution_s_value:", solution_s_value)
        new_variable_s_value = self.increase_dimension_s(solution_s_value, new_nb_rules, new_nb_terms)
        new_solution.extend(new_variable_s_value)
        
        # for the variable s_operator
        solution_s_operator, old_solution = old_solution[:nb_variables_s], old_solution[nb_variables_s:]
        #print("solution_s_operator:", solution_s_operator)
        
        new_variable_s_operator = self.increase_dimension_s(solution_s_operator, new_nb_rules, new_nb_terms)
        new_solution.extend(new_variable_s_operator)
        
        # for the variable satisfies_term
        nb_variables_satisfies_term = self.nb_individuals * self.nb_rules * self.nb_terms
        
        solution_satisfies_term, old_solution = old_solution[:nb_variables_satisfies_term], old_solution[nb_variables_satisfies_term:]
        #print("solution_satisfies_term:", solution_satisfies_term)
        new_variable_satisfies_term = self.increase_dimension_satisfies_term(solution_satisfies_term, new_nb_rules, new_nb_terms)
        
        print("NEXT")
        new_solution.extend(new_variable_satisfies_term)
        
        # for the variable satisfies_rule
        nb_variables_satisfies_rule = self.nb_individuals * new_nb_rules
        new_solution.extend(["*"]*nb_variables_satisfies_rule)

        # for the variable satisfies_ruleset
        new_solution.extend(["*"]*self.nb_individuals)

        # for TP and FP
        new_solution.extend(["*"]*2)
        return new_solution

    def increase_dimension_s(self, partial_solution, new_nb_rules, new_nb_terms):
        index = 0
        new_solution_s = []
        new_size = new_nb_rules * new_nb_terms
        for id_rule in range(self.nb_rules):
            for id_term in range(self.nb_terms):
                new_solution_s.append(partial_solution[index])
                index += 1
            id_term = self.nb_terms
            while id_term != new_nb_terms:
                new_solution_s.append("*")
                id_term += 1
        id_rule = self.nb_rules
        while id_rule != new_nb_rules:
            for id_term in range(new_nb_terms):
                new_solution_s.append("*")
            id_rule += 1
        return new_solution_s

    def increase_dimension_satisfies_term(self, partial_solution, new_nb_rules, new_nb_terms):
        new_solution_s = []
        nb_elements_individual = self.nb_rules*self.nb_terms
        start = 0
        end = nb_elements_individual
        for _ in range(self.nb_individuals):
            new_solution_s.extend(self.increase_dimension_s(partial_solution[start:end], new_nb_rules, new_nb_terms))
            start += nb_elements_individual
            end += nb_elements_individual
        return new_solution_s


instance_description = "pproblems/rulemining/instances/ecoli1d/ecoli1d.1.desc"
instance_training = "pproblems/rulemining/instances/ecoli1d/ecoli1d.individuals.1.training"
instance_test = "pproblems/rulemining/instances/ecoli1d/ecoli1d.individuals.1.test"

def run(*, nb_rules, nb_terms, solution_data=None, solution_type=None):
    rulemining = Rulemining(instance_description, instance_training, instance_test, 
                        nb_rules, nb_terms, solution_data, solution_type)
    rulemining.start()
    solution = rulemining.solution()
    print("solution:\n", solution)
    print("fmeasure:", rulemining.f_measure)
    print("pycsp3 time:", rulemining.time_pycsp3, " seconds")
    print("solver time:", rulemining.time_solver, " seconds")
    print("total time:", rulemining.time_solver + rulemining.time_pycsp3, " seconds")
    return rulemining

def instantiation_strategy():
    rulemining = run(nb_rules=1, nb_terms=1)
    solution = rulemining.solution()
    solution_new_dimension = rulemining.increase_dimension_solution(solution, 1, 2)

    rulemining2 = run(nb_rules=1, nb_terms=2, solution_data=solution_new_dimension, solution_type="Instantiation")
    solution = rulemining2.solution()
    solution_new_dimension = rulemining2.increase_dimension_solution(solution, 1, 3)

    rulemining3 = run(nb_rules=1, nb_terms=3, solution_data=solution_new_dimension, solution_type="Instantiation")
    solution = rulemining3.solution()
    solution_new_dimension = rulemining3.increase_dimension_solution(solution, 1, 4)
    
    rulemining4 = run(nb_rules=1, nb_terms=4, solution_data=solution_new_dimension, solution_type="Instantiation")
    solution = rulemining4.solution()
    
instantiation_strategy()