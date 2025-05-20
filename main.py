from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd

driver = webdriver.Chrome()

driver.get("https://www.commonsensemedia.org/movie-reviews#browse-reviews-list")

print(driver.page_source)

driver.quit()