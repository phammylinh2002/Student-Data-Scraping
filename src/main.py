import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Function to scrape the dynamic website
def scrape_website(username, password):
    # Set up the Selenium WebDriver
    driver = webdriver.Chrome()

    try:
        # Step 1: Open the login page
        driver.get('https://mlearning.hoasen.edu.vn')

        # Step 2: Find and fill in the login form
        username_input = driver.find_element_by_name('Username')
        password_input = driver.find_element_by_name('Password')

        username_input.send_keys(username)
        password_input.send_keys(password)

        # Step 3: Submit the login form
        password_input.send_keys(Keys.RETURN)

        # Allow some time for the page to load
        time.sleep(2)

        # Step 4: Navigate to the page you want to scrape
        driver.get('https://example.com/target-page')  # Replace with the actual URL of the target page

        # Allow some time for the dynamic content to load
        time.sleep(5)

        # Step 5: Scrape the content using BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

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
