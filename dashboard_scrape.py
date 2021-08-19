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
driver_path = "C:/webdrivers/chromedriver.exe" # Brad's machine
#driver_path = 'chromedriver' # Nancy's machine


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

# +
#Condensed code with exception handling from Dahomey Kadera: 
#Runs a bit slower than the PCS_COVID_ScraPy package, perhaps more dependable though.

from selenium import webdriver
import time
from  bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome(driver_path)
driver.get(URL)
driver.maximize_window()

time.sleep(1)

date_search = driver.find_element_by_id("sw-minibasefilter65979-field-0")
date_search.clear()
date_search.send_keys("2021")

time.sleep(1)

submit_enter = driver.find_element_by_id("minibaseSubmit65979")
submit_enter.click()

def initiate_soup():
  time.sleep(2)
  el = driver.find_element_by_class_name("sw-flex-table")
  return BeautifulSoup(el.get_attribute("outerHTML"), "html.parser")

column_names = []
soup = initiate_soup()
header = soup.find('tr')
for th in header.find_all('th'):
  column_names.append(th.get_text())

df = pd.DataFrame(columns = column_names)
  
def get_rows():
  global df
  soup = initiate_soup()
  rows = soup.find_all('tr')
  for row in rows[1: ]:
    this_row = []
    for td in row.find_all('td'):
      this_row.append(td.get_text())
    values_to_add = {}
    for i in range(len(column_names)): 
      values_to_add[column_names[i]] = this_row[i]
    row_to_add = pd.Series(values_to_add, name=len(df))
    df = df.append(row_to_add)	

get_rows()	
	
for i in range(2,100): 
  x_path_go = "//li/a[@aria-label='Go to Page %s']"%(str(i))
  x_path_skip = "//li/a[@aria-label='Skip to Page %s']"%(str(i))  
  #print(x_path_go)
  #print(x_path_skip)
  try: 
    pge = driver.find_element_by_xpath(x_path_go)
    if pge: 
      pge.click()
      get_rows()
  except: 
    pass
  
  try: 
    pge_s = driver.find_element_by_xpath(x_path_skip)
    if pge_s: 
      pge_s.click()
      get_rows()
  except: 
    pass  
	  
print(column_names)
df.to_csv("cov_dat_Dahomey_20210817.csv")
# -

print(df.shape)

# ## *** Moved analysis to dashboard_analysis.py ***


