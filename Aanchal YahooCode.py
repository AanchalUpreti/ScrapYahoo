#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
from datetime import datetime, timedelta
import time
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt

# For Before Corona
#end = datetime(2019,12,27)
#start = end - BDay(100)

# For After Corona
start = datetime(2019,12,27)
end = datetime.today()

baseUrl = 'https://finance.yahoo.com/quote/'
tech_list = 'AAPL'

# Function to get stock data, plot graph and store data in csv
def getStockData(tick, endPeriod, startPeriod):
    end = endPeriod
    start = startPeriod
    print(start,end)
    
    #Convert Dates to UNIX Time for Params
    unixStart = int(time.mktime(start.timetuple()))
    unixEnd = int(time.mktime(end.timetuple()))
    
    # Url link to yahoo finance with search parameters
    url = (baseUrl + str(tick) + '/history?period1=' + str(unixStart) + '&period2=' + str(
        unixEnd) + '&interval=1d&filter=history&frequency=1d')
    scrapWebsite(url)

# Function to scrap website
def scrapWebsite(url):
    
    # Send request to website
    result = requests.get(url)
    c = result.content
    
    # Set Beautiful Soup object
    soup = BeautifulSoup(c, "lxml")
    summary = soup.find('div', {'class': 'Pb(10px) Ovx(a) W(100%)'})
    
    # Fetch table with historical data
    tables = summary.find_all('table')
    
    # Array to store table rows
    data = []
    rows = tables[0].find_all('tr')
    for tr in rows:
        cols = tr.findAll('td')
        if len(cols) == 7:
            for td in cols:
                text = td.find(text=True)
                data.append(text)
    
    # Create Pandas DataFrame object
    dFrame = pd.DataFrame(np.array(data).reshape(int(len(data) / 7), 7))
    dFrame.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Aclose', 'Volume']
    dFrame.set_index('Date', inplace=False)

    # Call function to store data to csv file
    dump2csv(dFrame)
    
    # Call function to Calculate SMA and EMA and plot graph
    movingAverage(dFrame)

# Function to Calculate SMA and EMA and plot graph
def movingAverage(stockprices):
    # For printing close and type casting its values to int
    stockprices['Close'] = stockprices['Close'].astype(float)

    # Calculate SMA
    stockprices['SMA 20 Days'] = stockprices['Close'].rolling(20).mean()
    stockprices['SMA 50 Days'] = stockprices['Close'].rolling(50).mean()
    
    # Calculate EMA
    stockprices['EMA 20 Days'] = stockprices['Close'].ewm(span=20, adjust=False).mean()
    stockprices['EMA 50 Days'] = stockprices['Close'].ewm(span=50, adjust=False).mean()
    
    # PLot Graph of Price CLose, SMA and EMA Data
    stockprices[['Close', 'SMA 20 Days', 'EMA 50 Days', 'SMA 50 Days', 'EMA 20 Days']].plot(figsize=(12, 8))
    plt.grid(True)
    plt.title('AAPL Moving Averages')
    plt.axis('tight')
    plt.ylabel('Price')

# Funciton to Store data to CSV
def dump2csv(dataFrame):
    filename = str(tech_list) + '.csv'
    
    # If file already exists, append data to end of file, otherwise create new file with Column Names
    if os.path.exists(filename):
        append_write = 'a'
        dataFrame.to_csv(filename, sep='\t', mode=append_write, header=False)
    else:
        append_write = 'w'
        dataFrame.to_csv(filename, sep='\t', mode=append_write)


# Call the main function to run the script
getStockData(tech_list, end, start)