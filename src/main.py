import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Function to scrape the dynamic website
def scrape_website(username, password):
    # Set up the Selenium WebDriver
    url = 'https://mlearning.hoasen.edu.vn'
    driver = webdriver.Safari()

    try:
        # Step 1: Open the login page
        driver.get(url)
        
        # Step 2: Find and fill in the login form
        username_input = driver.find_element('name', 'username')
        password_input = driver.find_element('name', 'password')

        username_input.send_keys(username)
        password_input.send_keys(password)

        # Step 3: Submit the login form
        password_input.send_keys(Keys.RETURN)

        # Allow some time for the page to load
        time.sleep(3)

        # Step 4: Get all courses removed from view
        dropdown_button = driver.find_element('id', 'groupingdropdown')
        dropdown_button.click()
        time.sleep(1)
        item = driver.find_element('path', '//a[@class="dropdown-item" and text()="Remove from view"]')
        item.click()
        time.sleep(1)

        # Step 5: Scrape the content using BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        with open('page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        # Now you can use BeautifulSoup to extract the data you need
        # For example:
        # data = soup.find('div', class_='your-target-class').text

        print("Scraping successful!")

    finally:
        # Close the WebDriver after scraping
        driver.quit()

# Replace 'your_username' and 'your_password' with your actual credentials
if __name__ == '__main__':
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    scrape_website(username, password)
