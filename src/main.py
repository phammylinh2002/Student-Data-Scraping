from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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
        # driver.get(url)
        
        # # Step 2: Find and fill in the login form
        # username_input = driver.find_element(By.NAME, 'username')
        # password_input = driver.find_element(By.NAME, 'password')
        # username_input.send_keys(username)
        # password_input.send_keys(password)

        # # Step 3: Submit the login form
        # password_input.send_keys(Keys.RETURN)


        # # Step 4: Get all courses removed from view and display each as a card
        # time.sleep(5)
        # display_options = [
        #     {
        #         'removed_from_view': {
        #             'dropdown_button':'//*[@id="groupingdropdown"]',
        #             'option':'//a[contains(text(), "Removed from view")]'
        #         }
        #     },
        #     {
        #         'show_all': {
        #             'dropdown_button':'//button[contains(@aria-label, " items per page")]',
        #             'option':'//li[@data-limit="0"]'
        #         }
        #     },
        #     {
        #         'card_display': {
        #             'dropdown_button':'//*[@id="displaydropdown"]',
        #             'option':'//a[@data-value="card"]'
        #         }
        #     }
        # ]        
        # for option in display_options:
        #     for key, value in option.items():
        #         dropdown_button_xpath = value['dropdown_button']
        #         option_xpath = value['option']
        #     driver.find_element(By.XPATH, dropdown_button_xpath).click()
        #     time.sleep(1)
        #     driver.find_element(By.XPATH, option_xpath).click()
        #     print(f"Display option '{key}' was chosen")
        #     time.sleep(3)

        # Step 5: Scrape the content using BeautifulSoup
        # page_source = driver.page_source
        # soup = BeautifulSoup(page_source, 'html.parser')
        with open('my_courses.html', 'r', encoding='utf-8') as f:
            # f.write(page_source)
            page_source = f.read()
        soup = BeautifulSoup(page_source, 'html.parser')
        data = soup.select('div[role="listitem"]')[1:] # The first card is eliminated as it is the recently accessed course, which is already included in the course overview
        print(len(data))
        # for div in data[:2]:
        #     print("\n\n\n")
        #     print(div.prettify())
        # print("Scraping successful!")

    finally:
        # Close the WebDriver after scraping
        driver.quit()

# Replace 'your_username' and 'your_password' with your actual credentials
if __name__ == '__main__':
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    scrape_your_course_data(username, password)
