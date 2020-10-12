# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 16:04:40 2020

@author: 41207
"""
from sklearn.externals import joblib
from rdkit import Chem
from rdkit.Chem import AllChem
import pandas as pd
import numpy as np
import csv

def Model_selection(current_path,model): 
    cf = joblib.load(current_path+model)
    return cf
    
def ECFP_generate(filename,savefile,dimension,radius):
    df = pd.read_csv(filename,engine='python').iloc[:, 0]  
    smiles_list = np.array(df)
    ECFP=[]
    for i in range(len(smiles_list)):
        Smiles=smiles_list[i]
        m= Chem.MolFromSmiles(Smiles)
        fp = AllChem.GetMorganFingerprintAsBitVect(m, radius, nBits=dimension)
        fp = list(map(int,list(fp.ToBitString())))
        ECFP.append(fp)
    f = open(savefile,'w')
    csv_writer = csv.writer(f)
    b=[]
    for i in range(dimension):
        b.append(i) 
    csv_writer.writerow(b)
    for i in range(len(ECFP)):
        csv_writer.writerow(ECFP[i])
    f.close()
    fingerprint_content = pd.read_csv(savefile)
    des_list = np.array(fingerprint_content)
    return des_list

if __name__ == '__main__':
	current_path = '/home/user/zhuyang/ECFP/'
	model = 'CYP3A4-substrate.pkl'  
	filename = '/home/user/zhuyang/ECFP/zy3.csv'
	savefile = 'Molecular fingerprint.csv'
	dimension = 1024
	radius = 2
	###################################### Prediction ##########
	cf = Model_selection(current_path,model)
	des_list = ECFP_generate(filename,savefile,dimension,radius)
	y_predict_label = cf.predict(des_list)
	y_predict_proba = cf.predict_proba(des_list)
	print '#'*10+'Results labels'+'#'*10
	print y_predict_label
	print '#'*10+'Results probabilities'+'#'*10
	print y_predict_proba