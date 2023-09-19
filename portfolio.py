#! /usr/bin/python3

import yfinance as yf
import time
import os
import json
import pandas as pd
from sklearn.linear_model import LinearRegression

stock_dict = {}

ibovespa_symbol = "^BVSP"

def near_time_portfolio(stock_dict):
    option = ''
    while option != 'q':
        os.system('clear')
        for stock_symbol in stock_dict.keys():
            stock = yf.Ticker(stock_symbol)
            hist = stock.history(period='1d')
            df = hist[['Open', 'High', 'Low', 'Close', 'Volume']]
            df.index.name = stock_symbol
            print(df)
        option = input("\n[Enter] to continue.\n'q' to exit.\nInput: ")

def track_stock_price(stock_dict):

    stock = yf.Ticker(ibovespa_symbol)
    hist = stock.history(period='2d')
    ibov_var = variation(hist['Close'].iloc[-1], hist['Close'].iloc[0])
    port_var = 0

    print("\n__Stock___|_Current__|__Close___|__Delta1__|_Delta2_|__Beta__|")
    for stock_symbol in stock_dict.keys():
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period='2d')
        current = hist['Close'].iloc[-1]
        past = hist['Close'].iloc[0]
        var = variation(current, past)
        beta = var / ibov_var
        delta = current - past
        print(f'{stock_symbol:9} | R$ {current:5.2f} | R$ {past:5.2f} | R$ {delta:5.2f} | {var:5.2f}% | {beta:6.2f} |')

        port_var += var

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')

    port_var = port_var / len(stock_dict)

    print(f'Portfolio variation: {port_var:.2f}%')
    print(f'IBOV variation: {ibov_var:.2f}%')
    print(f'Beta (Port/IBOV): {port_var / ibov_var:.2f}')

def total_invested(stock_dict):
    total_sum = 0.0
    for stock, value in stock_dict.items():
        total_sum += value[1]
    return round(total_sum, 2)

def calculate_average(stock_qty, volume):
    if stock_qty > 0:
        return round(volume/stock_qty, 2)
    else:
        return 0.0

def track_portfolio_value(stock_dict):

    total_delta = 0.0

    print("\n__Stock___|___Avg____|_Current__|_Volume(c)__|__Delta1__|__Delta2__|___Delta3___|")
    for stock, value in stock_dict.items():
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1d')
        average = calculate_average(value[0], value[1])
        current = hist['Close'].iloc[0]
        delta1 = current - average

        if average != 0:
            delta2 = delta1 / average
        else:
            delta2 = 0

        delta2 *= 100
        delta3 = current * value[0]
        delta3 -= value[1]
        current_volume = current * value[0]
        total_delta += value[0] * current
        print(f'{stock:9} | R$ {average:5.2f} | R$ {current:5.2f} | R$ {current_volume:8,.2f}| R$ {delta1:5.2f} | {delta2:6.2f}%  | R$ {delta3:7.2f} |')

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')

    total_inv = total_invested(stock_dict)
    print(f'Total invested is R$ {total_inv:,.2f}')
    print(f'Portfolio value is R$ {total_delta:,.2f}')

    total_delta -= total_inv
    print(f"delta1: R$ {total_delta:.2f}")

    if total_inv > 0:
        total_delta = total_delta / total_inv
    else:
        total_delta = 0

    total_delta *= 100
    print(f"delta2: {total_delta:.2f}%")

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')


def show_portfolio(stock_dict):
    print("__Stock___|__Qty._|__Volume_____|___Avg____|")
    for stock, value in stock_dict.items():
        average = calculate_average(value[0], value[1])
        print(f'{stock:9} | {value[0]:5} | R$ {value[1]:8,.2f} | R$ {average:5.2f} |')

def show_stock_info(stock_dict):
    print("\n__Stock___|____Shares___|_______Mkt.Cap_______|_Current__|")
    for stock_symbol in stock_dict.keys():
        stock = yf.Ticker(stock_symbol)
        stock_data = stock.history(period='1d')
        current_price = stock_data["Close"].iloc[0]
        stock_data = stock.get_shares_full(start="2023-01-01", end=None)
        shares = stock_data.iloc[-1]
        market = shares * current_price
        print(f"{stock_symbol:9} | {shares:11,d} | R$ {market:16,.2f} | R$ {current_price:5.2f} |")

def edit_selection(stock_dict):
    while True:
                os.system('clear')
                print('new / delete / buy / sell / back\n')
                show_portfolio(stock_dict)
                option = input('\nInput option: ')

                if option == 'delete':
                    stock = input('Input stock ticker to delete: ')
                    if stock in stock_dict:
                        option = input(f'Delete {stock}? Y/n: ')
                        if option == "Y" or option == 'y':
                            del stock_dict[stock]
                        print(f'Deleted stock {stock}')

                    input("\nTo go back to main menu, input 'back'. [Enter]")

                elif option == 'buy':
                    stock = input('Input stock ticker to buy: ')
                    buy = int(input("Input quantity to buy: "))
                    price = float(input("Input price per share: "))
                    volume = buy * price

                    option = input(f'Buy {buy} {stock} for R$ {price} each? Y/n: ')
                    if option == 'y' or option == 'Y':
                        if stock in stock_dict:
                            value = stock_dict[stock]
                            buy += value[0]
                            volume += value[1]
                        stock_dict[stock] = (buy, volume)
                        print(f'Purchased stock {stock}.')
                    input("\nTo go back to main menu, input 'back'. [Enter]")

                elif option == 'sell':
                    stock = input('Input stock ticker to sell: ')
                    sell = int(input("Input quantity to sell: "))
                    price = float(input("Input price per share: "))
                    volume = sell * price

                    option = input(f"Sell {sell} {stock} for R$ {price} each? Y/n: ")
                    if option == 'y' or option == "Y":
                        if stock in stock_dict:
                            value = stock_dict[stock]
                            if value[0] >= sell:
                                sell = value[0] - sell
                                volume = value[1] - volume
                                stock_dict[stock] = (sell, volume)
                                print(f'Sold stock {stock}.')
                            else:
                                print("Cannot short stocks.")

                        else:
                            print(f"Stock {stock} not found in portfolio.")

                    input("\nTo go back to main menu, input 'back'. [Enter]")

                elif option == 'back':
                    break

                elif option == 'new':
                    option = input('To create a new stock list you will delete current portfolio.\nContinue? Y/n: ')
                    if option == 'y' or option == 'Y':
                        stock_dict = {}
                        print('Created empty stock list. To add stocks, select option "buy".')

                    input("\nTo go back to main menu, input 'back'. [Enter]")

                else:
                    continue

def show_stock_history(stock):
    ystock = yf.Ticker(stock)
    hist = ystock.history(period="1mo")
    print(f'\n{hist}')

def variation(current, past):
    data = current - past
    data = data / past
    return round(data * 100, 2)

def portfolio_variation(stock_dict):
    print("\n__Stock___|__Current_|___1day__|__7days__|_30days__|__365days_|")
    for stock_symbol in stock_dict.keys():
        tmp_list = []
        ystock = yf.Ticker(stock_symbol)
        hist = ystock.history(period='1y')
        current = hist["Close"].iloc[-1]
        data = hist["Close"].iloc[-2]
        tmp_list.append(variation(current, data))
        data = hist["Close"].iloc[-5]
        tmp_list.append(variation(current, data))
        data = hist["Close"].iloc[-22]
        tmp_list.append(variation(current, data))
        data = hist["Close"].iloc[0]
        tmp_list.append(variation(current, data))

        print(f"{stock_symbol:9} | R$ {current:5.2f} | {tmp_list[0]:6.2f}% | {tmp_list[1]:6.2f}% | {tmp_list[2]:6.2f}% | {tmp_list[3]:7.2f}% |")

def portfolio_statistics(stock_dict):
    print("\nData from last 2 months.")
    print("\n__Stock___|Current(c)_|__Mean(m)__|_Std.Dev__|_c<m__|__(c-m)/s_|")
    for stock_symbol in stock_dict.keys():
        ystock = yf.Ticker(stock_symbol)
        hist = ystock.history(period='2mo')
        current = hist['Close'].iloc[-1]
        mean = hist['Close'].iloc[:].mean()
        sigma = hist['Close'].iloc[:].std()
        test = current - mean
        delta = test / sigma
        delta = delta * 100
        test = test < 0
        print(f'{stock_symbol:9} | R$ {current:6.2f} | R$ {mean:6.2f} | R$ {sigma:5.2f} | {test:4} | {delta:7.2f}% |')

def portfolio_ratios(stock_dict):
    print("\n__Stock___|_Current__|_EBITDA_|__ROE___|___ROA__|_Cratio|__50dAvg__|_beta__|")
    for stock_symbol in stock_dict.keys():
        try:
            stock_ticker = yf.Ticker(stock_symbol)
            stock = stock_ticker.info
            current = stock['currentPrice']
            ebitda = stock['ebitdaMargins'] * 100
            roe = stock['returnOnEquity'] * 100
            roa = stock['returnOnAssets'] * 100
            cratio = stock['currentRatio']
            fifty = stock['fiftyDayAverage']
            beta = stock['beta']
            print(f'{stock_symbol:9} | R$ {current:5.2f} | {ebitda:5.2f}% | {roe:5.2f}% | {roa:5.2f}% | {cratio:4.2f}x | R$ {fifty:5.2f} | {beta:5.2f} |')
        except Exception as e:
            continue

def portfolio_regression(stock_dict):

    p = input('\nInput period, e.g. "3d": ')
    tickers = ' '.join(stock_dict.keys())

    tickers = yf.Tickers(tickers)
    hist = tickers.history(period=p)
    closes = hist['Close']

    total_inv = total_invested(stock_dict)

    data_dict = {}
    for index, row in closes.iterrows():
        portfolio = []
        for column_name, value in row.items():
            portfolio.append(round(stock_dict[column_name][0] * value, 2))
        data_dict[index] = portfolio

    days = 1
    df = {'Close': []}
    print('Date_______|____value_____|___delta1____|__delta2_|')
    for key, value in data_dict.items():
        days += 1
        sum_items = 0
        date = key.strftime('%Y-%m-%d')
        for item in value:
            sum_items += item
        df['Close'].append(sum_items)
        delta1 = sum_items - total_inv
        delta2 = delta1 / total_inv
        delta2 *= 100
        print(f'{date} | R$ {sum_items:9,.2f} | R$ {delta1:8,.2f} | {delta2:6.2f}% |')

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')

    df = pd.DataFrame(df)
    df['Days'] = range(1, days)
    model = LinearRegression()
    model.fit(df[['Days']], df['Close'])
    slope = model.coef_[0]
    intercept = model.intercept_
    tomorrow = (slope * float(days)) + intercept
    print(f"{days}-day Linear Regression for portfolio:")
    print(f"Slope: R$ {slope:,.2f} / day")
    print(f"Intercept: R$ {intercept:,.2f}\n")
    print(f'Forecast tomorrow R$ {tomorrow:,.2f}')

def portfolio_time(stock_dict):
    years = int(input('\nInput number of years: '))
    interest = float(input('Input interest rate as a decimal: '))
    columns = range(years + 1)
    data = []
    index = []

    for stock, value in stock_dict.items():
        data.append(future([], value[1], interest, years))
        index.append(stock)

    df = pd.DataFrame(data, columns=columns, index=index)
    df.loc['Total'] = df[:].sum()
    print()
    print(df)

def future(alist, present, i, t):
    alist.append(round(present, 2))
    if t == 0:
        return alist
    else:
        fv = 1 + i
        present *= fv
        return future(alist, present, i, t-1)

def load_portfolio():
    file_name = input('To load a portfolio, have your .json in the same path as your script.\nInput file name: ')

    if os.path.isfile(file_name):
        with open(file_name, 'r') as json_file:
            stock_dict = json.load(json_file)
        print(f'\nLoaded file "{file_name}".')
        return stock_dict
    else:
        print(f'\nFile "{file_name}" does not exist.\nLoaded empty portfolio')
        return {}

def save_portfolio(stock_dict):
    file_name = input('\nInput save as filename: ')
    if file_name.find('.json') == -1:
        file_name += '.json'
    with open(file_name, 'w') as json_file:
        json.dump(stock_dict, json_file)
    print(f'\nSaved file "{file_name}" in current directory.')


def pd2dict_sum(df, stock_dict):
    data_dict = {}
    for index, row in df.iterrows():
        data_dict[index] = 0
        for column_name, value in row.items():
            data_dict[index] += stock_dict[column_name][0] * value
    return data_dict

def portfolio_reg_candles(stock_dict):
    p = input('\nInput period, e.g. "3d": ')
    tickers = ' '.join(stock_dict.keys())

    tickers = yf.Tickers(tickers)
    hist = tickers.history(period=p)

    closes_dict = pd2dict_sum(hist['Close'], stock_dict)
    highs_dict = pd2dict_sum(hist['High'], stock_dict)
    lows_dict = pd2dict_sum(hist['Low'], stock_dict)

    data_dict = {}
    days = 1
    for key, value in closes_dict.items():
        date = key.strftime('%Y-%m-%d')
        data_dict[date] = [round(value, 2),
                           round(highs_dict[key], 2),
                           round(lows_dict[key], 2),
                           round(highs_dict[key] - lows_dict[key], 2)]
        days += 1

    df = pd.DataFrame(data_dict).transpose()

    columns = ['Close', 'High', 'Low', 'Range']
    df.columns = columns

    print(df)

    print(f"\n{days}-day Linear Regression for portfolio:")
    df['Days'] = range(1, days)

    for category in columns[:-1]:
        model = LinearRegression()
        model.fit(df[['Days']], df[category])
        slope = model.coef_[0]
        intercept = model.intercept_
        tomorrow = (slope * float(days)) + intercept
        print(f'{category} forecast tomorrow R$ {tomorrow:,.2f} | Slope R$/day {slope:.2f} | Intercept R$ {intercept:,.2f}')

def portfolio_sharpe(stock_dict):

    risk_free = float(input('\nInput period annual risk-free rate: '))
    tickers = ' '.join(stock_dict.keys())
    tickers = yf.Tickers(tickers)
    hist = tickers.history(period='1y')

    data_series = pd.Series(pd2dict_sum(hist['Close'], stock_dict).values())
    mean_data = data_series.mean()
    std_data = data_series.std()

    var_change = data_series.pct_change()
    std_daily = float(var_change.std())
    mean_daily = float(var_change.mean())
    sharpe = (mean_daily - risk_free) / std_daily

    print(f'\nStd Daily: {std_daily * 100:.2f}% | R$ {std_data:.2f} |')
    print(f'Mean Daily: {mean_daily * 100:.2f}% | R$ {mean_data:,.2f} | ')
    print(f'Risk-free: {risk_free * 100:.2f}%')
    print(f'\nSharpe Ratio: {sharpe:.2f}')
    sharpe_annual = sharpe * (252**0.5)
    print(f'Sharpe Annual: {sharpe_annual:.2f}')

def welcome():
    print("Last portfolio prices \t\t\tinput 'last' or 'a'")
    print("Track Beta value \t\t\tinput 'beta' or 'b'")
    print("Portfolio candles reg\t\t\tinput 'candles' or 'c'")
    print("Portfolio regression \t\t\tinput 'reg' or 'g'")
    print("Show portfolio \t\t\t\tinput 'show' or 'h'")
    print("Portfolio market capitalization info \tinput 'info' or 'i'")
    print("Portfolio Sharpe ratio\t\t\tinput 'sharpe' or 'j'")
    print("Portfolio future value\t\t\tinput 'time' or 'm'")
    print("Track portfolio value \t\t\tinput 'portfolio' or 'p'")
    print("Track stocks ratio \t\t\tinput 'ratio' or 'r'")
    print("Track portfolio statistics \t\tinput 'stats' or 't'")
    print("Track portfolio variation \t\tinput 'variation' or 'v'")
    print()
    print("To lookup a stock 1mo history\t\tinput 'history' or 'o'")
    print()
    print("Edit stock list\t\t\tinput 'edit' or 'e'")
    print("Load stock list\t\t\tinput 'load' or 'l'")
    print("Save stock list\t\t\tinput 'save' or 's'\n")

    print("To exit\t\t\t\tinput 'exit' or 'q'")

if __name__ == "__main__":

    option = 'a'
    stock_dict = load_portfolio()
    input('\nPress [Enter]')

    while option != 'exit':
        try:
            os.system('clear')
            welcome()

            option = input("\nInput option: ")

            if option == 'beta' or option == 'b':
                track_stock_price(stock_dict)
                input('\nPress [Enter]')

            elif option == 'time' or option == 'm':
                portfolio_time(stock_dict)
                input('\nPress [Enter]')

            elif option == 'candles' or option == 'c':
                portfolio_reg_candles(stock_dict)
                input('\nPress [Enter]')

            elif option == 'last' or option == 'a':
                near_time_portfolio(stock_dict)

            elif option == 'reg' or option == 'g':
                portfolio_regression(stock_dict)
                input('\nPress [Enter]')

            elif option == 'variation' or option == 'v':
                portfolio_variation(stock_dict)
                input('\nPress [Enter]')

            elif option == 'ratio' or option == 'r':
                portfolio_ratios(stock_dict)
                input('\nPress [Enter]')

            elif option == 'sharpe' or option == 'j':
                portfolio_sharpe(stock_dict)
                input('\nPress [Enter]')

            elif option == 'stats' or option == 't':
                portfolio_statistics(stock_dict)
                input('\nPress [Enter]')

            elif option == 'info' or option == 'i':
                show_stock_info(stock_dict)
                input('\nPress [Enter]')

            elif option == 'portfolio' or option == 'p':
                track_portfolio_value(stock_dict)
                show_portfolio(stock_dict)
                input('\nPress [Enter]')

            elif option == 'quit' or option == 'q':
                print("Thanks!")
                break

            elif option == 'show' or option == 'h':
                show_portfolio(stock_dict)
                input('\nPress [Enter]')

            elif option == 'history' or option == 'o':
                stock = input('\nInput stock ticker to look up in YFinance: ')
                show_stock_history(stock)
                input('\nPress [Enter]')

            elif option == 'load' or option == 'l':
                stock_dict = load_portfolio()
                input('\nPress [Enter]')

            elif option == 'save' or option == 's':
                save_portfolio(stock_dict)
                input('\nPress [Enter]')

            elif option == 'edit' or option == 'e':
                edit_selection(stock_dict)

            else:
                input("\nIncorrect option. [Enter]")

        except Exception as e:
            print(e)
            input('\n\nException caught\n\n[Enter]')
            continue
