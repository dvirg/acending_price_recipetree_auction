#!python3

"""
Imports stock prices from csv files downloaded from Yahoo.
The CSV files are stored in stocks directory.

Author: AnonymousD
Since:  2020-08
"""
import pandas as pd
from os import listdir
from os.path import isfile, join
import random

STOCKS = 'stocks'
POSITIVE_TYPES = ['High', 'Close']
NEGATIVE_TYPES = ['Open', 'Low']
TYPES = [*POSITIVE_TYPES, *NEGATIVE_TYPES]


def get_all_prices_shuffled(stock_file: str):
    df = pd.read_csv(stock_file)
    data = [df[t].to_numpy() for t in TYPES]
    long_data = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            long_data.append(int(data[i][j] * 1000))
    random.shuffle(long_data)
    return long_data


# print(get_all_prices_shuffled(join('stocks','A.csv')))

def get_stocks_tree_prices(agents_counts: list, agents_values: list):
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [get_prices_tree(join(STOCKS, stockFile), agents_counts, agents_values)
            for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]


def get_prices_tree(stock_file: str, agents_counts: list, agents_values: list):
    df = pd.read_csv(stock_file)
    data = []
    for t in TYPES:
        for price in df[t].to_numpy():
            data.append(int(price * 1000))
    random.shuffle(data)
    print(len(data))
    split_data = [[] for _ in range(len(agents_counts))]
    recipe_size = sum(agents_counts)
    data_index = 0
    for agent_index in range(len(agents_counts)):
        for i in range(int(len(data) / recipe_size * agents_counts[agent_index])):
            sign = -1 if agent_index > 0 else 1
            split_data[agent_index].append(sign * data[data_index] * agents_values[agent_index])
            data_index += 1
    return split_data

# print(get_prices_tree('stocks\\T.csv', (1,1)))

def getStocksPricesShuffled():
    onlyfiles = [f for f in listdir(STOCKS) if isfile(join(STOCKS, f))]
    return [getAllPricesShuffled(join(STOCKS, stockFile)) for stockFile in onlyfiles], [f[0:-4] for f in onlyfiles]

def getAllPricesShuffled(stockFile:str):
    df = pd.read_csv(stockFile)
    data = [df[type].to_numpy() for type in TYPES]
    long_data = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            long_data.append(int(data[i][j]*1000))
    random.shuffle(long_data)
    return long_data
