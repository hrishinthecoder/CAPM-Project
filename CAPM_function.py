import plotly.express as px
import numpy as np

def plots(df):
    fig = px.line()
    for i in df.columns[1:]:
        fig.add_scatter(x=df['Date'],y=df[i],name=i)
    fig.update_layout(width=450, margin = dict(l=20,r=20,t=50,b=20),legend = dict(orientation = 'h',yanchor ='bottom',y = 1.02,xanchor='right',x =1))
    return fig

def normalized(df2):
    df = df2.copy()
    for i in df.columns[1:]:
        df[i] = df[i]/df[i][0]
    return df 

def daily_return(df):
    df_daily_return=df.copy()
    for i in df.columns[1:]:
        for j in range(1,len(df)):
            df_daily_return[i][j] = ((df[i][j]-df[i][j-1])/df[i][j-1])*100
        df_daily_return[i][0] = 0
    return df_daily_return

def calculate_beta(stocks_daily_return,stock):
    rm = stocks_daily_return['sp500'].mean()*252
    b,a = np.polyfit(stocks_daily_return['sp500'], stocks_daily_return[stock],1)
    return b,a

def calculate_sharpe_ratio(stocks_daily_return, risk_free_rate=0):
    sharpe_ratios = {}
    for column in stocks_daily_return.columns[1:]:  # Skip 'Date'
        excess_return = stocks_daily_return[column] - risk_free_rate
        sharpe_ratio = excess_return.mean() / excess_return.std()
        sharpe_ratios[column] = sharpe_ratio * (252**0.5)  # Annualize it
    return sharpe_ratios


def calculate_volatility(stocks_daily_return):
    volatilities = {}
    for column in stocks_daily_return.columns[1:]:  # Skip 'Date'
        volatility = stocks_daily_return[column].std() * (252**0.5)  # Annualized
        volatilities[column] = volatility
    return volatilities



def calculate_cumulative_returns(stocks_df):
    cumulative_returns = stocks_df.copy()
    for column in stocks_df.columns[1:]:  # Skip 'Date'
        cumulative_returns[column] = (stocks_df[column] / stocks_df[column].iloc[0]) - 1
    return cumulative_returns


def plot_cumulative_returns(df):
    fig = px.line()
    for i in df.columns[1:]:
        fig.add_scatter(x=df['Date'], y=df[i], name=i)
    fig.update_layout(width=600, margin=dict(l=20, r=20, t=50, b=20), legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    return fig
