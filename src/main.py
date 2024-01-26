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

    def scrape_courses(self, profile_link):
        # Get all courses page soup
        self.driver.get(profile_link)
        time.sleep(3)
        self.driver.find_element(By.XPATH, '//*[@title="View more"]').click()
        time.sleep(3)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Scraping the soup
        courses = soup.find('dt', string='Course profiles').find_next_sibling('dd').find_all('a')
        all_course_data = {}
        for course in courses:
            course_link = self.url + '/course/view.php?id=' + re.search(r'course=(\d+)', course['href']).group(1)
            course_other_data = course.text.split("_")
            if len(course_other_data) >= 3:
                course_name, course_id, sem_id = course_other_data[:3]
                all_course_data[int(course_id)] = {
                    'name': course_name,
                    'sem_id': int(sem_id),
                    'link': course_link
                }
        return all_course_data
    
    
    def scrape_profile(self, is_mine=True, profile_link=None):
        # Get profile_link if the profile is mine
        if is_mine == True and profile_link == None:
            profile_link = self.driver.find_element(By.XPATH, '//*[@id="loggedin-user"]/a').get_attribute('href')
        elif (is_mine == False and profile_link == None) or (is_mine == True and profile_link != None):
            raise ValueError("The parameter `profile_link` is required when `is_mine` is False and vice versa.")
        
        # Scrape profile data
        self.driver.get(profile_link)
        time.sleep(3)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        name = soup.find('div', class_='page-header-headings').find('h1').text
        email = soup.find('dt', string='Email address').find_next_sibling('dd').find('a').text
        try: 
            id = soup.find('dt', string='Yahoo ID').find_next_sibling('dd').find('a')
        except AttributeError:
            id = None
        
        # Shape the profile data 
        profile_data = {
            'email': email,
            'name': name,
            'profile_link': profile_link
        }
        if id is not None:
            profile_data['_id'] = int(id.text)  
        
        return profile_data
    
    
    def quit_driver(self):
        self.driver.quit()
        return


def main():
    load_dotenv()
    url = 'https://mlearning.hoasen.edu.vn'
    username = os.environ['MLEARNING_USERNAME']
    password = os.environ['MLEARNING_PASSWORD']
    
    try:
        scraper = Scraper(url, username, password)
        scraper.log_in()
        
        # Scrape my student data
        profile_data = scraper.scrape_profile()
        profile_data['courses'] = scraper.scrape_courses(profile_data['profile_link'])
        document = profile_data
        
    finally:
        scraper.quit_driver()
        # a=1


if __name__ == "__main__":
    main()



# Course: https://mlearning.hoasen.edu.vn/course/view.php?id=16928
# My profile and the chosen course: https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=16928
# My profile: https://mlearning.hoasen.edu.vn/user/profile.php?id=19701
# Course participants: https://mlearning.hoasen.edu.vn/user/index.php?id=16928
# https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=18507&showallcourses=1
# https://mlearning.hoasen.edu.vn/user/index.php?id=18512
# Course: https://mlearning.hoasen.edu.vn/course/view.php?id=18512
# https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=18512