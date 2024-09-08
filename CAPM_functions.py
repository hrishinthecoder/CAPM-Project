import plotly.express as px
import numpy as np
import pandas as pd

# Function to create line plots
def plots(df):
    fig = px.line(df, x='Date', y=df.columns[1:], labels={'value': 'Values'})  # Create line plot
    fig.update_layout(
        width=450, 
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

# Function to normalize data
def normalized(df):
    return df.assign(**{col: df[col] / df[col].iloc[0] for col in df.columns[1:]})

# Function to calculate daily return
def daily_return(df):
    return df.assign(**{col: df[col].pct_change().fillna(0) * 100 for col in df.columns[1:]})

# Function to calculate beta value for a stock
def calculate_beta(stocks_daily_return, stock):
    market_return = stocks_daily_return['sp500'].mean() * 252  # Annualized market return
    beta, alpha = np.polyfit(stocks_daily_return['sp500'], stocks_daily_return[stock], 1)
    return beta, alpha

# Function to calculate Sharpe ratio
def calculate_sharpe_ratio(stocks_daily_return, risk_free_rate=0):
    sharpe_ratios = {
        col: ((stocks_daily_return[col] - risk_free_rate).mean() / stocks_daily_return[col].std()) * np.sqrt(252)
        for col in stocks_daily_return.columns[1:]
    }
    return sharpe_ratios

# Function to calculate volatility
def calculate_volatility(stocks_daily_return):
    return {col: stocks_daily_return[col].std() * np.sqrt(252) for col in stocks_daily_return.columns[1:]}

# Function to calculate cumulative returns
def calculate_cumulative_returns(stocks_df):
    return stocks_df.assign(**{col: (stocks_df[col] / stocks_df[col].iloc[0]) - 1 for col in stocks_df.columns[1:]})

# Function to plot cumulative returns
def plot_cumulative_returns(df):
    fig = px.line(df, x='Date', y=df.columns[1:], labels={'value': 'Cumulative Return'})
    fig.update_layout(
        width=600, 
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig
