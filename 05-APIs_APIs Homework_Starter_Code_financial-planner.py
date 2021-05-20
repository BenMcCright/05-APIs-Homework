#!/usr/bin/env python
# coding: utf-8

# # Unit 5 - Financial Planning
# 

# In[63]:


# Initial imports
import os
import requests
import pandas as pd
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from datetime import date, timedelta
from MCForecastTools import MCSimulation

get_ipython().run_line_magic('matplotlib', 'inline')


# In[64]:


# Load .env enviroment variables
load_dotenv()


# ## Part 1 - Personal Finance Planner

# ### Collect Crypto Prices Using the `requests` Library

# In[65]:


# Set current amount of crypto assets
my_btc = 1.2
my_eth = 5.3


# In[66]:


# Crypto API URLs
btc_url = "https://api.alternative.me/v2/ticker/Bitcoin/?convert=CAD"
eth_url = "https://api.alternative.me/v2/ticker/Ethereum/?convert=CAD"


# In[100]:


# Fetch current BTC price
btc_get = requests.get(btc_url).json()
btc_price = btc_get["data"]["1"]["quotes"]["USD"]["price"]

# Fetch current ETH price
eth_get = requests.get(eth_url).json()
eth_price = eth_get["data"]["1027"]["quotes"]["USD"]["price"]

# Compute current value of my crpto
my_btc_value = my_btc * btc_price
my_eth_value = my_eth * eth_price
my_crypto_total_value = my_btc_value + my_eth_value

# Print current crypto wallet balance
print(f"The current value of your {my_btc} BTC is ${my_btc_value:0.2f}")
print(f"The current value of your {my_eth} ETH is ${my_eth_value:0.2f}")


# ### Collect Investments Data Using Alpaca: `SPY` (stocks) and `AGG` (bonds)

# In[68]:


# Current amount of shares
my_spy = 50
my_agg = 200


# In[69]:


# Set Alpaca API key and secret
alpaca_key = os.getenv("ALPACA_API_KEY")
alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
alpaca_base_url = os.getenv("ALPACA_BASE_URL")


# In[70]:


# Create the Alpaca API object
alpaca = tradeapi.REST(alpaca_key, alpaca_secret)


# In[179]:


# Format current date as ISO format
start = date.today().isoformat()
end = date.today().isoformat()

# Set the tickers
tickers = ["SPY", "AGG"]

# Set timeframe to '1D' for Alpaca API
timeframe = "1D"

# Get current closing prices for SPY and AGG
close = pd.Timestamp(today, tz = "US/Central").isoformat()
agg_spy = alpaca.get_barset(tickers, timeframe, start = start, end = end).df

# Preview DataFrame
agg_spy.tail()


# In[96]:


# Pick AGG and SPY close prices
agg_close_price = agg_spy.iloc[0,3]
spy_close_price = agg_spy.iloc[0,8]
# Print AGG and SPY close prices
print(f"Current AGG closing price: ${agg_close_price}")
print(f"Current SPY closing price: ${spy_close_price}")


# In[104]:


# Compute the current value of shares
my_agg_value = my_agg * agg_close_price
my_spy_value = my_spy * spy_close_price
my_stocks_total_value = my_agg_value + my_spy_value

# Print current value of share
print(f"The current value of your {my_spy} SPY shares is ${my_spy_value:0.2f}")
print(f"The current value of your {my_agg} AGG shares is ${my_agg_value:0.2f}")


# ### Savings Health Analysis

# In[105]:


# Set monthly household income
monthly_income = 12000

# Create savings DataFrame
savings = [{"Savings" : my_crypto_total_value}, {"Savings" : my_stocks_total_value}]
savings_df = pd.DataFrame(savings, index = ["Crypto", "Stocks"])
savings_total = my_crypto_total_value + my_stocks_total_value

# Display savings DataFrame
display(savings_df)


# In[108]:


# Plot savings pie chart
savings_df.plot.pie(y = "Savings", figsize = (10, 8))
display(savings_df)


# In[112]:


# Set ideal emergency fund
emergency_fund = monthly_income * 3

# Calculate total amount of savings
total_savings = my_crypto_total_value + my_stocks_total_value

# Validate saving health
print(f"Your savings are greater than the needs of your emergency fund") if total_savings > emergency_fund else print(f"You need to increase your savings by ${emergency_fund - total_savings}")


# ## Part 2 - Retirement Planning
# 
# ### Monte Carlo Simulation

# In[174]:


# Set start and end dates of five years back from today.
# Sample results may vary from the solution based on the time frame chosen
today = date.today().isoformat()
start_date = pd.Timestamp(today).isoformat()
five_years_back = (date.today() - timedelta(days = 5 * 252)).isoformat()
end_date = pd.Timestamp(five_years_back).isoformat()


# In[180]:


# Get 5 years' worth of historical data for SPY and AGG
df_stock_data = alpaca.get_barset(tickers, timeframe, start = start_date, end = end_date , limit = 1000).df

# Display sample data
df_stock_data.tail()


# In[183]:


# Configuring a Monte Carlo simulation to forecast 30 years cumulative returns
mc_sim = MCSimulation(df_stock_data, [0.4, 0.6], 500, 30*252)


# In[184]:


# Printing the simulation input data
df_stock_data


# In[185]:


# Running a Monte Carlo simulation to forecast 30 years cumulative returns
mc_sim.calc_cumulative_return()


# In[188]:


# Plot simulation outcomes
mc_sim.plot_simulation()


# In[189]:


# Plot probability distribution and confidence intervals
mc_sim.plot_distribution()


# ### Retirement Analysis

# In[190]:


# Fetch summary statistics from the Monte Carlo simulation results
mc_sim_results = mc_sim.summarize_cumulative_return()

# Print summary statistics
print(mc_sim_results)


# ### Calculate the expected portfolio return at the 95% lower and upper confidence intervals based on a `$20,000` initial investment.

# In[193]:


# Set initial investment
initial_investment = 20000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $20,000
ci_lower = round(mc_sim_results.loc["95% CI Lower"] * initial_investment,2)
ci_upper = round(mc_sim_results.loc["95% CI Upper"] * initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 30 years will end within in the range of"
      f" ${ci_lower} and ${ci_upper}")


# ### Calculate the expected portfolio return at the `95%` lower and upper confidence intervals based on a `50%` increase in the initial investment.

# In[195]:


# Set initial investment
initial_investment = 20000 * 1.5

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $30,000
ci_lower = round(mc_sim_results.loc["95% CI Lower"] * initial_investment,2)
ci_upper = round(mc_sim_results.loc["95% CI Upper"] * initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 30 years will end within in the range of"
      f" ${ci_lower} and ${ci_upper}")


# ## Optional Challenge - Early Retirement
# 
# 
# ### Five Years Retirement Option

# In[198]:


# Configuring a Monte Carlo simulation to forecast 5 years cumulative returns
mc_sim_retirement = MCSimulation(df_stock_data, [0.25, 0.75], 500, 5 * 252)


# In[199]:


# Running a Monte Carlo simulation to forecast 5 years cumulative returns
mc_sim_retirement.calc_cumulative_return()


# In[200]:


# Plot simulation outcomes
mc_sim_retirement.plot_simulation()


# In[201]:


# Plot probability distribution and confidence intervals
mc_sim_retirement.plot_distribution()


# In[202]:


# Fetch summary statistics from the Monte Carlo simulation results
mc_sim_retirement_summary = mc_sim_retirement.summarize_cumulative_return()

# Print summary statistics
print(mc_sim_retirement_summary)


# In[204]:


# Set initial investment
initial_investment = 20000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower_five = round(mc_sim_retirement_summary.loc["95% CI Lower"] * initial_investment,2)
ci_upper_five = round(mc_sim_retirement_summary.loc["95% CI Upper"] * initial_investment,2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 5 years will end within in the range of"
      f" ${ci_lower_five} and ${ci_upper_five}")


# ### Ten Years Retirement Option

# In[205]:


# Configuring a Monte Carlo simulation to forecast 10 years cumulative returns
mc_sim_ten = MCSimulation(df_stock_data, [0.25, 0.75], 500, 10 * 252)


# In[206]:


# Running a Monte Carlo simulation to forecast 10 years cumulative returns
mc_sim_ten.calc_cumulative_return()


# In[207]:


# Plot simulation outcomes
mc_sim_ten.plot_simulation()


# In[208]:


# Plot probability distribution and confidence intervals
mc_sim_ten.plot_distribution()


# In[209]:


# Fetch summary statistics from the Monte Carlo simulation results
mc_sim_ten_summary = mc_sim_ten.summarize_cumulative_return()

# Print summary statistics
print(mc_sim_ten_summary)


# In[211]:


# Set initial investment
initial_investment = 60000

# Use the lower and upper `95%` confidence intervals to calculate the range of the possible outcomes of our $60,000
ci_lower_ten = round(mc_sim_ten_summary.loc["95% CI Lower"] * initial_investment, 2)
ci_upper_ten = round(mc_sim_ten_summary.loc["95% CI Upper"] * initial_investment, 2)

# Print results
print(f"There is a 95% chance that an initial investment of ${initial_investment} in the portfolio"
      f" over the next 10 years will end within in the range of"
      f" ${ci_lower_ten} and ${ci_upper_ten}")


# In[ ]:




