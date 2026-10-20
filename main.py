import time
from selenium import webdriver
from urllib.parse import urlparse, unquote
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException


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

# this is only done so that I can print multiple error messages,
# since there's the same NoSuchElementException for each every element not found error
def find_required_element_helper(parent, by, selector, error_message):
    try:
        return parent.find_element(by, selector)
    except NoSuchElementException:
        raise NoSuchElementException(error_message) from None

#same logic as find_required_element_helper, just for multiple elements,
#uses find_elements instead of find_element
def find_required_elements_helper(parent, by, selector, error_message):
    try:
        return parent.find_elements(by, selector)
    except NoSuchElementException:
        raise NoSuchElementException(error_message) from None

#dojoName is the name of the H2 header for the Dojo, copy it as is fom the website
def searchDojos():
    pwnTree = {}

    ul_elements = find_required_elements_helper(
        driver,
        By.CSS_SELECTOR,
        "ul.card-list",
        """The ul elements inside the webpage doesn't exit.
        First check if the webpage is correct,
        then inspect the website and see if the dojos are inside a ul tag, or other tags,
        and change the paramter accordingly.
        -----------------------------------------------------------------"""
    )

    for each_ul_element in ul_elements:

        a_elements = find_required_elements_helper(
            each_ul_element,
            By.TAG_NAME,
            "a",
            """The anchor tags inside the ul elements don't exist.
            Check the webpage and inspect the website to see
            whether the links are still inside anchor tags.
            ---------------------------------------------------------------"""
        )

        for each_a_element in a_elements:
            href = each_a_element.get_attribute("href")

            # Skip elements that do not have a URL
            if not href:
                continue

            try:
                card_title_element = each_a_element.find_element(
                    By.CLASS_NAME,
                    "card-title"
                )

                dojoTitle = card_title_element.text.strip()

                # Use the URL's last path segment if the title is empty
                if not dojoTitle:
                    raise NoSuchElementException("The card title is empty.")

            except NoSuchElementException:
                print(f"There is no title for href: {href}")
                print("Using the last path segment of the URL as the title.")

                path_segments = [
                    segment
                    for segment in urlparse(href).path.split("/") if segment
                ]

                dojoTitle = (
                    unquote(path_segments[-1])
                    if path_segments
                    else href
                )

                print("Do manual entry of this href if you want to.")
                print("-------------------------------------------------------")

            pwnTree[dojoTitle] = href

    return pwnTree
                
     

def master():
    start("https://pwn.college/dojos")
    dojosDict = searchDojos()

    #Printing output of dojos
    for key, value in dojosDict.items():
        print(f"{key}: {value}")
    print("------------------------------------------------------")
    
    time.sleep(2)
    end()




master()