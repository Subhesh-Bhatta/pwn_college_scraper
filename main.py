import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def start(url):
    global driver

    driver = webdriver.Chrome()
    driver.get(url)

def end():
    """
    Function to quit the WebDriver, closing the browser window.
    """
    global driver
    if driver:
        driver.quit()

def search


def master():
    start("https://pwn.college/dojos")
    time.sleep(2)
    end()




master()