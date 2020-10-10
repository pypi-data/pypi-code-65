from py_fcm import from_json, join_maps, FuzzyCognitiveMap, TYPE_DECISION

import numpy as np
from sklearn.metrics import f1_score
from sklearn.neural_network import MLPClassifier


# TODO: Create unit test for used functions and FCM behavior
# TODO: Update project architecture
# TODO: Use adjacency matrix for graph representation for later inference process vectorization
# TODO: Add generation algorithm to Py_FCM library
# TODO: optimize generation algorithm


def to_binary_list(value: int):
    return [int(val) for val in list(np.binary_repr(value, 8))]


def create_training_set():
    START = 1
    END = 100
    X = [to_binary_list(x) for x in range(START, END)]
    y = []
    for value in range(START, END):
        if value % 3 == 0 and value % 5 == 0:
            y.append("FizzBuzz")
        elif value % 3 == 0:
            y.append("Fizz")
        elif value % 5 == 0:
            y.append("Buzz")
        else:
            y.append('None')
    return X, y


def test_load_from_json():
    fcm_json = """{
             "max_iter": 500,
             "activation_function": "sigmoid",
             "activation_function_args": {"lambda_val":1},
             "memory_influence": false,
             "decision_function": "LAST",
             "concepts" :
              [
                {"id": "concept_1", "type": "SIMPLE", "activation": 0.5},
                {"id": "concept_2", "type": "DECISION", "custom_function": "sum_w", "custom_function_args": {"weight":0.3}},
                {"id": "concept_3", "type": "SIMPLE", "memory_influence":true },
                {"id": "concept_4", "type": "SIMPLE", "custom_function": "saturation", "activation": 0.3}
              ],
             "relations":
              [
                {"origin": "concept_4", "destiny": "concept_2", "weight": -0.1},
                {"origin": "concept_1", "destiny": "concept_3", "weight": 0.59},
                {"origin": "concept_3", "destiny": "concept_2", "weight": 0.8911}
              ]
            }
            """
    my_fcm = from_json(fcm_json)
    print(my_fcm.to_json())
    my_fcm.run_inference()
    result = my_fcm.get_final_state(concepts_type='any')
    print(result)
    print(my_fcm.get_topology_to_string())


def test_join_maps():
    fcm_json1 = """{
                 "max_iter": 500,
                 "activation_function": "sigmoid",
                 "activation_function_args": {"lambda_val":1},
                 "memory_influence": false,
                 "decision_function": "LAST",
                 "concepts" :
                  [
                    {"id": "concept_1", "type": "SIMPLE", "activation": 0.5},
                    {"id": "concept_2", "type": "DECISION", "custom_function": "sum_w", "custom_function_args": {"weight":0.3}},
                    {"id": "concept_3", "type": "SIMPLE", "memory_influence":true }
                  ],
                 "relations":
                  [
                    {"origin": "concept_1", "destiny": "concept_3", "weight": 0.59},
                    {"origin": "concept_3", "destiny": "concept_2", "weight": 0.8911}
                  ]
                }
                """
    fcm_json2 = """{
                 "max_iter": 500,
                 "activation_function": "sigmoid",
                 "activation_function_args": {"lambda_val":1},
                 "memory_influence": false,
                 "decision_function": "LAST",
                 "concepts" :
                  [
                    {"id": "concept_2", "type": "DECISION", "custom_function": "sum_w", "custom_function_args": {"weight":0.3}},
                    {"id": "concept_4", "type": "SIMPLE", "custom_function": "saturation", "activation": 0.3}
                  ],
                 "relations":
                  [
                    {"origin": "concept_4", "destiny": "concept_2", "weight": 0.2}
                  ]
                }
                """
    fcm_json3 = """{
                 "max_iter": 500,
                 "activation_function": "sigmoid",
                 "activation_function_args": {"lambda_val":1},
                 "memory_influence": false,
                 "decision_function": "LAST",
                 "concepts" :
                  [
                    {"id": "concept_1", "type": "SIMPLE", "activation": 0.3},
                    {"id": "concept_2", "type": "DECISION", "custom_function": "sum_w", "custom_function_args": {"weight":0.3}},
                    {"id": "concept_3", "type": "SIMPLE", "memory_influence":true },
                    {"id": "concept_4", "type": "SIMPLE", "custom_function": "saturation", "activation": 0.3}
                  ],
                 "relations":
                  [
                    {"origin": "concept_1", "destiny": "concept_3", "weight": -0.3911}
                  ]
                }
                """
    fcm1 = from_json(fcm_json1)
    fcm2 = from_json(fcm_json2)
    fcm3 = from_json(fcm_json3)

    new_fcm = join_maps([fcm1, fcm2, fcm3])  # , node_strategy="intersection"
    new_fcm.run_inference()
    result = new_fcm.get_final_state(concepts_type='any')
    print(result)
    print(new_fcm.to_json())


if __name__ == "__main__":
    fcm = FuzzyCognitiveMap()
    fcm.add_concept('test')
    print(fcm.to_json())
    fcm.add_concept('test', concept_type=TYPE_DECISION)
    print(fcm.to_json())