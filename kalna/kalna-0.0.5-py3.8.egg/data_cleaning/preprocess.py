import pandas as pd
import numpy as np



def read_data(file):
    data = pd.read_csv(file)
    return data

def show_data(data,no_of_records):
    return data.head(no_of_records)

def calculateSquare(num):
    square = num * num
    return square

def calculateCube(num):
    return (num * num *num)