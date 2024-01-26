#!/usr/local/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import time
import os
import re


class Scraper:
    def __init__(self, url, username, password):
        self.driver = webdriver.Safari()
        self.url = url
        self.username = username
        self.password = password

    def log_in(self):
        self.driver.get(self.url)
        # Find and fill in the login form
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        # Submit the login form
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

    def scrape_courses(self, is_mine=True):
        if not isinstance(is_mine, bool):
            raise ValueError("The parameter `is_mine` must be a boolean value.")
        
        if is_mine == True:
            # Change display options to scrape all my courses
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
            #     self.driver.find_element(By.XPATH, dropdown_button_xpath).click()
            #     time.sleep(1)
            #     self.driver.find_element(By.XPATH, option_xpath).click()
            #     print(f"Display option '{key}' was chosen")
            #     time.sleep(3)
            
            # Scrape!
            # show_all_courses_param = '&showallcourses=1'
            # my_profile_link = self.driver.find_element(By.XPATH, '//*[@id="loggedin-user"]/a').get_attribute('href')
            # profile_courses_url = my_profile_link + show_all_courses_param
            # self.driver.get(profile_courses_url)
            # time.sleep(3)
            # page_source = self.driver.page_source
            # soup = BeautifulSoup(page_source, 'html.parser')
            with open('./output/my_courses.html', 'r', encoding='utf-8') as f:
                # f.write(page_source)
                page_source = f.read()
            soup = BeautifulSoup(page_source, 'html.parser')
            courses = soup.select('#region-main > div > div > div > section:nth-child(3) > div > ul > li > dl > dd > ul > li > a')
            all_my_course_data = {}
            for course in courses:
                course_link = self.url + '/course/view.php?id=' + re.search(r'course=(\d+)&', course['href']).group(1)
                course_other_data = course.text.split("_")
                if len(course_other_data) >= 3:
                    course_name, course_id, sem_id = course_other_data[:3]
                    all_my_course_data[int(course_id)] = {
                        'name': course_name,
                        'sem_id': int(sem_id),
                        'link': course_link
                    }
            from pprint import pprint
            pprint(all_my_course_data)
            
            # https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=18507&showallcourses=1
            # https://mlearning.hoasen.edu.vn/user/index.php?id=18512
            # Course: https://mlearning.hoasen.edu.vn/course/view.php?id=18512
            # https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=18512
            
            # courses = soup.select('div[role="listitem"]')[1:] # The first card is eliminated as it is the recently accessed course, which is already included in the course overview
            # for course in courses:
            #     course_link_tag = course.select_one('a.aalink.coursename.mr-2')
            #     course_link = course_link_tag['href'].strip()
            #     course_other_data = course_link_tag.select_one('span.multiline').text.strip().split("_")
            #     if len(course_other_data) >= 3:
            #         course_name, course_id, sem_id = course_other_data[:3]
            #         all_my_course_data[int(course_id)] = {
            #             'name': course_name,
            #             'sem_id': int(sem_id),
            #             'link': course_link
            #         }
        else:
            return
        # return all_my_course_data

    def scrape_profile(self, page_source):
        # Add the logic to scrape profile data here...
        # This could be similar to the code in your active file from lines 93 to 97
        return

    def quit_driver(self):
        self.driver.quit()
        return



# def scrape_my_course_data():    
#     # Step 6: Scrape my profile data
#     my_name = soup.select_one('span.usertext.mr-1').text()
    
    
#     document = {
#         '_id': int(os.environ['MY_ID']),
#         'name': os.environ['MY_NAME'],
#         'email': os.environ['MLEARNING_USERNAME'],
#         'profile_link': my_profile_link,
#         'courses': all_my_course_data
#     }
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
    load_dotenv()
    url = 'https://mlearning.hoasen.edu.vn'
    username = os.environ['MLEARNING_USERNAME']
    password = os.environ['MLEARNING_PASSWORD']
    
    try:
        scraper = Scraper(url, username, password)
        # scraper.log_in()
        scraper.scrape_courses()
    finally:
        # scraper.quit_driver()
        a=1



if __name__ == "__main__":
    main()