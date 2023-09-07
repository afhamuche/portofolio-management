#! /usr/bin/python3

import yfinance as yf
import time
import os
import json
import numpy as np

stock_dict = {}

ibovespa_symbol = "^BVSP"

def track_stock_price(stock_dict):

    stock = yf.Ticker(ibovespa_symbol)
    hist = stock.history(period='2d')
    ibov_var = variation(hist['Close'].iloc[-1], hist['Close'].iloc[0])
    port_var = 0

    print("__Stock__|_Current__|__Open____|__Delta1__|_Delta2_|__Beta__|")
    for stock_symbol in stock_dict.keys():
        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period='2d')
        current = hist['Close'].iloc[-1]
        past = hist['Close'].iloc[0]
        var = variation(current, past)
        beta = var / ibov_var
        delta = current - past
        print(f'{stock_symbol} | R$ {current:5.2f} | R$ {past:5.2f} | R$ {delta:5.2f} | {var:5.2f}% | {beta:5.2f} |')

        port_var += var

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')

    port_var = port_var / len(stock_dict)\

    print(f'Portfolio variation = {port_var:.2f}%')
    print(f'IBOV variatio = {ibov_var:.2f}%')
    print(f'Beta (Port/IBOV) = {port_var / ibov_var:.2f}')



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

    total_inv = total_invested(stock_dict)
    print(f'\nTotal invested is R$ {total_inv:,.2f}')

    total_delta = 0.0
    data_dict = {}

    for stock_symbol, stock_value in stock_dict.items():
        stock = yf.Ticker(stock_symbol)
        stock_data = stock.history(period="1d")
        current_price = stock_data["Close"].iloc[0]
        total_delta += stock_value[0] * current_price
        data_dict.update({stock_symbol: current_price})

    print(f'Current investment is R$ {total_delta:,.2f}')

    total_delta -= total_inv

    print(f"delta1: R$ {total_delta:.2f}")

    total_delta = total_delta / total_inv
    total_delta = total_delta * 100

    print(f"delta2: {total_delta:.2f}%\n")

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')

    print("__Stock__|___Avg____|_Current__|__Delta1__|__Delta2__|___Delta3___|")
    for stock, value in stock_dict.items():
        average = calculate_average(value[0], value[1])
        current = data_dict[stock]
        delta1 = current - average
        delta2 = delta1 / average
        delta2 = delta2 * 100
        delta3 = current * value[0]
        delta3 -= value[1]
        print(f'{stock} | R$ {average:5.2f} | R$ {current:5.2f} | R$ {delta1:5.2f} | {delta2:6.2f}%  | R$ {delta3:7.2f} |')

    print ('\n- - - - - - - - - - - - - - - - - - - - \n')

def show_portfolio(stock_dict):
    print("__Stock__|__Qty._|__Volume___|___Avg____|")
    for stock, value in stock_dict.items():
        average = calculate_average(value[0], value[1])
        print(f'{stock} | {value[0]:5} | R$ {value[1]:,.2f} | R$ {average:5.2f} |')

def show_stock_info(stock_dict):
    print("\n__Stock__|____Shares___|_______Mkt.Cap_______|_Current__|")
    for stock_symbol in stock_dict.keys():
        stock = yf.Ticker(stock_symbol)
        stock_data = stock.history(period='1d')
        current_price = stock_data["Close"].iloc[0]
        stock_data = stock.get_shares_full(start="2023-01-01", end=None)
        shares = stock_data.iloc[-1]
        market = shares * current_price
        print(f"{stock_symbol} | {shares:11,d} | R$ {market:,.2f} | R$ {current_price:5.2f} |")

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
                    volume = float(input("Input amount spent: "))
                    option = input(f'Buy {buy} {stock} for R$ {volume}? Y/n: ')
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
                    volume = float(input("Input amount spent: "))
                    option = input(f"Sell {sell} {stock} for R$ {volume}? Y/n: ")
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
    print("\n__Stock__|__Current_|___1day__|__7days__|_30days__|__365days_|")
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

        print(f"{stock_symbol} | R$ {current:5.2f} | {tmp_list[0]:6.2f}% | {tmp_list[1]:6.2f}% | {tmp_list[2]:6.2f}% | {tmp_list[3]:7.2f}% |")

def portfolio_statistics(stock_dict):
    print("\nData from last 2 months.")
    print("\n__Stock__|Current(c)_|__Mean(m)__|_Std.Dev__|_c<m__|__(c-m)/s_|")
    for stock_symbol in stock_dict.keys():
        ystock = yf.Ticker(stock_symbol)
        hist = ystock.history(period='2mo')
        current = hist['Close'].iloc[-1]
        mean = np.mean(hist['Close'].iloc[:])
        sigma = np.std(hist['Close'].iloc[:])
        test = current - mean
        delta = test / sigma
        delta = delta * 100
        test = test < 0
        print(f'{stock_symbol} | R$ {current:6.2f} | R$ {mean:6.2f} | R$ {sigma:5.2f} | {test:4} | {delta:7.2f}% |')

def welcome():
    print("Show portfolio, input 'show' or 'h'")
    print("Track Beta value, input 'beta' or 'b'")
    print("Track portfolio value, input 'portfolio' or 'p'")
    print("Track portfolio variation, input 'variation' or 'v'")
    print("Track portfolio statistics, input 'stats' or 't'")
    print("Portfolio shares market capitalization info, input 'info' or 'i'\n")

    print("To lookup individual stock 1mo history, input 'history' or 'o'\n")

    print("Edit stock list, input 'edit' or 'e'")
    print("Load stock list, input 'load' or 'l'")
    print("Save stock list, input 'save' or 's'\n")

    print("To exit, input 'exit' or 'x'")

if __name__ == "__main__":

    option = 'a'

    while option != 'exit':
        os.system('clear')
        welcome()

        option = input("\nInput option: ")

        if option == 'beta' or option == 'b':
            track_stock_price(stock_dict)
            input('\nPress [Enter]')

        elif option == 'variation' or option == 'v':
            portfolio_variation(stock_dict)
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

        elif option == 'exit' or option == 'x':
            print("Thanks!")
            break

        elif option == 'show' or option == 'h':
            show_portfolio(stock_dict)
            input('\nPress [Enter]')

        elif option == 'history' or option == 'o':
            stock = input('Input stock ticker to look up in YFinance: ')
            show_stock_history(stock)
            input('\nPress [Enter]')

        elif option == 'load' or option == 'l':
            file_name = input('To load a portfolio, have your .json in the same path as your script.\nInput file name: ')
            if os.path.isfile(file_name):
                with open(file_name, 'r') as json_file:
                    stock_dict = json.load(json_file)
                print(f'\nLoaded file "{file_name}".')
            else:
                print(f'\nFile "{file_name}" does not exist.')
            input('\nPress [Enter]')

        elif option == 'save' or option == 's':
            file_name = input('\nInput save as filename: ')
            if file_name.find('.json') == -1:
                file_name += '.json'
            with open(file_name, 'w') as json_file:
                json.dump(stock_dict, json_file)
            print(f'\nSaved file "{file_name}" in current directory.')
            input('\nPress [Enter]')

        elif option == 'edit' or option == 'e':
            edit_selection(stock_dict)

        else:
            option = input("\nIncorrect option.")
