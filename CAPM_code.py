import pandas as pd
import streamlit as st
import datetime
import yfinance as yf
import CAPM_functions
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title='CAPM', page_icon="chart_with_upwards_trend", layout="wide")
st.title("Capital Asset Pricing Model")

# getting input from user
col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect("Choose 4 stocks", 
                                 ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL', 'META', 'IBM',
                                  'ORCL', 'BABA', 'JPM', 'BAC', 'DIS', 'KO', 'PEP', 'PFE', 'INTC', 'CSCO', 
                                  'COST', 'VZ', 'T', 'WMT', 'HD', 'CVX', 'XOM', 'V', 'MA', 'NKE', 'PG'),
                                 ['TSLA', 'AAPL', 'AMZN', 'GOOGL'])
with col2:
    year = st.number_input("Number of Years", 1, 500)

try:
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)

    # Download stock data for all selected stocks at once
    tickers = " ".join(stocks_list)
    data = yf.download(tickers, start=start, end=end, group_by='ticker')

    stocks_df = pd.DataFrame()
    for stock in stocks_list:
        stock_data = data[stock]['Close'].reset_index()
        stock_data.columns = ['Date', stock]
        stock_data['Date'] = stock_data['Date'].dt.tz_localize(None)
        if stocks_df.empty:
            stocks_df = stock_data
        else:
            stocks_df = pd.merge(stocks_df, stock_data, on='Date', how='inner')

    SP500 = yf.download('^GSPC', start=start, end=end)[['Close']].reset_index()
    SP500.columns = ['Date', 'sp500']
    SP500['Date'] = SP500['Date'].dt.tz_localize(None)
    
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### DataFrame head')
        st.dataframe(stocks_df.head(), use_container_width=True)
    with col2:
        st.markdown('### DataFrame tail')
        st.dataframe(stocks_df.tail(), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Price of all the Stocks')
        st.plotly_chart(CAPM_functions.plots(stocks_df), use_container_width=True)
    with col2:
        st.markdown('### Price of all the Stocks After Normalization')
        st.plotly_chart(CAPM_functions.plots(CAPM_functions.normalized(stocks_df)), use_container_width=True)

    # Multi-threaded daily return calculation for faster execution
    def calculate_returns():
        return CAPM_functions.daily_return(stocks_df)
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(calculate_returns)
        stocks_daily_return = future.result()

    beta = {}
    alpha = {}

    def calculate_beta_alpha(stock):
        if stock in stocks_daily_return.columns:
            return CAPM_functions.calculate_beta(stocks_daily_return, stock)

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(calculate_beta_alpha, stocks_list))
        for i, result in enumerate(results):
            if result:
                beta[stocks_list[i]], alpha[stocks_list[i]] = result

    beta_df = pd.DataFrame({'Stock': list(beta.keys()), 'Beta Value': [str(round(b, 2)) for b in beta.values()]})
    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean() * 252

    return_df = pd.DataFrame()
    return_value = [str(round(rf + (beta[stock] * (rm - rf)), 2)) if stock in beta else "N/A" for stock in stocks_list]
    
    return_df['Stock'] = stocks_list
    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return Value')
        st.dataframe(return_df, use_container_width=True)

    sharpe_ratios = CAPM_functions.calculate_sharpe_ratio(stocks_daily_return)
    sharpe_df = pd.DataFrame({'Stock': list(sharpe_ratios.keys()), 'Sharpe Ratio': [str(round(s, 2)) for s in sharpe_ratios.values()]})
    with col1:
        st.markdown('### Sharpe Ratios')
        st.dataframe(sharpe_df, use_container_width=True)

    volatility = CAPM_functions.calculate_volatility(stocks_daily_return)
    volatility_df = pd.DataFrame({'Stock': list(volatility.keys()), 'Volatility': [str(round(v, 2)) for v in volatility.values()]})
    with col2:
        st.markdown('### Volatility')
        st.dataframe(volatility_df, use_container_width=True)

    st.markdown("## Cumulative Returns")
    cumulative_returns = CAPM_functions.calculate_cumulative_returns(stocks_df)
    st.plotly_chart(CAPM_functions.plot_cumulative_returns(cumulative_returns), use_container_width=True)

except Exception as e:
    st.markdown("<h1 style='color: red;'>Cannot show further. Give a valid input.</h1>", unsafe_allow_html=True)
