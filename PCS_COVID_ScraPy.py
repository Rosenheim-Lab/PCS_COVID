#Import packages
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as WDW
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

print('^^^^^^^^^^^^PCS_COVID_ScraPy is now loaded! Happy data analysis!^^^^^^^^^^^^^')

ID = 'ui-paging-container'
DEBUG = False
headless = True

def debug(*args):
    if DEBUG == True:
        print(args)

def get_table(driver):
    #Access table on each page
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find_all('table')

    #read the table
    new_df = pd.read_html(str(table))
    
    return new_df[0]

def get_page_indices(driver):
    paging_buttons = driver.find_element(By.ID, ID).text
    page_text_indices = [page for page in paging_buttons.split('\n')]
    page_numbers = [int(page) for page in page_text_indices if (page != '...')]

    return paging_buttons, page_text_indices, page_numbers


def initiate_scraping(url, driver_path):
    #Set up selenium web interaction -
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    if headless == True:
        options.add_argument('--headless')         #Operates webpage without viewing through Chrome
    driver = webdriver.Chrome(driver_path)
    

    #Open webpage with webdriver, un-comment --headless argument above if you don't want to 
    #view the page. 
    driver.get(url)

    # Wait for pages to fully load for specified amount of time before throwing error.
    driver.implicitly_wait(10)

    #Now that the web page is open and operable, we need to click on the submit
    #button. Clicking on the search button allows us to get all of the data in a table. 
    click_submit_main(driver)

    return driver

def click_submit_main(driver):
    driver.find_element_by_xpath('//*[@id="minibaseSubmit65979"]').click()


def determine_total_pages(url, driver_path):
    '''
    This function clicks the submit button, clicks on the ellipsis until the ellipsis is not the last
    in the list of page indices, and returns the total number of pages to be scraped of data tables.
    '''
    #Click submit without filters so that all data are displayed in table over multiple pages
    driver = initiate_scraping(url, driver_path)
    
    for x in range(10000):      #This covers up to 10000 pages of data tables on the website.
        _, page_text_indices, page_numbers = get_page_indices(driver)
        if page_text_indices[-1] == '...':
            print('Iteration ', x, '. Clicking "..." to obtain pages after ', str(max(page_numbers)), ';\n searching for the last page.')
            next_page_xpath = '//*[@id="ui-paging-container"]/ul/li[' + str(max(page_numbers) + 1) + ']/a'
            debug(next_page_xpath)
            button = driver.find_element_by_xpath(next_page_xpath)
            driver.execute_script("arguments[0].click();", button)
        else:
            print('Iteration ', x, 'No ellipsis (...) at the end of this page. Maximum obtained.')
            total_pages = max(page_numbers)
            break
    #Once determined, return the webpage to the original form with the submit button to execute
    #filterless search and scrape data:
    new_search_xpath = '//*[@id="module-content-64809"]/div/div[2]/ul/li/div/div[1]/span/span/p[1]/a'
    new_search_button = driver.find_element_by_xpath(new_search_xpath)
    driver.execute_script("arguments[0].click();", new_search_button)

    return total_pages, page_text_indices, driver


def Scrape_data(url, driver_path, delay):
    '''
    Wrapper function employing the functions above to perform the iterative scraping routine.
    This routine can target either the current PCS data or the historic data (2020-2021 school
    year). 
        Inputs:
            url - (string) web address where the data portal can be accessed.
            driver_path - (string) the file path to your webdriver. See the readme.md for 
                instructions on installing and testing a webdriver. 
            delay - (float) number of seconds to delay before operating clicks or selections
                through the webdriver. This is an important parameter to use if this routine
                hangs up repeatedly on your computer, especially when going through large data
                sets with many pages. Increasing the delay will increase the total amount of 
                time it takes for this routine to operate, however it is useful to avoid
                hang-ups associated with the web driver trying to access java script controls
                which have not yet loaded. 
    '''


    #Determine the number of pages:
    tot, indices, driver = determine_total_pages(url, driver_path)
    print('Imitated filterless search to determine total pages: complete...\n')

    #Initiate the page log:
    data_df = pd.DataFrame([])
    print('Empty DataFrame created. \n')

    #Initiate filterless search
    click_submit_main(driver)
    print('Restarting filterless search to scrape data...')

    #Set up dictionary container for data troubleshooting:
    data_dict = {}
    print('Empty dictionary ready for temporary data sets.\n')

    #Scrape page 1 data
    temp_df = get_table(driver)
    data_df = pd.concat([data_df, temp_df])
    key = 'Page ' + str(1)
    data_dict |= {key:temp_df}
    print('Data scraped from page 1 table...\n')
    first_loop = True

    #Loop through remaining pages, beginning with page 2
    for page in range(2, tot+1):
        paging_buttons, page_text_indices, page_numbers = get_page_indices(driver)
        print('Scraping page ' + str(page) + ' of ' + str(tot) + ' pages.')
        if page <= max(page_numbers):
            if first_loop is True: 
                debug('Working in the if loop, first group of pages.')
                #This is the condition for the first time iterating through the table pages
                next_page_xpath = '//*[@id="ui-paging-container"]/ul/li[' + str(page) + ']/a'
                debug('Page 1 iteration ' + str(page) + ', xpath = ' + str(next_page_xpath))
                button = driver.find_element_by_xpath(next_page_xpath)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(delay)
            else:
                debug('Working in the if loop, subsequent groups of pages.')
                #This is the condition for the susequent times iterating through the table pages
                next_page_xpath = '//*[@id="ui-paging-container"]/ul/li[' + str(new_start) + ']/a'
                new_start = new_start + 1
                debug('Subsequent page iteration ' + str(page) + ', xpath = ' + str(next_page_xpath))
                button = driver.find_element_by_xpath(next_page_xpath)
                driver.execute_script("arguments[0].click();", button)
                time.sleep(delay)
            #Scrape data and concatenate
            temp_df = get_table(driver)
            debug('Data scraped from page ' + str(page) + r' table ...\n')
            #debug(temp_df.head())
            data_df = pd.concat([data_df, temp_df])
            key = 'Page ' + str(page)
            data_dict |= {key:temp_df}

        elif page > max(page_numbers):
            debug('Working from the elif loop (clicking the ellipsis).')
            #In this case, we click the right ellipsis.
            next_page_xpath = '//*[@id="ui-paging-container"]/ul/li[' + str(page) + ']/a'
            debug('Page 1 iteration ' + str(page) + ', xpath = ' + str(next_page_xpath))
            button = driver.find_element_by_xpath(next_page_xpath)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(2)
            #Scrape data and concatenate
            temp_df = get_table(driver)
            debug('Data scraped from page ' + str(page) + r' table ...\n, represented by "..."...')
            #debug(temp_df.head())
            data_df = pd.concat([data_df, temp_df])
            key = 'Page ' + str(page)
            data_dict |= {key:temp_df}
            #Set first_loop = False
            first_loop = False
            debug(page)
            debug(first_loop)
            new_start = 4
            debug('New counter for constructing x_paths: ', new_start)
    
    return data_dict, data_df
 