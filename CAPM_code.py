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
    stocks_list = st.multiselect("Choose 4 stocks", ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVDA', 'GOOGL'),
                                 ['TSLA', 'AAPL', 'AMZN', 'GOOGL'])
with col2:
    year = st.number_input("Number of Years", 1, 500)

try:
    # Optimizing API calls by downloading all stock data at once
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)

    # Download data for multiple stocks at once
    tickers = " ".join(stocks_list)
    data = yf.download(tickers, start=start, end=end, group_by='ticker')

    # Create the stocks dataframe by extracting closing prices of each stock
    stocks_df = pd.DataFrame()
    for stock in stocks_list:
        stock_data = data[stock]['Close'].reset_index()
        stock_data.columns = ['Date', stock]
        
        # Ensure Date is without timezone (datetime64[ns])
        stock_data['Date'] = stock_data['Date'].dt.tz_localize(None)

        if stocks_df.empty:
            stocks_df = stock_data
        else:
            stocks_df = pd.merge(stocks_df, stock_data, on='Date', how='inner')

    # Download SP500 data
    SP500 = yf.download('^GSPC', start=start, end=end).reset_index()[['Date', 'Close']]
    SP500.columns = ['Date', 'sp500']

    # Ensure SP500 'Date' column is without timezone (datetime64[ns])
    SP500['Date'] = SP500['Date'].dt.tz_localize(None)
    
    # Merge stocks data with SP500 data
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    # Display DataFrames
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### DataFrame head')
        st.dataframe(stocks_df.head(), use_container_width=True)
    with col2:
        st.markdown('### DataFrame tail')
        st.dataframe(stocks_df.tail(), use_container_width=True)

    # Plot stock prices
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Price of all the Stocks')
        st.plotly_chart(CAPM_functions.plots(stocks_df),use_container_width=True)
    with col2:
        st.markdown('### Price of all the Stocks After Normalization')
        st.plotly_chart(CAPM_functions.plots(CAPM_functions.normalized(stocks_df)),use_container_width=True)

    # Multi-threaded daily return calculation for faster execution
    def calculate_returns():
        return CAPM_functions.daily_return(stocks_df)
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(calculate_returns)
        stocks_daily_return = future.result()

    # Multi-threaded beta and alpha calculation
    beta = {}
    alpha = {}
    
    def calculate_beta_alpha(stock):
        if stock in stocks_daily_return.columns:
            return CAPM_functions.calculate_beta(stocks_daily_return, stock)
    
    # Using threads to calculate beta and alpha for each stock
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(calculate_beta_alpha, stocks_list))
        for i, result in enumerate(results):
            if result:
                beta[stocks_list[i]], alpha[stocks_list[i]] = result

    # Display calculated Beta values
    beta_df = pd.DataFrame({'Stock': list(beta.keys()), 'Beta Value': [str(round(b, 2)) for b in beta.values()]})
    with col1:
        st.markdown('### Calculated Beta Value')
        st.dataframe(beta_df, use_container_width=True)

    # Calculate return values using CAPM
    rf = 0  # Assuming risk-free rate is 0 for simplicity
    rm = stocks_daily_return['sp500'].mean() * 252  # Assuming 252 trading days in a year

    return_df = pd.DataFrame()
    return_value = []

    for stock in stocks_list:
        if stock in beta:
            return_value.append(str(round(rf + (beta[stock] * (rm - rf)), 2)))
        else:
            return_value.append("N/A")  # In case beta is not calculated for a stock

    return_df['Stock'] = stocks_list
    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return Value')
        st.dataframe(return_df, use_container_width=True)

    # New Feature: Calculate and display Sharpe Ratios
    col1, col2 = st.columns([1, 1])

    sharpe_ratios = CAPM_functions.calculate_sharpe_ratio(stocks_daily_return)
    sharpe_df = pd.DataFrame({'Stock': list(sharpe_ratios.keys()), 'Sharpe Ratio': [str(round(s, 2)) for s in sharpe_ratios.values()]})
    with col1:

        st.markdown('### Sharpe Ratios')
        st.dataframe(sharpe_df, use_container_width=True)

    # New Feature: Calculate and display Volatility
    volatility = CAPM_functions.calculate_volatility(stocks_daily_return)
    volatility_df = pd.DataFrame({'Stock': list(volatility.keys()), 'Volatility': [str(round(v, 2)) for v in volatility.values()]})
    with col2:

        st.markdown('### Volatility')
        st.dataframe(volatility_df, use_container_width=True)

    # New Feature: Plot Cumulative Returns
   # New Feature: Plot Cumulative Returns in its own dedicated section
    st.markdown("## Cumulative Returns")
    st.markdown("The cumulative returns of the selected stocks over the specified period:")

# Calculate cumulative returns using the function from CAPM_VIZZ
    cumulative_returns = CAPM_functions.calculate_cumulative_returns(stocks_df)

# Plot the cumulative returns in a larger, fully visible section
    st.plotly_chart(CAPM_functions.plot_cumulative_returns(cumulative_returns), use_container_width=True)


except Exception as e:
     st.markdown("<h1 style='color: red;'>Cannot show further. Give a valid input.</h1>", unsafe_allow_html=True)
