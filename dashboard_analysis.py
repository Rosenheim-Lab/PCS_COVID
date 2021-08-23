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
import datetime
import matplotlib.dates as mdates
import numpy as np
import glob

# %% [markdown]
# ## Data Analysis
#
# From this point on, we employ pandas and matplotlib to analyze and visualize the data. This notebook allows you to slice the data into various bins, by date, by school, by category, and shows some clever ways to plot the data compared to last year's data. 
#
# ### This year's data, last year's data
# The next cell loads and cleans up the latest .csv file saved from the datascraping routine. It also loads the static data from the 2020-2021 school year, which had already been scraped in the same fashion. The clean-up steps are: 
#    * Get rid of extra columns (sometimes the scraper goes too fast and gets extra columns labeled 0, 1, 2)
#    * Transform the `Date` column into pandas datetime objects for easier plotting

# %%
# Import datadump.csv files from 2021-2022 school year

# make a list of csvs
files = glob.glob('data_dump_*.csv')
files = sorted(files, reverse=True)

# Pick the data dump file from the most recent date
data_df = pd.read_csv(files[0])
data_df['Date'] = pd.to_datetime(data_df['Date'], yearfirst=True)
print(data_df.columns)
print(data_df.dtypes)

# Import all data from 2020-2021 school year for comparison
last_year_df = pd.read_csv('All_Data_2020-2021.csv')
last_year_df['Date'] = pd.to_datetime(last_year_df['Date'], yearfirst=True)
print(last_year_df.columns)
print(last_year_df.dtypes)

# %%
#Uncomment the line below if the data have extra columns 0, 1, and 2 in the dataframe. This happens
#sometimes when the scraping happens too fast for th table to load.
data_df.drop(columns=['Unnamed: 0'], inplace=True)
print(data_df.columns)

# %% [markdown]
# ## Initial Visualization
#
# In the next two cells, we visualize the data at the district level. The first visualization is simply looking at the positive reported cases each day of the 2021-2022 school year, for both employees and students. The second cell visualizes the cumulative sum of cases for the 2021-2022 school year and compares those data to the same length of time starting in the Fall semester and the Spring semester. 

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
last_year_df['Total cases'] = last_year_df['Number of positive employees'] + last_year_df['Number of positive students']
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
plt.xticks(rotation=30, ha='right')
ax.legend(['Employees', 'Students'])

plt.savefig('Daily Positive Cases.png')


# %%
#Daily district-wide cumulative sums for 2021-2021 and compare to last school year
#Start with active mask to compare the same amounts of elapsed school days:
summer_start_date_2020 = pd.to_datetime('2020-08-30')
summer_start_date_2021 = pd.to_datetime('2021-08-11')
winter_start_date_2020 = pd.to_datetime('2021-01-04')
length_current_year = max(data_df['Date']) - summer_start_date_2021 + datetime.timedelta(days=1)
time_mask_summer = summer_start_date_2020 + length_current_year
time_mask_winter = winter_start_date_2020 + length_current_year
print(length_current_year, time_mask_summer, time_mask_winter)

daily_cum_sum = data_df.groupby(['Date'])['Total cases'].sum().cumsum().sort_values()
#print(daily_cum_sum)

#Create a DataFrame with data equal to the number of school days so far, 
# for both summer and winter semesters, using the dynamic time mask from above
last_year_so_far_summer_df = last_year_df[~(last_year_df['Date']<summer_start_date_2020) & ~(last_year_df['Date']>time_mask_summer)]
#print(last_year_so_far_summer_df.head())
daily_cum_sum_summer2020 = last_year_so_far_summer_df.groupby(['Date'])['Total cases'].sum().cumsum().sort_values()
summer_xaxis = daily_cum_sum_summer2020.index-min(daily_cum_sum_summer2020.index)
last_year_so_far_winter_df = last_year_df[~(last_year_df['Date']<winter_start_date_2020) & ~(last_year_df['Date']>time_mask_winter)]
#print(last_year_so_far_summer_df.head())
daily_cum_sum_winter2020 = last_year_so_far_winter_df.groupby(['Date'])['Total cases'].sum().cumsum().sort_values()
winter_xaxis = daily_cum_sum_winter2020.index-min(daily_cum_sum_winter2020.index)

print('Axis length comparison:\n')
print('x-axis: ', last_year_so_far_summer_df.index-min(last_year_so_far_summer_df.index))
print('y-axis: ', daily_cum_sum_summer2020)

fig, ax = plt.subplots()

ax.plot(daily_cum_sum.index-min(daily_cum_sum.index), 
        daily_cum_sum, 
        marker='s',
        mec='k',
        markerfacecolor='orange',
        markersize=10,
        color='k'
)
ax.plot(summer_xaxis, 
        daily_cum_sum_summer2020, 
        marker='d',
        mec='k',
        markerfacecolor='lightgray',
        markersize=10,
        color='lightgray'
)
ax.plot(winter_xaxis, 
        daily_cum_sum_winter2020, 
        marker='>',
        mec='k',
        markerfacecolor='lightgray',
        markersize=10,
        color='lightgray'
)
#plt.xticks(rotation=30, ha='right')
ax.set_ylabel('District-wide cumulative sum, + cases')
ax.set_xlabel('Days since the first day of semester')
ax.legend(
        [
        '2021-2022 Fall, ' + str(max(daily_cum_sum)) + ' total cases',
        '2020-2021 Fall, ' + str(max(daily_cum_sum_summer2020)) + ' total cases',
        '2020-2021 Spring, ' + str(max(daily_cum_sum_winter2020)) + ' total cases'
        ]
)
ax.set_title('Cumulative cases after ' + str((length_current_year - datetime.timedelta(days=1)).days) + ' school days')
plt.savefig('DailyCumsumComparison.png')
plt.savefig('DailyCumsumComparison.jpg')
plt.savefig('DailyCumsumComparison.pdf')

# %% [markdown]
# ## Focus on North Pinellas County vs. South Pinellas County
#
# Pinellas County is politically heterogeneous, with the south side leaning strongly democrat and the north side leaning strongly republican. Masks in schools and a social responsible response to COVID in general have become partisan issues. One goal of this notebook is to examine whether partisanship has caused a rift in how schools transmit and spread COVID in absence of mask mandates in the county. As we build a data base of school addresses and total populations for a full analysis, we offer an analysis of two schools as a proxy for examination of this partisan divide in social responsibility.
#
# To compare two schools, we select the text in the their names and use pandas to filter the rest of the data. For each one, a time series can be made for both students and employees who have tests positive for COVID 19 during this school year. These schools allow us to use geography as a proxy for how many people may become sick with COVID due to opening schools with no mask mandate and the highly contagious delta variant of COVID causing record daily positive cases and hospitalization in the county and across the state. 

# %%
#Use the following two lines to pick data from a single school:
text_in_school1_name = 'Midtown'
school1_df = data_df[data_df['Locations affected'].astype(str).str.contains(text_in_school1_name)].sort_values(by='Date', ascending=True)
school1_df['Cumulative Sum Students'] = school1_df['Number of positive students'].cumsum()
print(school1_df)
print(school1_df.dtypes)

text_in_school2_name = 'Dunedin Elementary'
school2_df = data_df[data_df['Locations affected'].astype(str).str.contains(text_in_school2_name)].sort_values(by='Date', ascending=True)
school2_df['Cumulative Sum Students'] = school2_df['Number of positive students'].cumsum()
print(school2_df)

_, ax = plt.subplots(nrows=1, ncols=1)
ax.plot(
    (school2_df['Date']),
    school2_df['Cumulative Sum Students'],
    color='yellow', 
    mec='k',
    marker='o',
    linestyle=" ",
    label=text_in_school2_name
)
ax.plot(
    (school1_df['Date']),
    school1_df['Cumulative Sum Students'],
    color='lightgreen', 
    mec='k',
    marker='o',
    linestyle=" ",
    label=text_in_school1_name
)
plt.xticks(rotation=30, ha='right')
ax.legend()


#fmt_weekly = mdates.DayLocator(interval=2)
#ax.xaxis.set_major_locator(fmt_weekly)
#ax.xaxis.set_major_locator(mdates.YearLocator())
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
# %%
