#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 21:14:36 2019

@author: louis Carbonne
Data from https://rp5.ru/ weather archive

Goal: based on the pressure, humidity, and temperature data, predict if it has been raining
No prediction of the weather based on time data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#data import in a dictionnary
df= {}
dates={}
for name in ['Temperature','Pressure','Wind','Humidity','Rainfall']:
    df[name] = pd.read_csv(name+'.csv', sep=';', parse_dates = True)

#Grouping by date and merging tables
for key, dataset in df.items():
    df[key]= dataset.groupby('Date', as_index=False).mean()

merged = df['Temperature']
for key, dataset in df.items():
    if key != 'Temperature':
        merged = merged.merge(dataset, on='Date')
        
merged['Date'] = pd.to_datetime(merged.Date , format = '%Y-%m-%d')
merged.index = merged.Date
merged = merged.drop(['Date'], axis=1)

#rest of the data: interpolation to fill the NaN values
merged= merged.interpolate()

#renaming for simplicity
merged.columns = ['t','p','wd','wv','h','r']

#creating the train and validation set
train = merged[:int(0.8*(len(merged)))]
test = merged[int(0.8*(len(merged))):]

##Feature scaling
#from sklearn.preprocessing import StandardScaler
#sc_X = StandardScaler()
#data = sc_X.fit_transform(merged)

#fit the model
from statsmodels.tsa.vector_ar.var_model import VAR

model = VAR(endog=train)
model_fit = model.fit()

# make prediction on validation
prediction = model_fit.forecast(model_fit.y, steps=len(test))

#converting predictions to dataframe
cols = merged.columns = ['t','p','wd','wv','h','r']
pred = pd.DataFrame(index=range(0,len(prediction)),columns=[cols])
for j in range(0,13):
    for i in range(0, len(prediction)):
       pred.iloc[i][j] = prediction[i][j]

#check rmse
for i in cols:
    print('rmse value for', i, 'is : ', sqrt(mean_squared_error(pred[i], valid[i])))
    
'''
X_list = [merged[['t','p','wd','wv','h','r']].iloc[i:i+10].to_numpy() for i in np.arange(len(merged))]
X = np.ar

#Creating Y dataset as the weather on the 11th day 
Y = X.iloc[10:]
'''















