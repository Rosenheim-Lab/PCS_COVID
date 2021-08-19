# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Scrape Dashboard Data for COVID Cases 
# ## in Pinellas County Schools
#
# In this notebook, we develop tools to scrape and analyze the data contained in Pinellas County School's COVID database. The tools include county wide totals, school by school analyses, and data visualization.
#
# ## Setting the constants and loading some packages
# Below, two url's are loaded as strings. The first url, `URL`, is the PCSB web page containing COVID case numbers for each school each day they are reported. This web page provides some searchability of the COVID results during the 2021-2022 school year in Pinellas County Schools. We do not need the searchability functionality of the webpage; we need the data contained in the database so that we can analyze and visualize it with pandas and matplotlib. To get the whole database, only only needs to click on the `Submit` button without any filters applied. Then the web page dynamically displays a table splayed over several pages. 
#

# +
#Load packages
import pandas as pd
import matplotlib.pyplot as plt
import PCS_COVID_ScraPy as PCS
from datetime import date
import matplotlib.dates as mdates



#Set URL
URL = 'https://www.pcsb.org/covid19cases'
URL_2020_2021 = 'https://www.pcsb.org/Page/34025'

#Set driver path !!!Important - every user will have a different driver path! See readme.md for more info!
driver_path = "/Users/williams/Documents/NancyPy/PCS_COVID/chromedriver"


# -

# ## Scraping the table into a df
#
# Once the variables are set above, we can run the wrapper function. This function is likely to throw errors such as "StaleElement" or "Driver not Found" until you:
#   1. Get the timer set appropriately for your internet connection and page load times, and 
#   2. Get consistent behavior from the web browser you are driving. 
#
# In the case of those types of errors, close the browser that opens when this operates and re-run this cell. You may get several consecutive errors, but it will eventually work. You can also try to re-run the first cell and increase the delay time.
#
# This routine will give status updates of how many pages it is scraping and how many it has scraped.

data_dict, data_df = PCS.Scrape_data(URL, driver_path, 2)

# ## Data Analysis
#
# From this point on, we employ pandas and matplotlib to analyze and visualize the data. This notebook allows you to slice the data into various bins, by date, by school, by category, and shows some clever ways to plot the data compared to last year's data. 

# +
#Verify the size the dataframe. There are approximately 25 rows per page scraped (in most cases). 

#Uncomment the line below if the data have extra columns 0, 1, and 2 in the dataframe. This happens
#sometimes when the scraping happens too fast for th table to load.
#data_df.drop(columns=[0, 1, 2], inplace=True)

data_df['Date'] = pd.to_datetime(data_df['Date'], yearfirst=True)
print(data_df.columns)
print(data_df.dtypes)
print(data_df.shape)




# +
#Save the datadump. If you want to save a .csv file, un-comment the last line and run this cell.

today = date.today()
filename = 'data_dump_' + today.strftime("%Y%m%d") +'.csv'
print(filename)
#Uncomment the line below to save the data 
pd.DataFrame.to_csv(data_df, filename)
# -

# ## * Move to dashboard_analysis.py


