#!/usr/local/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Scraper:
    def __init__(self):
        self.driver = webdriver.Safari().get('https://mlearning.hoasen.edu.vn')

    def log_in(self, username, password):
        # Find and fill in the login form
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys(username)
        password_input.send_keys(password)
        # Submit the login form
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

    def scrape_courses(self, page_source):
        # Add the logic to scrape course data here...
        # This could be similar to the code in your active file from lines 72 to 90
        return

    def scrape_profile(self, page_source):
        # Add the logic to scrape profile data here...
        # This could be similar to the code in your active file from lines 93 to 97
        return

    def quit_driver(self):
        self.driver.quit()
        return



def change_display_options():
    display_options = [
        {
            'removed_from_view': {
                'dropdown_button':'//*[@id="groupingdropdown"]',
                'option':'//a[contains(text(), "Removed from view")]'
            }
        },
        {
            'show_all': {
                'dropdown_button':'//button[contains(@aria-label, " items per page")]',
                'option':'//li[@data-limit="0"]'
            }
        },
        {
            'card_display': {
                'dropdown_button':'//*[@id="displaydropdown"]',
                'option':'//a[@data-value="card"]'
            }
        }
    ]        
    for option in display_options:
        for key, value in option.items():
            dropdown_button_xpath = value['dropdown_button']
            option_xpath = value['option']
        driver.find_element(By.XPATH, dropdown_button_xpath).click()
        time.sleep(1)
        driver.find_element(By.XPATH, option_xpath).click()
        print(f"Display option '{key}' was chosen")
        time.sleep(3)



def scrape_my_course_data():
    # Step 4: Get all courses removed from view and display each as a card
    time.sleep(5)
    

    # Step 5: Scrape the content using BeautifulSoup
    # page_source = driver.page_source
    # soup = BeautifulSoup(page_source, 'html.parser')
    with open('./output/my_courses.html', 'r', encoding='utf-8') as f:
        # f.write(page_source)
        page_source = f.read()
    soup = BeautifulSoup(page_source, 'html.parser')
    courses = soup.select('div[role="listitem"]')[1:] # The first card is eliminated as it is the recently accessed course, which is already included in the course overview
    all_my_course_data = {}
    for course in courses:
        course_link_tag = course.select_one('a.aalink.coursename.mr-2')
        course_link = course_link_tag['href'].strip()
        course_other_data = course_link_tag.select_one('span.multiline').text.strip().split("_")
        if len(course_other_data) >= 3:
            course_name, course_id, sem_id = course_other_data[:3]
            all_my_course_data[int(course_id)] = {
                'name': course_other_data[0],
                'sem_id': int(course_other_data[2]),
                'link': course_link
            }
    
    # Step 6: Prepare document to insert into MongoDB
    # Get my profile link
    my_profile_link = soup.select_one('a.d-inline-block.aabtn')['href'].strip()
    document = {
        '_id': int(os.environ['MY_ID']),
        'name': os.environ['MY_NAME'],
        'email': os.environ['MLEARNING_USERNAME'],
        'profile_link': my_profile_link,
        'courses': all_my_course_data
    }
    # print(len(all_my_course_data))
    # for key, value in all_my_course_data.items():
    #     print(type(key))
        # print(str(i) + ". " + value['name'] + "\n")
        # i+=1
        # for key, value in course.items():
        #     print(value['name'])
            # print(key, "\n", value, "\n\n")
        # print(div.prettify())
    # print("Scraping successful!")

    # Course: https://mlearning.hoasen.edu.vn/course/view.php?id=16928
    # My profile and the chosen course: https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=16928
    # My profile: https://mlearning.hoasen.edu.vn/user/profile.php?id=19701
    # Course participants: https://mlearning.hoasen.edu.vn/user/index.php?id=16928


# Replace 'your_username' and 'your_password' with your actual credentials
def main():
    # driver = webdriver.Safari().get('https://mlearning.hoasen.edu.vn')
    username = os.environ['MLEARNING_USERNAME']
    password = os.environ['MLEARNING_PASSWORD']
    
    try:
        # log_in(driver, username, password)
        scrape_my_course_data()
    finally:
        # quit_driver(driver)
        a=1

if __name__ == "__main__":
    main()