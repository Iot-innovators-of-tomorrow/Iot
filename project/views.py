import time

from django.shortcuts import render,HttpResponse,redirect
import requests
import numpy as np
from .models import Stock
from .serializers import ImageUploadSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import os
from django.views.decorators.csrf import csrf_exempt
def home_page(request):
    if request.method =="POST":
        # Main code
        investment_amount = int(request.POST.get("amount"))

        # Input the period the user is ready to expect (in months)
        period = int(request.POST.get("months"))

        # Define stock symbols
        stock_symbols = request.POST.getlist("ticker")

        # Fetch stock prices and calculate expected returns
        stock_prices = [ ]
        closing_prices_matrix = prepare_matrix(stock_symbols)

        # Calculate expected returns
        expected_returns = calculate_expected_return(closing_prices_matrix)
        for i, symbol in enumerate(stock_symbols):
            print(f"Expected Annual Return for {symbol}: {expected_returns[ i ]:.2f}%")
        for symbol in stock_symbols:
            try:
                historical_data = get_historical_data(symbol)
                # Get the latest stock price
                first_key, first_value = next(iter(historical_data.items( )))
                latest_price = float(first_value[ '4. close' ])
                stock_prices.append(latest_price)
            except ValueError as e:
                print(e)
                exit( )

        # Allocate portfolio using proportional allocation based on expected returns
        portfolio, initial_weights = allocate_portfolio_proportionally(investment_amount, expected_returns)

        # Print initial portfolio allocation
        print_portfolio(portfolio, stock_prices, stock_symbols)

        # Calculate final values and weights
        final_values = calculate_final_values(portfolio, expected_returns)
        final_weights, total_final_value = calculate_weights(final_values)

        # Print the final portfolio weights and total value after the given period
        print("\nPortfolio Weights After the Given Period:")
        for i in range(len(stock_symbols)):
            print(f"Weight of {stock_symbols[ i ]}: {final_weights[ i ]:.2%}")

        print(f"\nTotal Portfolio Value After the Given Period: ${total_final_value:.2f}")


        return redirect("output")
    return render(request,template_name="homepage.html",)

def initial_page(request):
    if request.method =="POST":
        # Main code
        investment_amount = int(request.POST.get("amount"))

        # Input the period the user is ready to expect (in months)
        period = int(request.POST.get("months"))

        # Define stock symbols
        stock_symbols = request.POST.getlist("ticker")

        # Fetch stock prices and calculate expected returns
        stock_prices = [ ]
        closing_prices_matrix = prepare_matrix(stock_symbols)

        # Calculate expected returns
        expected_returns = calculate_expected_return(closing_prices_matrix)
        for i, symbol in enumerate(stock_symbols):
            print(f"Expected Annual Return for {symbol}: {expected_returns[ i ]:.2f}%")
        for symbol in stock_symbols:
            try:
                historical_data = get_historical_data(symbol)
                # Get the latest stock price
                first_key, first_value = next(iter(historical_data.items( )))
                latest_price = float(first_value[ '4. close' ])
                stock_prices.append(latest_price)
            except ValueError as e:
                print(e)
                exit( )

        # Allocate portfolio using proportional allocation based on expected returns
        portfolio, initial_weights = allocate_portfolio_proportionally(investment_amount, expected_returns)

        # Print initial portfolio allocation
        print_portfolio(portfolio, stock_prices, stock_symbols)

        # Calculate final values and weights
        final_values = calculate_final_values(portfolio, expected_returns)
        final_weights, total_final_value = calculate_weights(final_values)

        # Print the final portfolio weights and total value after the given period
        print("\nPortfolio Weights After the Given Period:")
        for i in range(len(stock_symbols)):
            print(f"Weight of {stock_symbols[ i ]}: {final_weights[ i ]:.2%}")

        print(f"\nTotal Portfolio Value After the Given Period: ${total_final_value:.2f}")


        return redirect("output")
    return render(request,template_name="index.html",)


def get_historical_data(symbol, outputsize='compact'):
    """Function to get historical stock data from Alpha Vantage."""
    obj, get_data = Stock.objects.get_or_create(ticker=symbol)
    if get_data or not obj.data:
        api_key = "7LGYFHVE31AEQKRR"
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={outputsize}&apikey={api_key}"
        response = requests.get(url)
        data = response.json()
        obj.data=data
        obj.save()
        return data["Time Series (Daily)"]

    return obj.data["Time Series (Daily)"]

def prepare_matrix(stock_symbols):
    """Prepare the matrix of closing prices for the given stock symbols."""
    all_closing_prices = []
    dates = None
    for symbol in stock_symbols:
        historical_data = get_historical_data(symbol)
        if dates is None:
            dates = sorted(historical_data.keys())
        closing_prices = [float(historical_data[date]['4. close']) for date in dates]
        all_closing_prices.append(closing_prices)
    # Convert list of lists into a numpy array and transpose it to have dates as rows and tickers as columns
    closing_prices_matrix = np.array(all_closing_prices).T  # Shape: (num_dates, num_tickers)
    # print(closing_prices_matrix)
    return closing_prices_matrix

def calculate_expected_return(closing_prices_matrix):
    """Calculate expected return based on historical data."""
    # Calculate daily returns
    cs = closing_prices_matrix
    for j in range(cs.shape[ 1 ]):  # Iterate over each column
        for i in range(cs.shape[ 0 ] - 1):  # Iterate over each row except the last one
            cs[ i, j ] = cs[ i, j ] - cs[ i + 1, j ]

    avg_daily_returns = np.mean(closing_prices_matrix[:-1, :], axis=0)
    print(avg_daily_returns)
    to_return = [number  for number in avg_daily_returns]
    return to_return # Return in percentage # Return in percentage
#%%

def allocate_portfolio_proportionally(investment_amount, expected_returns):
    """Function to allocate the portfolio based on expected returns proportionally."""
    total_expected_return = sum(expected_returns)
    weights = [ret / total_expected_return for ret in expected_returns]
    portfolio = [int(investment_amount)* weight for weight in weights]
    return portfolio, weights
#%%

def print_portfolio(portfolio, stock_prices, stock_symbols):
    """Function to print the initial portfolio allocation."""
    print("Portfolio Allocation for Maximum Profit:")
    to_return = []
    for i in range(len(portfolio)):
        num_shares = portfolio[i] / stock_prices[i]
        to_return.append(num_shares)
        print(f"Buy {num_shares:.2f} shares of {stock_symbols[i]} (total ${portfolio[i]:.2f}) at price ${stock_prices[i]:.2f}")
    return to_return
#%%

def calculate_final_values(portfolio, expected_returns,period):
    """Function to calculate the final value of each stock in the portfolio after the given period."""
    final_values = [portfolio[i] * (expected_returns[i] / 100) * period for i in range(len(portfolio))]
    return final_values
#%%

def calculate_weights(final_values):
    """Function to calculate the portfolio weights based on final values."""
    print(final_values)
    total_value = sum(final_values)
    weights = [value / total_value for value in final_values]
    return weights, total_value


def investment_summary_view(request):
    # Define object symbols
    stock_symbols = request.POST.getlist("ticker")
    time.sleep(5)
    if "smartphone" in stock_symbols :
        context = {
            "image":"static/images/image_phone.jpg"
        }
    else:
        context = {
            "image": "static/images/laptop_laptop.jpg"
        }
    return render(request, 'output.html', context)


@csrf_exempt
@api_view(['POST'])
def upload_image(request):
    # Initialize the serializer with the incoming data
    serializer = ImageUploadSerializer(data=request.data)

    if serializer.is_valid():
        # Get the camera index and file from the request
        camera_index = serializer.validated_data['camera_index']
        uploaded_file = serializer.validated_data['file']

        # Save the uploaded file (you can change the directory as needed)
        file_path = os.path.join('C:/Users/Sarvar/Desktop/INHA/5th Semester/IOT/project/Iot/found_images', f"Camera{camera_index}_{uploaded_file.name}")
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        return Response({"message": f"File received from Camera {camera_index} and saved to {file_path}."}, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
