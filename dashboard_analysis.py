# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3.9.1 64-bit
#     name: python3
# ---

# %% [markdown]
# # Analyze Dashboard Data for COVID Cases in Pinellas County Schools
#
# In this notebook, we analyze the data contained in Pinellas County School's COVID database. The tools include county wide totals, school by school analyses, and data visualization.
#
# This notebook analyzes the latest .csv data file scraped by the `dashboard_scrape.py` notebook. From this point on, we employ pandas and matplotlib to analyze and visualize the data. This notebook allows you to slice the data into various bins, by date, by school, by category, and shows some clever ways to plot the data compared to last year's data. 

# %%
#Load packages
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import matplotlib.dates as mdates

# %% [markdown]
# ## Data Analysis
#
# From this point on, we employ pandas and matplotlib to analyze and visualize the data. This notebook allows you to slice the data into various bins, by date, by school, by category, and shows some clever ways to plot the data compared to last year's data. 

# %%
# Import datadump.csv files

# make a list of csvs
import glob
files = glob.glob('data_dump_*.csv')
files = sorted(files, reverse=True)

data_df = pd.read_csv(files[0])
data_df
print(data_df.columns)
print(max(data_df['Date']))

# %%
#Uncomment the line below if the data have extra columns 0, 1, and 2 in the dataframe. This happens
#sometimes when the scraping happens too fast for th table to load.
#data_df.drop(columns=[0, 1, 2], inplace=True)

# %%
pcsb_students_2019 = 100000
hcsb_students_2019 = 223305

#Mask for cases since the beginning of the school year, 8/11/2021
school_year_mask = data_df['Date']>='2021-08-11'
data_df = data_df.loc[school_year_mask]
print(data_df.shape)

#Add column for total cases, calculate grand total.
data_df['Total cases'] = data_df['Number of positive employees'] + data_df['Number of positive students']
print(data_df.shape)
print('Total cases in district = ' + str(sum(data_df['Total cases'].dropna())))
total_cases_students = sum(data_df['Number of positive students'].dropna())
print('Total covid+ student cases in district = ' + str(total_cases_students) + 
      ' (' + str(total_cases_students/pcsb_students_2019*100) + "%" + ' of students)')
total_cases_employees = sum(data_df['Number of positive employees'].dropna())
print('Total covid+ employees cases in district = ' + str(total_cases_employees))
cases_by_date = data_df.groupby('Date').sum().sort_values(by='Date', ascending=True)
print(cases_by_date)
fig, ax = plt.subplots()
ax.plot(cases_by_date.index, cases_by_date['Number of positive employees'], 
        color='lightgreen', mec='k', marker='o', markersize=10)
ax.plot(cases_by_date.index, cases_by_date['Number of positive students'], 
        color='lightblue', mec='k', marker='^', markersize=10)
ax.title.set_text("Total daily +COVID reports - Pinellas County Schools")
ax.set_ylabel('# of positive cases reported each day')
plt.xticks(rotation='vertical')
ax.legend(['Employees', 'Students'])

plt.savefig('Daily Positive Cases.png')


# %%
#Cumulative sums
school = 'Midtown Academy'
data_df.sort_values(['Locations affected', 'Date'], ascending=[True, True], inplace=True)
data_df['Cumulative Sum Students'] = data_df.groupby(by='Locations affected')['Number of positive students'].cumsum()
print(data_df.loc[data_df['Locations affected'] == school])
fig, ax = plt.subplots()
#ax.plot(data_df['Date'].loc[data_df['Locations affected']==school], 
#        data_df['Date'].loc[data_df['Cumulative Sum Students']==school])
ax.plot(data_df['Date'].loc[data_df['Locations affected']==school], 
        data_df['Cumulative Sum Students'].loc[data_df['Locations affected']==school])

# %% [markdown]
# ## Focus on Midtown Academy (K-5, southside) vs. Dunedin (K-5, north county)
#
# To compare two schools, we select the text in the their names and use pandas to filter the rest of the data. For each one, a time series can be made for both students and employees who have tests positive for COVID 19 during this school year. These schools allow us to use geography as a proxy for how many people may become sick with COVID due to opening schools with no mask mandate and the highly contagious delta variant of COVID causing record daily positive cases and hospitalization in the county and across the state. 

# %%
#Use the following two lines to pick data from a single school:
text_in_school1_name = 'Midtown'
school1_df = data_df[data_df['Locations affected'].astype(str).str.contains(text_in_school1_name)].sort_values(by='Date', ascending=True)
print(school1_df)

text_in_school2_name = 'Dunedin Elementary'
school2_df = data_df[data_df['Locations affected'].astype(str).str.contains(text_in_school2_name)].sort_values(by='Date', ascending=True)

_, ax = plt.subplots(nrows=1, ncols=1)
ax.plot(
    (school2_df['Date']),
    school2_df['Number of positive students'],
    color='yellow', 
    mec='k',
    marker='o',
    linestyle=" ",
    label=text_in_school1_name
)
ax.plot(
    (school1_df['Date']),
    school1_df['Number of positive students'],
    color='lightgreen', 
    mec='k',
    marker='o',
    linestyle=" ",
    label=text_in_school2_name
)
ax.legend()


#fmt_weekly = mdates.DayLocator(interval=2)
#ax.xaxis.set_major_locator(fmt_weekly)
#ax.xaxis.set_major_locator(mdates.YearLocator())
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
# %%
