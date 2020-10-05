#!/usr/bin/python


'''
   Copyright © 2019  Atos Spain SA. All rights reserved.
  
   This file is part of the ReMAP platform.
  
   The ReMAP platform is free software: you can redistribute it 
   and/or modify it under the terms of GNU GPL v3.
   
   THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT ANY WARRANTY OF ANY KIND, 
   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT, 
   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
   CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN ACTION OF CONTRACT, TORT 
   OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
   OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  
   See README file for the full disclaimer information and LICENSE file 
   for full license information in the project root.  
  '''


import pandas as pd
import numpy as np
import json
# Import ReMAP SDK module
from remapSDK import remapSDK


class model:

    def __init__(self, system, param):
        self.parameters = param
        self.system = system
        self.sensor_data = pd.DataFrame()
        self.RUL = np.NaN
        self.std = np.NaN

        # Simple linear regression model:
        self.slope = 13.0

        # Standard deviation of RUL is proportional to prognostic horizon
        self.std_slope = 1.0

        # Define how we express the RUL
        self.unit = "CYCLES"

    def calculate_rul(self, sensor_data):
        self.sensor_data = sensor_data

        # Just take the last value from the relevant parameter and calculate RUL
        sensor_value = sensor_data[self.parameters[0]].values[-1]
        self.RUL = sensor_value * self.slope
        self.std = sensor_value * self.std_slope
        return [self.RUL, self.std]


 ### 1. Initialize ###
print('#'*10 + ' INITIALIZING ' + '#'*10)
remapSdk = remapSDK.Sdk()

print('#'*10 + ' WP5 PoC ' + '#'*10)

# Live data
print('#'*10 + ' READING LIVE DATA ' + '#'*10)
# Sensor data
data_table = pd.DataFrame()
data_table = data_table.append(pd.read_csv(
    remapSdk.getDataset()), ignore_index=True)
data_table['timestamp'] = pd.to_datetime(
    data_table['timestamp'])


# Prognostics
print('#'*10 + ' RUNNING PROGNOSTICS ' + '#'*10)

# Select last flight of this aircraft
last_departure = data_table.sort_values(by='timestamp').iloc[-1].timestamp
data_last_flight = data_table[data_table.timestamp == last_departure]

# Access models from all aircraft. Feed data to these models. Calculate RUL
start_time = remapSdk.getStartTime()
print("start_time: "+start_time)

end_time = remapSdk.getEndTime()
print("end_time: "+end_time)

tailno = remapSdk.getTailNumber()
print("tailno: "+tailno)


# model(system, params)
metadata = pd.DataFrame()
metadata = metadata.append(remapSdk.getMetadata())
parameters = metadata[metadata.type == "number"].to_dict('records')
parametersInference = [str(parameters[0]['parameter']['name'])]
print()
print("Parameters for inference:")
print(parametersInference)
print("PartNo("+parametersInference[0]+"): " +
      remapSdk.getParamPartNumber(parametersInference[0]))
new_model = model('brake_1', parametersInference)

[RUL, std] = new_model.calculate_rul(data_last_flight)

jsonoutput = {
    "rulUnit": new_model.unit,
    "rulValue": RUL,
    "confidenceIntervalMin": RUL - std,
    "confidenceIntervalMax": RUL + std,
    "distributionType": "Normal",
    "distributionParameters": [
        {
            "name": "mean",
            "value": RUL
        },
        {
            "name": "std",
            "value": std
        }
    ]
}

output = remapSdk.sendOutput(jsonoutput)
print(json.dumps(json.loads(output), indent=2))
print('#'*10 + ' End WP5 PoC ' + '#'*10)

print('')

print('#'*10 + ' WP6 PoC ' + '#'*10)
aircraft = remapSdk.getAircraft()
print("aircraft: "+json.dumps(aircraft, indent=2))

fleet = remapSdk.getFleet()
print("fleet: "+json.dumps(fleet, indent=2))

dataset = remapSdk.getDataset()
print("dataset file: "+dataset)
dataset_table = pd.DataFrame()
dataset_table = dataset_table.append(pd.read_csv(
    remapSdk.getDataset()), ignore_index=True)
print(dataset_table)

tasks = remapSdk.getTasks()
print("tasks file: "+tasks)
tasks_table = pd.DataFrame()
tasks_table = tasks_table.append(pd.read_csv(
    remapSdk.getTasks()), ignore_index=True)
print(tasks_table)

schedule = remapSdk.getSchedule()
print("schedule: "+schedule)
schedule_table = pd.DataFrame()
schedule_table = schedule_table.append(pd.read_csv(
    remapSdk.getSchedule()), ignore_index=True)
print(schedule_table)

output = remapSdk.sendScheduleOutput(schedule)

print('#'*10 + ' End WP6 PoC ' + '#'*10)