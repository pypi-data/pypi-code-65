from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os
import gspread
import math
from math import sqrt
import time
import csv
import random
from pprint import pprint
from googleapiclient.discovery import build
from matplotlib import pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
import pandas as pd
from sklearn import metrics
from sklearn.metrics import explained_variance_score, r2_score, mean_absolute_error, mean_squared_error
from oauth2client import file, client, tools


def get_dataset(dataset):
    """returns a dataframe named dataset from the drive after all data preprocessing"""
    dataframe = []
    scope = ["https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope)
    client = gspread.authorize(creds)
    spreadSheet = client.open(dataset)
    sheet = spreadSheet.sheet1

    for i, worksheet in enumerate(spreadSheet.worksheets()):
        with open("myfile", "w") as file:
            writer = csv.writer(file)
            writer.writerows(worksheet.get_all_values())

    dataframe = loadCSV("myfile", dataframe)
    dataframe = dataframe[1:]  # since first row contains names of features

    strRow_to_float(dataframe)
    minmax = minmax_normalisation(dataframe)
    normalisze_dataframe(dataframe, minmax)
    return dataframe


def loadCSV(filename, dataframe):
    """returns a dataframe"""
    with open(filename, "r") as file:
        csvFile = csv.reader(file)
        for row in csvFile:
            if not row:
                continue
            dataframe.append(row)
    return dataframe


def strRow_to_float(dataframe):
    """Converts string row to float"""
    for index, row in enumerate(dataframe):
        row = [float(num)for num in row]
        dataframe[index] = row


def normalisze_dataframe(dataframe, minmax):
    """returns a normalised data values in between [0,1]"""
    for row in dataframe:
        for i in range(len(row)):
            row[i] = (row[i]-minmax[i][0])/(minmax[i][1]-minmax[i][0])


def minmax_normalisation(dataframe):
    """returns a list of min max values for each feature in a dataset"""
    minmax = list()
    for i in range(len(dataframe[0])):
        colValues = [row[i] for row in dataframe]
        minValue = min(colValues)
        maxValue = max(colValues)
        minmax.append([minValue, maxValue])
    return minmax


def predict(row, coefficients):
    """returns the predicted value using coefficients"""
    predicted = coefficients[0]  # bias
    for i in range(len(row)-1):
        predicted = coefficients[i+1]*row[i]
    return predicted


def trainParameters(train, learningRate, noOfEpochs):
    """optimising parameters using stochastic gradient descent algorithm"""
    coeff = [0.0 for i in range(len(train[0]))]
    for epoch in range(noOfEpochs):
        for row in train:
            predicted = predict(row, coeff)
            error = predicted-row[-1]
            coeff[0] = coeff[0]-(learningRate*error)  # bias
            for i in range(len(row)-1):
                coeff[i+1] = coeff[i+1]-(learningRate*error*row[i])
    return coeff


def linear_Regression_SGD(train, test, learningRate, noOfEpochs):
    """returns the predicted list of outputs on test data"""
    predictions = []
    coef = trainParameters(train, learningRate, noOfEpochs)
    for row in test:
        predicted = predict(row, coef)
        predictions.append(predicted)
    return predictions, coef


def hyperVisualise(actual, predictions, coef):
    """creates a file contains all the metrics of model to be saved to drive"""
    metric = open("metricsFile.txt", "w")
    metric.write("The learnt parameters of the regression model are: ")
    for i in range(0, len(coef)):
        metric.write(str(coef[i]))
        metric.write("\n")
    metric.write("mean_Square_Error is {}".format(
        mean_squared_error(actual, predictions)))
    metric.write("\n")
    metric.write("mean_Absolute_Error is {}".format(
        mean_absolute_error(actual, predictions)))
    metric.write("\n")
    metric.write("explained_Variance_Square is {}".format(
        explained_variance_score(actual, predictions)))
    metric.write("\n")
    metric.write("R_2 Score is {}".format(r2_score(actual, predictions)))
    metric.write("\n")
    metric.close()
    save_Files_To_Drive("metricsFile.txt")


def save_Files_To_Drive(filename):
    """saves a file into drive after proper authentication"""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    file1 = drive.CreateFile({"title":filename})
    file1.SetContentFile(filename)
    file1.Upload()

def plotGraph(dSet):
    """returns a graph between x and y coordinate to let you save to drive"""
    print("Enter the column number to be plotted on X co-ordinate")
    x_coordinate=int(input())
    print("Enter the column number to be plotted on Y co-ordinate")
    y_coordinate=int(input())
    x_coordinateList=[]
    y_coordinateList=[]
    for i in range(len(dSet)):
        x_coordinateList.append(dSet[i][x_coordinate-1])
        y_coordinateList.append(dSet[i][y_coordinate-1])
    plt.plot(x_coordinateList,y_coordinateList)
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.savefig("graph.png")
    save_Files_To_Drive("graph.png")
    plt.show()


def main():
    print("Enter the name of the dataset from your drive")
    dataset = input()
    dSet= get_dataset(dataset)
    random.shuffle(dSet)
    # 80% of data for training and remaining for testing our model
    tlength = int(0.8*(len(dSet)))
    train = dSet[:tlength]
    test = dSet[tlength:]
    predictions, coef = linear_Regression_SGD(train, test, 0.001, 50)
    actual = []
    for i in range(len(test)):
        actual.append(test[i][-1])
    hyperVisualise(actual, predictions, coef)
    plotGraph(dSet)


if __name__ == "__main__":
    main()
