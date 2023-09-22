#! /usr/bin/python3

import yfinance as yf
import pyexcel as pe
import os
import csv
from sklearn.linear_model import LinearRegression
import pandas as pd

def load_portfolio(filename):
    if os.path.isfile(filename):
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            stock_dict = {}
            for row in reader:
                stock_dict[row[0]] = [int(row[1]), float(row[2])]
        print(f'Loaded {filename} successfully!')
    else:
        print(f'\nFile "{filename}" does not exist.\nLoaded empty portfolio')
        return {}
    return stock_dict

def calculate_average(shares, total):
    if shares != 0:
        return round(total/shares, 2)
    else:
        return 0.0

def to_stock_sheet(stock_dict):
    print('Saving "Stock" sheet...')
    data_sheet = [['Stock', 'Shares', 'Total (R$)', 'Average (R$)']]
    for key, value in stock_dict.items():
        data_sheet.append([key] + value + [calculate_average(value[0], value[1])])
    print('"Stock" sheet saved')
    return data_sheet

def variation_delta(current, past):
    current -= past
    current = current / past
    return float(round(current * 100, 2))

def to_beta_sheet(stock_dict):
    print('Saving "Beta" sheet...')

    ibovespa_symbol = "^BVSP"
    stock = yf.Ticker(ibovespa_symbol)
    hist = stock.history(period='2d')
    ibov_var = variation_delta(hist['Close'].iloc[-1], hist['Close'].iloc[0])

    port_var = 0.0
    total_inv = 0.0

    data_sheet = [['Stock', 'Current (R$)', 'Yday (R$)', 'Delta1 (R$)', 'Delta2 (%)', 'Beta']]
    for stock, value in stock_dict.items():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='2d')
        current = float(hist['Close'].iloc[-1])
        yday = float(hist['Close'].iloc[0])
        delta1 = current - yday
        delta2 = variation_delta(current, yday)
        beta = round(delta2/ibov_var, 2)

        data_sheet.append([stock, current, yday, delta1, delta2, beta])

        total_inv += yday * value[0]
        port_var += delta1 * value[0]

    data_sheet.append(['-', '-', '-', '-', '-', '-'])
    data_sheet.append(['Port Var (%)', 'IBOV Var (%)', 'Beta'])

    port_var = port_var / total_inv
    port_var = round(port_var*100, 2)
    beta = round(port_var/ibov_var, 2)

    data_sheet.append([port_var, ibov_var, beta])

    print('"Beta" sheet saved')
    return data_sheet

def total_invested(stock_dict):
    total_sum = 0.0
    for stock, value in stock_dict.items():
        total_sum += value[1]
    return round(total_sum, 2)

def to_current_sheet(stock_dict):
    print('Saving "Current" value sheet...')

    data_sheet = [['Stock', 'Shares', 'Current (R$)', 'Total (R$)', 'Delta1 (R$)', 'Delta2 (%)']]

    current_value = 0.0
    total_inv = total_invested(stock_dict)

    for stock, value in stock_dict.items():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1d')
        current = float(hist['Close'].iloc[0])
        current_total = value[0] * current
        delta1 = current_total - value[1]
        if value[1] != 0:
            delta2 = (100 * delta1) / value[1]
            delta2 = round(delta2, 2)
        else:
            delta2 = 0.0

        data_sheet.append([stock, value[0], current, current_total, delta1, delta2])
        current_value += current_total

    data_sheet.append(['-', '-', '-', '-', '-', '-'])
    data_sheet.append(['Total Inv (R$)', 'Current Val (R$)', 'Delta1 (R$)', 'Delta2 (%)'])

    delta1 = current_value - total_inv
    delta2 = (100 * delta1) / total_inv

    data_sheet.append([total_inv, current_value, delta1, delta2])

    print('"Current" sheet saved')
    return data_sheet

def to_mkt_cap(stock_dict):
    print('Saving "Mkt Cap" sheet...')

    data_sheet = [['Stock', 'Current (R$)', 'Total Shares', 'Mkt. Cap. (R$)']]

    for stock in stock_dict.keys():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1d')
        current = float(hist['Close'].iloc[0])
        shares = ticker.get_shares_full(start='2023-01-01', end=None)
        shares = int(shares.iloc[-1])
        market = shares * current

        data_sheet.append([stock, current, shares, market])

    print('"Mkt Cap" sheet saved')
    return data_sheet

def to_regn_sheet(stock_dict, p='20d'):
    print('Saving "Regn" sheet...')

    tickers = ' '.join(stock_dict.keys())
    tickers = yf.Tickers(tickers)
    hist = tickers.history(period=p)
    closes = hist['Close']
    total_inv = total_invested(stock_dict)

    data_dict = {}
    for index, row in closes.iterrows():
        sum_items = 0.0
        for column_name, value in row.items():
            sum_items += round(stock_dict[column_name][0] * value, 2)
        data_dict[index] = sum_items

    data_sheet = [['Date', 'Port Value (R$)', 'Delta1 (R$)', 'Delta2 (%)']]
    days = 1
    df = {'Close': []}
    for timestamp, sum_items in data_dict.items():
        days += 1
        date = timestamp.strftime('%Y-%m-%d')
        df['Close'].append(sum_items)
        delta1 = float(sum_items - total_inv)
        delta2 = float((100 * delta1) / total_inv)

        data_sheet.append([date, sum_items, delta1, delta2])

    data_sheet.append(['-', '-', '-', '-'])

    df = pd.DataFrame(df)
    df['Days'] = range(1, days)
    model = LinearRegression()
    model.fit(df[['Days']], df['Close'])
    slope = float(model.coef_[0])
    intercept = float(model.intercept_)
    regn = (slope * float(days)) + intercept

    data_sheet.append(['Period (days)', 'Forecast (days)', 'Forecast (R$)', 'Slope (R$/day)', 'Intercept (R$)'])

    data_sheet.append([days-1, days, regn, slope, intercept])

    print('"Regn" sheet saved')
    return data_sheet

if __name__ == "__main__":

    filename = input('To load a portfolio, have your .csv in your working directory. \nInput filename: ')
    ods_filename = filename[:-3] + 'ods'

    stock_dict = load_portfolio(filename)

    stock_sheet = pe.Sheet(to_stock_sheet(stock_dict), name='Stocks')
    current_beta_sheet = pe.Sheet(to_beta_sheet(stock_dict), name='Beta')
    current_value_sheet = pe.Sheet(to_current_sheet(stock_dict), name='Current')
    mkt_cap_sheet = pe.Sheet(to_mkt_cap(stock_dict), name='Mkt Cap')
    regn_sheet = pe.Sheet(to_regn_sheet(stock_dict), name='Regn')

    pe.save_book_as(bookdict={
        'Stocks': stock_sheet,
        'Beta': current_beta_sheet,
        'Current': current_value_sheet,
        'Mkt Cap': mkt_cap_sheet,
        'Regn': regn_sheet,
        }, dest_file_name=ods_filename)
