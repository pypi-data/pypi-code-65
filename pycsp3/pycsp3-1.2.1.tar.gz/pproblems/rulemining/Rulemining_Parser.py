# Example: python3 g7_todo/Rulemining.py -dataparser=g7_todo/Rulemining_Parser.py g7_todo/instances_rulemining/ecoli1d/ecoli1d.desc g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.training g7_todo/instances_rulemining/ecoli1d/ecoli1d.individuals.1.test

import sys

from pycsp3.problems.data.parsing import *

assert any(f.endswith(".desc") for f in sys.argv), "At least one of data files have to ends with .desc"
assert any(f.endswith(".training") for f in sys.argv), "At least one of data files have to ends with by .training"
assert any(f.endswith(".test") for f in sys.argv), "At least one of data files have to ends with by .test"

description_file = [f for f in sys.argv if f.endswith(".desc")][0]
training_file = [f for f in sys.argv if f.endswith(".training")][0]
test_file = [f for f in sys.argv if f.endswith(".test")][0]


print("description file:", description_file)
print("training_file:", training_file)
print("test_file:", test_file)

data["attributes"] = []
data["prediction"] = None

class Attribute():
    pos = 0

    def __init__(self, name, order, values):
        self.name = name
        self.order = order
        self.values = values
        self.position = Attribute.pos
        Attribute.pos = Attribute.pos + 1

    def __repr__(self):
        return str(self.name) + ": " + ",".join(element for element in self.values)

class Prediction():
    def __init__(self, attribute, operator, value):
        self.attribute = attribute
        self.operator = operator
        self.value = value

    def __repr__(self):
        return str(self.attribute) + " - " + self.operator + " - " + self.value


def add_attribute(name, elements):
    global data
    order = True if elements.startswith("<") else False
    if order:
        elements = elements[1:]
    elements = [element.replace("{","").replace("}","").strip() for element in elements.split(",")]
    attribute = Attribute(name, order, elements)
    data["attributes"].append(attribute)
    
    
def add_prediction(name, operator, value):
    global data
    attribute = [attribute for attribute in data["attributes"] if attribute.name == name][0]
    data["prediction"] = Prediction(attribute, operator, value)
    

def read_description():
    prediction_started = False
    f = open(description_file, "r") 
    for line in f: 
        if not prediction_started and "@attribute" in line:
            add_attribute(line.split(" ")[1], line.split(" ")[2])
        elif not prediction_started and "@prediction" in line:
            prediction_started = True
            add_prediction(line.split(" ")[1], line.split(" ")[2], line.split(" ")[3])

def read_individuals(file_individuals):
    individuals=[]
    f = open(file_individuals, "r") 
    for line in f:
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            elements_keys = []
            elements = [(element.replace("{","").replace("}","").strip().split(" ")[0], element.replace("{","").replace("}","").strip().split(" ")[1]) for element in line.split(",")]
            elements_index = []
            for element in elements:
                attr = [attribute for attribute in data["attributes"] if attribute.position == int(element[0])][0]
                value_index = [i for i, value in enumerate(attr.values) if value == element[1]][0]
                elements_index.append((attr.position, value_index))
            individuals.append(elements_index)    
    return individuals
            
        
read_description()

data["individuals"] = read_individuals(training_file)

data["nbrules"] = None
data["nbterms"] = None
data["datasolution"] = None
data["typesolution"] = None
#print("HERE")
#print(sys.argv)

if len(sys.argv) > 5:
    if len(sys.argv) > 5:
        data["nbrules"] = int(sys.argv[5])
    if len(sys.argv) > 6:
        data["nbterms"] = int(sys.argv[6])
    if len(sys.argv) > 7:
        data["datasolution"] = sys.argv[7]
    if len(sys.argv) > 8:
        data["typesolution"] = sys.argv[8]

    #print("nb_rules:", data["nbrules"])
    #print("nb_terms:", data["nbterms"])
