from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Function to scrape the dynamic website
def scrape_your_course_data(username, password):
    # Set up the Selenium WebDriver
    url = 'https://mlearning.hoasen.edu.vn'
    driver = webdriver.Safari()

    try:
        # Step 1: Open the login page
        driver.get(url)
        
        # Step 2: Find and fill in the login form
        username_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')
        username_input.send_keys(username)
        password_input.send_keys(password)

        # Step 3: Submit the login form
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Step 4: Get all courses removed from view and display each as a card
        wait = WebDriverWait(driver, 10)
        # Show removed-from-view courses
        driver.find_element(By.XPATH, '//*[@id="groupingdropdown"]').click()
        remove_from_view_xpath = '//a[contains(text(), "Removed from view")]'
        wait.until(EC.element_to_be_clickable((By.XPATH, remove_from_view_xpath)))
        driver.find_element(By.XPATH, remove_from_view_xpath).click()
        time.sleep(1)
        print("Displaying removed-from-view courses")
        # Show all courses in a page 
        driver.find_element(By.XPATH, '//button[contains(@aria-label, " items per page")]').click()
        show_all_xpath = '//li[@data-limit="0"]'
        wait.until(EC.element_to_be_clickable((By.XPATH, show_all_xpath)))
        driver.find_element(By.XPATH, show_all_xpath).click()
        time.sleep(1)
        print("Displaying all courses in a page")
        # Show each course as a card
        driver.find_element(By.XPATH, '//*[@id="displaydropdown"]').click()
        card_display_xpath = '//a[@data-value="card"]'
        wait.until(EC.element_to_be_clickable((By.XPATH, card_display_xpath)))
        driver.find_element(By.XPATH, card_display_xpath).click()
        time.sleep(1)
        print("Displaying each course as a card")

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
    scrape_your_course_data(username, password)
