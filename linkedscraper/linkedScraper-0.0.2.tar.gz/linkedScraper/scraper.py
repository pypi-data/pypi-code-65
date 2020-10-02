import csv
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import os


def logon(email, password):
    driver = webdriver.Chromeos.path.dirnmae(__file__)
    driver.get('https://www.linkedin.com/')
    driver.find_element_by_xpath('//a[text()="Sign in"]').click()
    time.sleep(2)
    username_input = driver.find_element_by_name('session_key')
    username_input.send_keys(email)
    time.sleep(.5)
    password_input = driver.find_element_by_name('session_password')
    password_input.send_keys(password)

def profilescaper(url):
    driver = webdriver.Chromeos.path.dirnmae(__file__)
    ## Data scraping ## 
    driver.get(url)
    time.sleep(.5)
    sel = Selector(text=driver.page_source)
    name = sel.xpath('//*[starts-with(@class, "inline t-24 t-black t-normal break-words")]/text()').extract_first()
    name = name.strip()
    job = sel.xpath('//*[starts-with(@class, "mt1 t-18 t-black t-normal break-words")]/text()').extract_first()
    job = job.strip()
    print(job, name)
    about = sel.xpath('//*[@id="ember2565"]/text()').extract()
    print(about)
    time.sleep(1)
    print('Done.')
    return [name, about, job]

def companyscraper(urls):
    driver = webdriver.Chromeos.path.dirnmae(__file__)

    # click on the sign in button
    # we're finding Sign in text button as it seems this element is seldom to be changed

    time.sleep(1)

    dict_ar = []
    url_ar = []
    for u in urls:
        url = u + 'about'
        driver.get(url)
        time.sleep(.5)
        
        sel = Selector(text=driver.page_source)
        try:
            about = sel.xpath('//*[@class="break-words white-space-pre-wrap mb5 t-14 t-black--light t-normal"]/text()').extract_first().strip()
            website = sel.xpath('//*[@class="link-without-visited-state"]/text()').extract_first().strip()

            results_dd = sel.xpath('//dd/text()').extract()
            results_dt = sel.xpath('//dt/text()').extract()

            dict1 = dict()

            for i in results_dt:
                i = i.strip()
                if i == 'Website':
                    dict1['Website'] = website
                if i == 'Industry':
                    dict1['Industry'] = 1
                if i == 'Company size':
                    dict1['Company size'] = 1
                if i == 'Headquarters':
                    dict1['Headquarters'] = 1
                if i == 'Type':
                    dict1['Type'] = 1
                if i == 'Specialties':
                    dict1['Specialties'] = 1

            for i in results_dd:
                if 'on LinkedIn' in i:
                    results_dd.remove(i)

            new_dd = []
            for i in results_dd:
                i = i.strip('\n')
                i = i.strip(' ')
                i = i.replace('\n', '')
                new_dd.append(i)

            new_dd = [i for i in new_dd if i] 
            i = 0
            for keys in dict1:
                if dict1[keys] == 1:
                    dict1[keys] = new_dd[i]

                    i+=1


            
            dict_ar.append(dict1)
            url_ar.append(u)
        except:
            print(url, " doesn't work")



        time.sleep(1)

    finaldf = pd.DataFrame(dict_ar)
    finaldf = finaldf.fillna('N/A')
    finaldf['LinkedIn site'] = url_ar

    print('Done.')
    driver.quit()
    return finaldf

