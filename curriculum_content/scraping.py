# Following https://realpython.com/beautiful-soup-web-scraper-python/ 
# and 
# https://www.scrapingbee.com/blog/selenium-python/

# install webdriver for Chrome from https://chromedriver.chromium.org/downloads

# in your python environment install selenium
# https://selenium-python.readthedocs.io/installation.html

# to identify xpath location of relevant content can use https://selectorshub.com/selectorshub/

import json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By

config_json = "scraping_config.json"

configFile = open(config_json)

config = json.load(configFile)
configFile.close()

institutions = config['institutions']
driver_path = config['driver_path']

print(institutions)


