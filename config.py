import datetime
import pprint
import time
import sqlite3

import requests

import functions

TABLE_TYPE = 'A'

START_DATE = datetime.date.today() - datetime.timedelta(days=6)
print(START_DATE)
END_DATE = datetime.date.today()
print(END_DATE)
DELTA = 92



functions.create_tables()
functions.get_data_from_nbp(TABLE_TYPE, START_DATE, END_DATE)
