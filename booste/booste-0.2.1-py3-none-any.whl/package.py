import os
from uuid import uuid4
import numpy as np
import json
import time
from .gpt2_utils import gpt2_main

def gpt2(api_key, in_string, length = 5, temperature = 0.8, window_max = 100):
    return gpt2_main(
        api_key = api_key, 
        model_size = "gpt2", 
        in_string = in_string, 
        length = length, 
        temperature = temperature,  
        window_max = window_max)

def gpt2_xl(api_key, in_string, length = 5, temperature = 0.8, window_max = 100):
    return gpt2_main(
        api_key = api_key, 
        model_size = "gpt2-xl", 
        in_string = in_string, 
        length = length, 
        temperature = temperature,  
        window_max = window_max)