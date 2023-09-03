#! /usr/bin/python3

import yfinance as yf
import time

stock_dict = {"PETR3.SA": (1000, 35690.0),
              "VALE3.SA": (1000, 68890.0),
}

ibovespa_symbol = "^BVSP"

def track_stock_price(stock_dict):

    stock_list_size = len(stock_dict)
    try:
        oscillation = 0.0

        for stock_symbol in stock_dict.keys():
            stock = yf.Ticker(stock_symbol)
            stock_data = stock.history(period="2d")
            open_price = stock_data["Close"].iloc[0]
            current_price = stock_data["Close"].iloc[1]

            variation = (current_price - open_price) / open_price
            oscillation += variation

        oscillation = oscillation / stock_list_size

        print(f'Index oscillation = {oscillation * 100:.2f}%')

        stock = yf.Ticker(ibovespa_symbol)
        stock_data = stock.history(period="2d")
        open_price = stock_data["Close"].iloc[0]
        current_price = stock_data["Close"].iloc[1]

        variation = (current_price - open_price) / open_price
        print(f'IBOV variation = {variation * 100:.2f}%')

        beta = oscillation / variation
        print(f'BETA (Index/IBOV) = {beta:.2f}')

        print ('\n- - - - - - - - - - - - - - - - - - - - \n')

    except Exception as e:
        print(f"Error: {e}")

def total_invested(stock_dict):
    total_sum = 0.0
    for stock, value in stock_dict.items():
        total_sum += value[1]
    return round(total_sum, 2)

def calculate_average(stock_qty, volume):
    return round(volume/stock_qty, 2)

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

    print("__Stock__|___Avg____|_Current__|__Delta1__|__Delta2__|")
    for stock, value in stock_dict.items():
        average = calculate_average(value[0], value[1])
        current = data_dict[stock]
        delta1 = current - average
        delta2 = delta1 / average
        delta2 = delta2 * 100
        print(f'{stock} | R$ {average:5.2f} | R$ {current:5.2f} | R$ {delta1:5.2f} | {delta2:6.2f}%  |')


if __name__ == "__main__":

    option = 'a'

    while option != 'exit':

        print("To track Beta value, input 'beta' or 'b'")
        print("To track portfolio value, input 'portfolio' or 'p'")
        print("To exit, input 'exit' or 'x'")
        option = input("\nInput option: ")
        if option == 'beta' or option == 'b':
            track_stock_price(stock_dict)
            input()
        elif option == 'portfolio' or option == 'p':
            track_portfolio_value(stock_dict)
            input()
        elif option == 'exit' or option == 'x':
            print("Thanks!")
            break
        else:
            option = input("\nIncorrect option.\nInput option 'beta', 'portfolio' or 'exit':")

