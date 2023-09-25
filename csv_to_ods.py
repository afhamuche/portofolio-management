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
    return data_sheet

def variation_delta(current, past):
    current -= past
    current = current / past
    return float(round(current * 100, 2))

def to_beta_sheet(stock_dict):
    print('Saving "Beta" sheet...')

    ibovespa_symbol = "^BVSP"
    ticker = yf.Ticker(ibovespa_symbol)
    hist = ticker.history(period='2d')
    ibov_var = round(variation_delta(hist['Close'].iloc[-1], hist['Close'].iloc[0]), 2)

    port_var = 0.0
    total_inv = 0.0

    data_sheet = [['Stock', 'Current (R$)', 'Yday (R$)', 'Delta1 (R$)', 'Delta2 (%)', 'Beta']]
    for stock, value in stock_dict.items():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='2d')
        current = round(float(hist['Close'].iloc[-1]), 2)
        yday = round(float(hist['Close'].iloc[0]), 2)
        delta1 = current - yday
        delta2 = round(variation_delta(current, yday), 2)
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

    return data_sheet

def total_invested(stock_dict):
    total_sum = 0.0
    for stock, value in stock_dict.items():
        total_sum += value[1]
    return round(total_sum, 2)

def to_current_sheet(stock_dict):
    print('Saving "Current" value sheet...')

    data_sheet = [['Stock', 'Shares', 'Average (R$)', 'Current (R$)', 'Total (R$)', 'Delta1 (R$)', 'Delta2 (%)']]

    current_value = 0.0
    total_inv = total_invested(stock_dict)

    for stock, value in stock_dict.items():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1d')
        current = round(float(hist['Close'].iloc[0]), 2)
        current_total = round(value[0] * current, 2)
        delta1 = round(current_total - value[1], 2)
        if value[1] != 0:
            delta2 = (100 * delta1) / value[1]
            delta2 = round(delta2, 2)
        else:
            delta2 = 0.0

        data_sheet.append([stock, value[0], calculate_average(value[0], value[1]), current, current_total, delta1, delta2])
        current_value += current_total

    data_sheet.append(['-', '-', '-', '-', '-', '-', '-'])
    data_sheet.append(['Total Inv (R$)', 'Current Val (R$)', 'Delta1 (R$)', 'Delta2 (%)'])

    delta1 = round(current_value - total_inv, 2)
    delta2 = round((100 * delta1) / total_inv, 2)

    data_sheet.append([round(total_inv, 2), round(current_value, 2), delta1, delta2])

    return data_sheet

def to_mkt_cap(stock_dict):
    print('Saving "Mkt Cap" sheet...')

    data_sheet = [['Stock', 'Current (R$)', 'Total Shares', 'Mkt. Cap. (R$)']]

    for stock in stock_dict.keys():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1d')
        current = round(float(hist['Close'].iloc[0]), 2)
        shares = ticker.get_shares_full(start='2023-01-01', end=None)
        shares = int(shares.iloc[-1])
        market = round(shares * current, 2)

        data_sheet.append([stock, current, shares, market])

    return data_sheet

def to_regn_sheet(stock_dict, p='20d'):
    print(f'Saving {p} Regression "Regn" sheet...')

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
        delta1 = round(float(sum_items - total_inv), 2)
        delta2 = round(float((100 * delta1) / total_inv), 2)

        data_sheet.append([date, sum_items, delta1, delta2])

    data_sheet.append(['-', '-', '-', '-'])

    df = pd.DataFrame(df)
    df['Days'] = range(1, days)
    model = LinearRegression()
    model.fit(df[['Days']], df['Close'])
    slope = round(float(model.coef_[0]), 2)
    intercept = round(float(model.intercept_), 2)
    regn = round((slope * float(days)) + intercept, 2)

    data_sheet.append(['Period (days)', 'Forecast (days)', 'Forecast (R$)', 'Slope (R$/day)', 'Intercept (R$)'])
    data_sheet.append([days-1, days, regn, slope, intercept])

    return data_sheet

def to_variation_sheet(stock_dict):
    print('Saving "Var" sheet...')

    data_sheet = [['Stock', 'Current (R$)', '1day (%)', '7day (%)', '30day (%)', '1year (%)']]

    for stock in stock_dict.keys():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1y')
        current = round(float(hist['Close'].iloc[-1]), 2)
        day1 = variation_delta(current, hist['Close'].iloc[-2])
        day7 = variation_delta(current, hist['Close'].iloc[-5])
        day30 = variation_delta(current, hist['Close'].iloc[-22])
        dayY = variation_delta(current, hist['Close'].iloc[0])
        data_sheet.append([stock, current, day1, day7, day30, dayY])

    return data_sheet

def to_stats_sheet(stock_dict, p='2mo'):
    print(f'Saving {p} "Stats" sheet...')

    ibovespa_symbol = "^BVSP"
    ticker = yf.Ticker(ibovespa_symbol)
    hist = ticker.history(period=p)
    ibov_change = hist['Close'].pct_change()

    data_sheet = [['Stock', 'Current (R$)', 'Mean (R$)', 'Std Dev (R$)', 'IBOV Corr', 'C<M', 'C-M', '(C-M)/S']]

    for stock in stock_dict.keys():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period=p)

        current = round(float(hist['Close'].iloc[-1]), 2)
        mean = round(float(hist['Close'].mean()), 2)
        std_dev = round(float(hist['Close'].std()), 2)
        stock_change = hist['Close'].pct_change()
        correlation = float(ibov_change.corr(stock_change))
        test = current < mean
        delta1 = current - mean
        delta2 = round(delta1 / std_dev, 2)

        data_sheet.append([stock, current, mean, std_dev, correlation, test, delta1, delta2])

    return data_sheet

def future_value(present, i, t, alist=[]):
    alist.append(round(present, 2))
    if t == 0:
        return alist
    else:
        fv = 1 + i
        present *= fv
        return future_value(present, i, t-1, alist=alist)

def to_time_sheet(stock_dict, years=10):
    print('Saving "Time" sheet...')

    total_inv = total_invested(stock_dict)

    data_sheet = [['Interest X Years'] + list(range(0, years+1))]

    for i in range(-7,10):
        interest = (1+i) * 0.01
        data_sheet.append([interest] + future_value(total_inv, interest, years, []))

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
    variation_sheet = pe.Sheet(to_variation_sheet(stock_dict), name='Var')
    stats_sheet = pe.Sheet(to_stats_sheet(stock_dict), name='Stats')
    time_sheet = pe.Sheet(to_time_sheet(stock_dict), name='Time')

    pe.save_book_as(bookdict={
        'Stocks': stock_sheet,
        'Beta': current_beta_sheet,
        'Current': current_value_sheet,
        'Mkt Cap': mkt_cap_sheet,
        'Regn': regn_sheet,
        'Var': variation_sheet,
        'Stats': stats_sheet,
        'Time': time_sheet,
        }, dest_file_name=ods_filename)
