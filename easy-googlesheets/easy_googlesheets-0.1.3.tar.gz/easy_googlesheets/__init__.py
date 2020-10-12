 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 20:48:51 2020

@author: roberto
"""

#import httplib2
import os
import re
from apiclient import discovery
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
import json

class GSheets():
    def __init__(self, secret_filename, spreadsheet_id,  data_tab_name=None, control_id="user0"):
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), secret_filename)
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        self.service=None
        self.tab_id=None
        self.control_id=control_id
        self.spreadsheet_id=spreadsheet_id
        self.index={}
        self.connect(credentials)
        self.main_operations_col = "'%s'!%s"%(control_id,"A")
        self.data_tab_name=data_tab_name
        self.data_range = str(list(self.index.values())[0]+'2:'+list(self.index.values())[-1])
        self.operations_range="'%s'!%s:%s"%(control_id,"A2",list(self.index.values())[-1])
        #self.write_range(data={'values':[["QUERY"]]},range_name=self.main_operations_col+str(1))
        #self.write_range(data={'values':[["CONTROL STACK"]]},range_name=self.control_stack_col+str(1))
        
        if control_id != None:
            tab = self.add_tab(control_id)
            if tab != None:
                self.tab_id = tab['replies'][0]['addSheet']['properties']['sheetId']
            
    def connect(self, credentials):
        self.service=discovery.build('sheets', 'v4', credentials=credentials)
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range="1:1").execute()
        coordinate_col='A'
        for value in request["values"][0]:
            self.index[value]="%s"%(coordinate_col)#,coordinate_row)
            coordinate_col=chr(ord(coordinate_col)+1)

    def set_sheet(self, spreadsheet_id):
        self.spreadsheet_id=spreadsheet_id
        
    def add_tab(self, name=None):
        spreadsheet_data = {'addSheet':{
                                    'properties':{
                                        'title': name
                                    }
                                } 
                            }       
        update_spreadsheet_data = {"requests": spreadsheet_data} # Modified
        update_data = update_spreadsheet_data
        response=None
        try:
            updating = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id, body=update_data)
            response=updating.execute()
        except HttpError as e:
            cont = e.content
            res_json = json.loads(cont.decode('utf-8')) 
            if res_json['error']['code']==400:
                print("WARNING: Another user using this sheet")
        return response
        
    def delete_tab(self, name=None):
        spreadsheet_data = {
                          "deleteSheet": {
                            "sheetId": name
                          }
                        }
        update_spreadsheet_data = {"requests": spreadsheet_data} # Modified
        update_data = update_spreadsheet_data
        response=None
        try:
            updating = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id, body=update_data)
            response=updating.execute()
        except HttpError as e:
            print(e)
            #cont = e.content
            #res_json = json.loads(cont.decode('utf-8')) 
            #if res_json['error']['code']==400:
            #    print("WARNING: Another user using this sheet")
        return response   
    
    def read_range(self, range_name):
        request = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=range_name)
        response = request.execute()
        if 'values' in response:
            response=response['values']
        else:
            response=None
        return response
    
    def write_range(self, data, range_name):
        self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, 
                                 range=range_name, 
                                 valueInputOption='USER_ENTERED',
                                 body=data).execute()

    def insert_range(self, data, range_name):
        value_input_option = 'RAW'  # TODO: Update placeholder value.
        # How the input data should be inserted.
        insert_data_option = 'INSERT_ROWS'  # TODO: Update placeholder value.
        request = self.service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=data)
        response = request.execute()

        return response

    def clear_range(self, range_name):
        clear_values_request_body = {
            # TODO: Add desired entries to the request body.
        }
        request = self.service.spreadsheets().values().clear(spreadsheetId=self.spreadsheet_id, range=range_name, body=clear_values_request_body)
        response = request.execute()
        return response

    def remove(self, group, start_index, end_index):
        spreadsheet_data = [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": 0,
                        "dimension": group,
                        "startIndex": start_index,
                        "endIndex": end_index
                    }
                }
            }
        ]
        
        update_spreadsheet_data = {"requests": spreadsheet_data} # Modified
        
        update_data = update_spreadsheet_data
        updating = self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=update_data)
        response=updating.execute()
        
        #response=self.service.spreadsheet().delete_row(6)
        return response

    def filter_by(self, filter_list):
        data={'values':[]}
        filters=[]
        conditions=""
        p=re.compile(r"^(\w+)(\W+)(\w+)$")
        n=0
        for filt in filter_list:
            if n!=0:
                conditions+=" AND "
            key,op,value=p.search(filt).group(1),p.search(filt).group(2),p.search(filt).group(3)
            col=self.index[key]
            conditions += col+op+value
            n+=1
        filters.append("=QUERY('%s'!%s%d:%s; \"SELECT * where %s\";-1)"%(self.data_tab_name, list(self.index.values())[0],2,list(self.index.values())[-1],conditions))
        data['values'].append(filters)
        #range_name="%s%d:%s%d"%(self.main_operations_col ,2,chr(ord(self.main_operations_col )+1),2)
        self.write_range(data, self.operations_range)
        response = self.read_range(self.operations_range)
        res_list=[]
        if response!=None:
            if response[0][0]!='#N/A':
                for element in response:
                    my_dict={}
                    for key,res in zip(self.index.keys(),element):
                        my_dict[key]=res
                    res_list.append(my_dict)
        #self.clear_range(self.operations_range)
        return res_list

    def insert(self, data):
        my_list=[]
        for key in self.index.keys():
            my_list.append(data[key])
        value_input_option = 'RAW'  # TODO: Update placeholder value.
        # How the input data should be inserted.
        insert_data_option = 'INSERT_ROWS'  # TODO: Update placeholder value.
        value_range_body = {
            'values':[my_list]
        }
        request = self.service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range=self.data_range, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
        response = request.execute()

        return response
    
    #def remove_by(self, filter_list):
    #     selection = self.filter_by(filter_list)


    def close(self):
        if self.tab_id!=None:
            self.delete_tab(self.tab_id)
        else:
            print("WARNING: user stuck")
            
if __name__=='__main__':
    myGSheets = GSheets(secret_filename='credentials.json', 
                        spreadsheet_id='',
                        data_tab_name='Page 1',
                        control_id='user1')
    
    # Example of filter output
    filter_list=["lat>0", "lng<0"]
    print(myGSheets.filter_by(filter_list))
    
    # Example of insert row
    myGSheets.insert({'name': '100 Montaditos ', 
                      'lat': float(37.3812499), 
                      'lng': float(-6.0085387), 
                      'url': 'https://spain.100montaditos.com/es/la-carta/', 
                      'vicinity': 'Calle San Jacinto, 89, 41010 Sevilla', 
                      'ref': 2999389465, 
                      'uploader': 'user1'})
            
    #print(myGSheets.remove("ROWS",6,9))
    
    # Always close at the end
    myGSheets.close()
    