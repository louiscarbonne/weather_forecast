#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 12:31:17 2019

@author: louis
"""

#Gather data from https://opendata-download-metobs.smhi.se/api/

#List all the sations on the website that:
# 1. Are closer than D to stockholm
# 2. Have records of all the values ['t','p','wd','wv','h','r'] from t1 to t2

import pandas as pd
import xml.etree.ElementTree as ET
import urllib
from math import sin, cos, sqrt, atan2, radians
import sqlite3


# Calculating distance in km between 2 points with given geo coord
def distance_from_coord(lat1,lon1,lat2,lon2):
    R = 6373.0
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c)

def list_stations_from_smhi(version, from_year, to_year, D, param_dict):
    url_base = "http://opendata-download-metobs.smhi.se/api/version/"+version
    ns = {'metobs': 'https://opendata.smhi.se/xsd/metobs_v1.xsd',
      'portal': 'https://opendata.smhi.se/xsd/portal.xsd'}
    stations = set()
    k = 0
    for key, param in param_dict.items():
        fhandle = urllib.request.urlopen(url_base+"/parameter/"+str(param)+".xml")
        print('Looking at the stations for parameter: ',key,param)
        data = fhandle.read()
        tree = ET.fromstring(data)
        stations_temp = set()
        for station in tree.findall('metobs:station',ns):
            
            station_name = station.find('metobs:name',ns).text
            station_id = station.find('metobs:id',ns).text
            
            coord = station.find('portal:summary',ns).text
            lat = float(coord.split(' ')[1])
            lon = float(coord.split(' ')[3])
            distance = distance_from_coord(59.342,18.0575,lat,lon)
#            print(distance)
            
            t1 = station.find('metobs:from',ns).text.split('-')[0]
            t2 = station.find('metobs:to',ns).text.split('-')[0]
#            print(from_year,to_year)

            if distance < D and t1 <= from_year and t2 >= to_year:
                stations_temp.add((station_name,station_id, distance))
                #print('Station ',station_name,' appended to list of stations for param ',key)
                #print('Distance to Stockholm: ',distance)
#            elif distance > D:
#                #print('Station ',station_name,' not added because too far away')
#            elif t1 > from_year or t2 < to_year: 
#                #print('Station ',station_name,' not added because not enough records of parameter ',key)
            
        if k == 0:
            stations = stations_temp.copy()
        else:
            stations = stations & stations_temp
            print(stations_temp)
            print('Set of stations removed from the current list because not in list of param ',key,' :' )
            print(stations-stations_temp)
            print('Set of stations not added because not in current list:')
            print(stations_temp-stations)
        k += 1
        print('###################################################')
              
    print('Final set of stations:')
    print(stations)
    return stations

def smhi_to_db(version, station_list, from_year, to_year, param_dict, db, table_name):
    
    url_base = "http://opendata-download-metobs.smhi.se/api/version/"+version
    
    conn = sqlite3.connect(db)
    cur = conn.cursor()    

    
    for station_name, station_id, dist in station_list:
        #Filling the data table (station_id,station_name,parameter,datetime,value)
        print(station_name)
        for key, param in param_dict.items():
            print(key)
            url = url_base+"/parameter/"+str(param)+"/station/"+station_id+"/period/corrected-archive/data.csv"
            urllib.request.urlretrieve(url,'data.csv')
            table = pd.read_csv('data.csv',sep=';', usecols = [0,1,2])
            i = table.index[table.iloc[:,0] == 'Datum'].tolist()
            table.columns = table.iloc[i[0]]
            table = table.drop(table.index[:i[0]+1])
            table['date_time'] = [i+' '+j for i,j in zip(table['Datum'],table['Tid (UTC)'])]
            table['date_time']= pd.to_datetime(table['date_time'])
            table = table.drop(columns=['Datum','Tid (UTC)'])
            table = table[pd.to_datetime(table['date_time']) > pd.to_datetime(str(from_year))]
            table = table[pd.to_datetime(table['date_time']) < pd.to_datetime(str(to_year))]
            #Inserting the new data in the database
            table['station_id']= int(station_id)
            table['station_name']= station_name
            table['parameter'] = key
            table.columns = ['value','time','station_id','station_name','parameter']
            table = table[['time','station_id','station_name','parameter','value']]
            table = table.set_index('time')
            table['value'] = [float(i) for i in table['value']]
            print(table.head())
            print('########')
            print(table.dtypes)
            
            table.to_sql(table_name, conn, if_exists='append', index_label='time')
            conn.commit()
            
# %%
#Application
parameters = {
        't': 1
        ,'p': 9
        ,'wd': 3
        ,'wv': 4
        ,'h': 6
#        ,'r_per_day': 5
#        ,'r_per_h': 7
        }

list_stations = list_stations_from_smhi('latest', '2009', '2018', 500, parameters)
smhi_to_db('latest', list_stations ,'2010', '2017', parameters, 'weather_archive.db', 'data')