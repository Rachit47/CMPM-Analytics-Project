import streamlit as st
import pandas as pd
import pandas_datareader.data as web
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
col1, col2 = st.columns([1,1])
with col1:
	stocks_list = st.multiselect("Select 4 Stocks", ('TSLA','AAPL','NFLX','MSFT','MGM','AMZN','NVEA','GOOGL'),('TSLA','AAPL','AMZN','GOOGL'))
with col2:
	year = st.number_input("Number of years",1,10)

#Downloading Market data for S&P500
try:
	end = datetime.date.today()
	start = datetime.date(datetime.date.today().year-year, datetime.date.today().month, datetime.date.today().day)
	SP500 = web.DataReader(['sp500'],'fred',start,end)
	# print(SP500.head())

	stocks_df = pd.DataFrame() #generating an empty dataframe

	for stock in stocks_list:
		data = yf.download(stock, period = f'{year}y') # collect stock data for the desired number of years
		stocks_df[f'{stock}'] = data['Close'] # generating the dataframe with the stock name and adding the respective 'close' price for each stock

	print(stocks_df.head())

	stocks_df.reset_index(inplace = True)
	SP500.reset_index(inplace = True)
	SP500.columns = ['Date','sp500']
	# dtypes of both the dataframes are different, so we need to convert them before merging
	stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')

	# removing the time values from the date col
	stocks_df['Date'] = stocks_df['Date'].apply(lambda x:str(x)[:10])
	stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
	stocks_df = pd.merge(stocks_df, SP500, on = 'Date', how = 'inner')
	print(stocks_df)

	col1,col2 = st.columns([1,1])
	with col1:
		st.markdown("### Dataframe Top Records")
		st.dataframe(stocks_df.head(), use_container_width = True)
	with col2:
		st.markdown("### Dataframe Last Records")
		st.dataframe(stocks_df.tail(), use_container_width = True)

	col1, col2 = st.columns([1,1])
	with col1:
		st.markdown("### All Stock Prices")
		st.plotly_chart(CMPM_Utilities.interactive_plot(stocks_df))
	with col2:
		st.markdown("### Normalized Stock Prices")
		st.plotly_chart(CMPM_Utilities.interactive_plot(CMPM_Utilities.normalise(stocks_df)))

	stocks_everyday_return = CMPM_Utilities.everyday_return_percent(stocks_df)

	betas = {}
	alphas = {}

	for i in stocks_everyday_return.columns:
		if i != 'Date' and i != 'sp500':
			beta, alpha = CMPM_Utilities.beta_computation(stocks_everyday_return, i)

			betas[i] = beta
			alphas[i] = alpha
	print(betas, alphas)
	beta_df = pd.DataFrame(columns = ['Stock', 'Beta_Value'])
	beta_df['Stock'] = [str(i) for i in betas.keys()]
	beta_df['Beta_Value'] = [str(round(i,2)) for i in betas.values()]

	with col1:
		st.markdown("### CMPM Risk Indicators (Beta Values)")
		st.dataframe(beta_df, use_container_width = True)

	Rf = 0;
	Rm = stocks_everyday_return['sp500'].mean()*252 # Market Portfolio Return for 252 days 
	return_df = pd.DataFrame()
	return_values = []
	for stock, β in betas.items():
		return_values.append(str(round(Rf + (β*(Rm - Rf)),2)))
	return_df['Stock'] = stocks_list

	return_df['Return Values'] = return_values

	with col2:
		st.markdown("### CMPM-Driven Return Evaluation")

		st.dataframe(return_df, use_container_width = True)
except:
	st.write("Kindly select a valid input")
