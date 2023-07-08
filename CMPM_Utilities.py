import plotly.express as px

# Utility to plot interactive plotly chart
import numpy as np
def interactive_plot(df):
	fig = px.line()
	for i in df.columns[1:]:
		fig.add_scatter(x = df['Date'], y = df[i], name = i) # date v/s stock gaphs for each stock
	fig.update_layout(width = 450, margin = dict(l=20, r = 20, t=50, b = 20), legend = dict(orientation = 'h', yanchor = 'bottom', y = 1.02, xanchor = 'right', x = 1,))
	return fig

# Utility to normalise the stock prices based on starting prices
def normalise(orig_df):
	df = orig_df.copy()
	for i in df.columns[1:]:
		df[i] = df[i]/df[i][0]
	return df

# Utility to compute everyday returns
def everyday_return_percent(df):
	df_everyday_return = df.copy()
	for i in df.columns[1:]:
		for j in range(1, len(df)):
			df_everyday_return[i][j] = ((df[i][j]-df[i][j-1])/df[i][j-1])*100
		df_everyday_return[i][0] = 0 # initialising every column's first value to 0
	return df_everyday_return 

# Utility for computing Beta for CAPM
def beta_computation(stocks_everyday_return, stock):
	Rm = stocks_everyday_return['sp500'].mean()*252
	β, α = np.polyfit(stocks_everyday_return['sp500'],stocks_everyday_return[stock],1)
	return β, α 