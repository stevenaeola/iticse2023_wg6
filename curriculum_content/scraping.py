#!/usr/bin/env python
# coding: utf-8

# Following https://realpython.com/beautiful-soup-web-scraper-python/
# and https://www.scrapingbee.com/blog/selenium-python/
# 
# 
# install webdriver for Chrome from https://chromedriver.chromium.org/downloads
# 
# in your python environment install selenium https://selenium-python.readthedocs.io/installation.html
# 
# to identify xpath location of relevant content can use https://selectorshub.com/selectorshub/

import json
import pandas as pd

import os

from selenium import webdriver
from selenium.webdriver.common.by import By

import pprint

import sys

def heading(field):
    return "<h2>" + field + "</h2>"
    
def scrape(institution_name):
    config_json = "scraping_config.json"
    institution_json = "institution.json"

    with open(config_json) as config_file:
        config = json.load(config_file)

    driver_path = config['driver_path']

    print("Scraping " + institution_name)

    pp = pprint.PrettyPrinter(indent=4)

    driver = webdriver.Chrome(executable_path=driver_path)
    key_fields = ['institution', 'elective', 'overview']
    overview_fields = ['title', 'summary', 'content', 'ilo']
    all_fields = key_fields + overview_fields

    try:
        path = institution_name

        with open(os.path.join(path, institution_json)) as institution_file:
            institution_config = json.load(institution_file)
            pp.pprint(institution_config)
        electives_df = pd.DataFrame(columns=all_fields, dtype="string")

        if pre_scraped := institution_config.get('pre_scraped_file',""):
            if fields := institution_config.get('fields', ""):
                pre_scraped_df = pd.read_csv(os.path.join(path, pre_scraped), dtype='str')
                pre_scraped_df['institution'] = institution_name
                pre_scraped_df['overview'] = ""
                for field in [i for i in all_fields if i not in ['institution','overview']]:
                    lookup = fields[field]
                    if not lookup:
                        pre_scraped_df[field] = ""
                        continue
                    pre_scraped_df[field] = pre_scraped_df[lookup]

                    if field in overview_fields:
                        pre_scraped_df['overview'] =  pre_scraped_df['overview'] + heading(field) + pre_scraped_df[field]

                electives_df = pre_scraped_df[all_fields]
                electives_df = electives_df[electives_df['elective'].str.len() >0]
                electives_df.to_csv(os.path.join(path,'electives_pre.csv'), index= False)
                return

        url = institution_config['scrapeURL']        
        xpaths = institution_config['XPath']
        electives = institution_config['electives']

        for elective in electives:
            if isinstance(electives, dict):
                elective_url = url.replace("%ELECTIVE%", electives[elective])
            else:
                elective_url = url.replace("%ELECTIVE%", elective)
            driver.get(elective_url)
#            full_page=driver.find_elements(By.XPATH, '//').get_attribute('innerHTML')
#            full_file = open("Page" + elective, "w")
#            full_file.write(full_page)
#            full_file.close()
            overview = ""
            overview_dictionary = {}
            for overview_field in overview_fields:
                overview_dictionary[overview_field] = ""
                try:
                    overview_elts = driver.find_elements(By.XPATH, xpaths[overview_field])
                except Exception:
#                    print("Could not find field " + overview_field)
                    continue
                overview += heading(overview_field)
                for elt in overview_elts:
#                    print ("found elt for " + overview_field)
                    innerHTML = elt.get_attribute('innerHTML')
                    overview += innerHTML
                    overview_dictionary[overview_field] += innerHTML
            new_row = {"institution": institution_config['institution'],
                    "elective": elective,
                    "overview": overview} | overview_dictionary
            electives_df = electives_df.append(new_row, ignore_index=True)
        electives_df = electives_df[electives_df['elective'].str.len() >0]
        electives_df.to_csv(os.path.join(path,'electives_scraped.csv'), index=False)
        driver.quit()
    except OSError as err:
        print("OS error:", err)
        driver.quit()

def main():
    try:
        arg = sys.argv[1]
        institution_name = arg
        scrape(institution_name)
    except IndexError:
        print("No institution defined on command line")
        return

if __name__ == "__main__":
    main()
