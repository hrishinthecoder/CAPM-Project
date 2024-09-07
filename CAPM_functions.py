#import necessary libraries
import plotly.express as px
import numpy as np

# function to create line plots
def plots(df):
    fig = px.line()  # create an empty figure
    for i in df.columns[1:]:  # iterate over columns (skipping the 'Date' column)
        fig.add_scatter(x=df['Date'], y=df[i], name=i)  # add scatter plot for each column
    fig.update_layout(width=450, 
                      margin=dict(l=20, r=20, t=50, b=20),  # set layout margins
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))  # update legend
    return fig  # return the figure

# function to normalize data
def normalized(df2):
    df = df2.copy()  # create a copy of the dataframe
    for i in df.columns[1:]:  # iterate over columns (skipping 'Date')
        df[i] = df[i] / df[i][0]  # normalize each column by the first value
    return df  # return normalized dataframe

# function to calculate daily return
def daily_return(df):
    df_daily_return = df.copy()  # create a copy of the dataframe
    for i in df.columns[1:]:  # iterate over columns (skipping 'Date')
        for j in range(1, len(df)):  # iterate over rows, starting from 1
            df_daily_return[i][j] = ((df[i][j] - df[i][j - 1]) / df[i][j - 1]) * 100  # calculate daily return
        df_daily_return[i][0] = 0  # set first value to 0
    return df_daily_return  # return dataframe with daily returns

# function to calculate beta value for a stock
def calculate_beta(stocks_daily_return, stock):
    rm = stocks_daily_return['sp500'].mean() * 252  # calculate annualized market return
    b, a = np.polyfit(stocks_daily_return['sp500'], stocks_daily_return[stock], 1)  # calculate beta using linear regression
    return b, a  # return beta and alpha values

# function to calculate Sharpe ratio
def calculate_sharpe_ratio(stocks_daily_return, risk_free_rate=0):
    sharpe_ratios = {}  # initialize dictionary to store Sharpe ratios
    for column in stocks_daily_return.columns[1:]:  # iterate over columns (skipping 'Date')
        excess_return = stocks_daily_return[column] - risk_free_rate  # calculate excess return
        sharpe_ratio = excess_return.mean() / excess_return.std()  # calculate Sharpe ratio
        sharpe_ratios[column] = sharpe_ratio * (252 ** 0.5)  # annualize the Sharpe ratio
    return sharpe_ratios  # return the dictionary of Sharpe ratios

# function to calculate volatility
def calculate_volatility(stocks_daily_return):
    volatilities = {}  # initialize dictionary to store volatilities
    for column in stocks_daily_return.columns[1:]:  # iterate over columns (skipping 'Date')
        volatility = stocks_daily_return[column].std() * (252 ** 0.5)  # calculate annualized volatility
        volatilities[column] = volatility  # store in the dictionary
    return volatilities  # return the dictionary of volatilities

# function to calculate cumulative returns
def calculate_cumulative_returns(stocks_df):
    cumulative_returns = stocks_df.copy()  # create a copy of the dataframe
    for column in stocks_df.columns[1:]:  # iterate over columns (skipping 'Date')
        cumulative_returns[column] = (stocks_df[column] / stocks_df[column].iloc[0]) - 1  # calculate cumulative return
    return cumulative_returns  # return the dataframe with cumulative returns

# function to plot cumulative returns
def plot_cumulative_returns(df):
    fig = px.line()  # create an empty figure
    for i in df.columns[1:]:  # iterate over columns (skipping 'Date')
        fig.add_scatter(x=df['Date'], y=df[i], name=i)  # add scatter plot for each column
    fig.update_layout(width=600, 
                      margin=dict(l=20, r=20, t=50, b=20),  # set layout margins
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))  # update legend
    return fig  # return the figure
