import datetime
import pprint
import time
import json
import os

import pandas as pd
import requests
import aiohttp
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


from matplotlib import style
style.use("ggplot")


URL = 'http://api.nbp.pl/api/exchangerates/tables/{table}/{startDate}/{endDate}/'
URL_single_curr = 'http://api.nbp.pl/api/exchangerates/rates/{table}/{code}/{startDate}/{endDate}/'
TABLE_TYPE = 'A'
DELTA = 92


def create_tables():
    con = sqlite3.connect('nbp.db')
    cur = con.cursor() 
    cur.execute("CREATE TABLE IF NOT EXISTS currency(currency STRING, code STRING, date DATE, mid DOUBLE)") 
    con.commit()
    con.close()

    con = sqlite3.connect('charts.db')
    cur = con.cursor() 
    cur.execute("CREATE TABLE IF NOT EXISTS pictures(name STRING, chart BLOB)") 
    con.commit()
    con.close()

#Add date from all currency to datebase. This function is useing in config file.
def add_to_db(start_date, end_date, contents):
    
    con = sqlite3.connect('nbp.db')
    cur = con.cursor()
    for i in range(len(contents)):
        for j in range(len(contents[i]['rates'])):
            cur.execute("INSERT INTO currency(currency, code, date, mid) VALUES (:currency, :code, :date, :mid)", {'currency':contents[i]['rates'][j]['currency'], 'code':contents[i]['rates'][j]['code'], 'date':contents[i]['effectiveDate'], 'mid':contents[i]['rates'][j]['mid']})
            con.commit()
    con.close()

#Add date from single currency to datebase. 
def add_to_db_single_curr(start_date, end_date, contents):
    
    con = sqlite3.connect('nbp.db')
    cur = con.cursor()
    for i in range(len(contents['rates'])):
        cur.execute("INSERT INTO currency(currency, code, date, mid) VALUES (:currency, :code, :date, :mid)", {'currency':contents['currency'], 'code':contents['code'], 'date':contents['rates'][i]['effectiveDate'], 'mid':contents['rates'][i]['mid']})
        con.commit()
    con.close()

#Get data from nbp api for single current
def get_data_from_nbp_single_curr(table, curr_code, start_date, end_date):
    r = requests.get(
        URL_single_curr.format(
                        table=TABLE_TYPE,
                        code=curr_code,
                        startDate=start_date.strftime('%Y-%m-%d'),
                        endDate=end_date.strftime('%Y-%m-%d')
                        ),
                        params={'format': 'json'},
        )
    parsed_json = r.json()
    add_to_db_single_curr(start_date, end_date, parsed_json)

#Get data from nbp api for all current
def get_data_from_nbp(table, start_date, end_date):
    r = requests.get(
        URL.format(
            table=TABLE_TYPE,
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=end_date.strftime('%Y-%m-%d')
        ),
        params={'format': 'json'},
    )
    parsed_json = r.json()
    add_to_db(start_date, end_date, parsed_json)

#Get data from nbp api for single current in 92 record parts (nbp api restriction)
def get_data_from_nbp_max(table, code, START_DATE, END_DATE):
    full_delta = END_DATE - START_DATE
    how_many_runs = full_delta.days / DELTA
    if int(how_many_runs) < how_many_runs:
        how_many_runs = int(how_many_runs) + 1
    start_date = START_DATE
    end_date = START_DATE
    for run in range(int(how_many_runs)):
        start_date = end_date
        end_date = start_date + datetime.timedelta(days=DELTA)
        if end_date > END_DATE:
            end_date = END_DATE
        get_data_from_nbp_single_curr(table, code, start_date, end_date)


def get_data_from_db(currency, start, stop):
    con = sqlite3.connect('nbp.db')
    cur = con.cursor()
    query = "SELECT date, mid FROM currency WHERE code LIKE '{}' AND date >= '{}' AND date <= '{}';".format(currency,start,stop)
    cur.execute(query)
    data = cur.fetchall()
    con.close()

    return data, currency

#Create chart and save it in static folder and in db as binary file
def chart(data, currency):

    df = pd.DataFrame(data = data, columns = ['date', 'mid'])
    df['date'] = pd.to_datetime(df['date'])
    fig = plt.figure()
    plt.ylabel('Price')
    plt.xlabel('Date')
    fig.autofmt_xdate(bottom=0.2, rotation=45, ha='right')
    ax = plt.subplot(111)
    plt.plot(df['date'], df['mid'], 'ro-')
    name = currency + '_' + str(min(df['date'])).split()[0] + '_' + str(max(df['date'])).split()[0] + '.svg'
    plt.savefig('static/'+name)
    with open('static/'+name,'rb') as fin:
        img = fin.read()
    save_chart(name, img)
    return name

    

def save_chart(title, pic):
    con = sqlite3.connect('charts.db')
    cur = con.cursor()
    cur.execute('INSERT INTO pictures(name, chart) VALUES (?, ?)',(title, pic))
    con.commit()
    con.close()


    


