import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import CMPM_Utilities

st.set_page_config(page_title="CMPM", page_icon="chart_with_upward_trend", layout='wide')
st.write(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');
body, .stApp {{
    font-family: 'Orbitron', sans-serif;
}}
</style>
""", unsafe_allow_html=True)
st.title("Capital Market Pricing Model")

# Prompting for user input
col1, col2 = st.columns([1, 1])
with col1:
    stocks_list = st.multiselect(
        "Select 4 Stocks",
        ('TSLA', 'AAPL', 'NFLX', 'MSFT', 'MGM', 'AMZN', 'NVEA', 'GOOGL'),
        ('TSLA', 'AAPL', 'AMZN', 'GOOGL')
    )
with col2:
    year = st.number_input("Number of years", 1, 10)

# Downloading Market data for S&P500
try:
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
    SP500 = yf.download('^GSPC', start, end)

    stocks_df = pd.DataFrame()

    for stock in stocks_list:
        data = yf.Ticker(stock).history(period=f'{year}y')
        stocks_df[stock] = data['Close']

    st.write(stocks_df.head())

    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)
    SP500.columns = ['Date', 'sp500']
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date']).dt.date
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Dataframe Top Records")
        st.dataframe(stocks_df.head(), use_container_width=True)
    with col2:
        st.markdown("### Dataframe Last Records")
        st.dataframe(stocks_df.tail(), use_container_width=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### All Stock Prices")
        st.plotly_chart(CMPM_Utilities.interactive_plot(stocks_df))
    with col2:
        st.markdown("### Normalized Stock Prices")
        st.plotly_chart(CMPM_Utilities.interactive_plot(CMPM_Utilities.normalise(stocks_df)))

    stocks_everyday_return = CMPM_Utilities.everyday_return_percent(stocks_df)

    betas = {}
    alphas = {}

    for stock in stocks_list:
        if stock != 'sp500':
            beta, alpha = CMPM_Utilities.beta_computation(stocks_everyday_return, stock)
            betas[stock] = beta
            alphas[stock] = alpha

    beta_df = pd.DataFrame({'Stock': list(betas.keys()), 'Beta_Value': list(betas.values())})

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### CMPM Risk Indicators (Beta Values)")
        st.dataframe(beta_df, use_container_width=True)

    Rf = 0
    Rm = stocks_everyday_return['sp500'].mean() * 252
    return_values = [round(Rf + (beta * (Rm - Rf)), 2) for beta in betas.values()]
    return_df = pd.DataFrame({'Stock': stocks_list, 'Return Values': return_values})

    with col2:
        st.markdown("### CMPM-Driven Return Evaluation")
        st.dataframe(return_df, use_container_width=True)

except Exception as e:
    st.write("Error occurred:", str(e))
