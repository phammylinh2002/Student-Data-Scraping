#!/usr/local/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from random import randint
import time
import os
import re
    

class Scraper:
    def __init__(self, url, username, password):
        self.driver = webdriver.Chrome()
        self.url = url
        self.username = username
        self.password = password


    def wait(self):
        time.sleep(randint(3, 10))


    def log_in(self):
        """
        Logs in to the website using the provided username and password.

        This method navigates to the login page, fills in the login form with the provided username and password,
        and submits the form to log in to the website.

        Args:
            self (object): The instance of the class.

        Returns:
            None
        """
        
        self.driver.get(self.url)
        # Find and fill in the login form
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        # Submit the login form
        password_input.send_keys(Keys.RETURN)
        self.wait()

    
    def scrape_courses(self, profile_link):
        """
        Scrapes the courses from the given profile link.

        Args:
            profile_link (str): The link to the profile page.

        Returns:
            list: A list of dictionaries containing the course data, including the course link and name.
        """
        
        # Get all courses page soup
        show_all_courses_link = profile_link + '&showallcourses=1'
        self.driver.get(show_all_courses_link)
        self.wait()
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Scraping the soup
        courses = soup.find('dt', string='Course profiles').find_next_sibling('dd').find_all('a')
        invalid_courses = []
        all_course_data = []
        for course in courses:
            course_link = self.url + '/course/view.php?id=' + re.search(r'course=(\d+)', course['href']).group(1)
            course_name_match = re.search(r"([\w\s\(\)]+_\d{4}_\d{4})", course.text)
            if course_name_match is not None:
                course_name = course_name_match.group(1)
                course_data = {
                    'link': course_link,
                    'name': course_name
                }
                all_course_data.append(course_data)
            else:
                invalid_courses.append(course.text)
                continue
        print(f"Found {len(invalid_courses)} courses in his/her data: {invalid_courses}")
        return all_course_data
    
    
    def scrape_profile(self, is_mine=True, profile_link=None):
        """
        Scrapes the profile data of a user.

        Args:
            is_mine (bool, optional): Indicates whether the profile is of the logged-in user. Defaults to True.
            profile_link (str, optional): The link to the profile. Required when `is_mine` is False and vice versa.

        Returns:
            dict: A dictionary containing the scraped profile data.
                - 'email': The email address of the user.
                - 'name': The name of the user.
                - 'profile_link': The link to the profile.
                - '_id' (optional): The Yahoo ID of the user, converted to an integer.
        """
        
        # Get profile_link if the profile is mine
        if is_mine == True and profile_link == None:
            profile_link = self.driver.find_element(By.XPATH, '//*[@id="loggedin-user"]/a').get_attribute('href')
        elif (is_mine == False and profile_link == None) or (is_mine == True and profile_link != None):
            raise ValueError("The parameter `profile_link` is required when `is_mine` is False and vice versa.")
        
        # Scrape profile data
        self.driver.get(profile_link)
        self.wait()
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        name = soup.find('div', class_='page-header-headings').find('h1').text
        print(f"\n{name}'s data is being scraped...")        
        email = soup.find('dt', string='Email address').find_next_sibling('dd').find('a').text
        try: 
            id = soup.find('dt', string='Yahoo ID').find_next_sibling('dd').find('a').text
        except AttributeError:
            id = None
        
        # Shape the profile data 
        profile_data = {
            'email': email,
            'name': name,
            'profile_link': profile_link
        }
        if id is not None:
            profile_data['_id'] = int(id)  
        
        return profile_data
    
    
    def scrape_classmate_profile_links(self, your_profile_link, your_course_data):
        """
        Scrape the profile links of classmates from the given course data.

        Args:
            your_profile_link (str): The link to your own profile.
            your_course_data (list): A list of dictionaries containing course information.

        Returns:
            set: A set of profile links of classmates.
        """
        
        # Check if your_course_data is a list
        if not isinstance(your_course_data, list):
            raise TypeError('your_course_data must be a list')

        all_classmate_profile_links = set()
        for index, course in enumerate(your_course_data, start=1):
            # Prepare the soup
            classmate_list_link = course['link'].replace('course', 'user').replace('view', 'index')
            self.driver.get(classmate_list_link)
            self.wait()
            show_all = self.driver.find_element(By.CSS_SELECTOR, "a[data-action='showcount']").get_attribute('href')
            self.driver.get(show_all)
            self.wait()
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Print number of classmates
            no_of_classmates = int(self.driver.find_element(By.CSS_SELECTOR, 'p[data-region="participant-count"]').text.split()[0]) - 1
            print(f"{str(index)}. There are {str(no_of_classmates)} classmates in class {course['name']}.", end=" ")

            # Scrape!
            classmates = soup.select('table#participants a')
            classmate_profile_links = set()
            current_no_of_classmates = len(all_classmate_profile_links)
            for classmate in classmates:
                profile_link = classmate['href'].replace('view', 'profile').split('&')[0]
                if profile_link != your_profile_link and 'profile' in profile_link:
                    classmate_profile_links.add(profile_link)
                else:
                    continue            
                
            # Update all_classmate_profile_links
            all_classmate_profile_links.update(classmate_profile_links)
            print(f"{len(all_classmate_profile_links) - current_no_of_classmates} new classmate(s).")
            
        return all_classmate_profile_links
    
    
    def quit_driver(self):
        self.driver.quit()
        return



def main():
    start_time = time.time()
    load_dotenv()
    url = 'https://mlearning.hoasen.edu.vn'
    username = os.environ['MLEARNING_USERNAME']
    password = os.environ['MLEARNING_PASSWORD']
    
    try:
        scraper = Scraper(url, username, password)
        scraper.log_in()
        
        # Scrape your student data
        your_student_data = scraper.scrape_profile()
        your_profile_link = your_student_data['profile_link']
        your_course_data = scraper.scrape_courses(your_profile_link)
        your_student_data['courses'] = your_course_data
        print(f"\nSuccessfully scraped your student data. You attended in {len(your_student_data['courses'])} classes.\n")
        
        # Scrape your classmate profile links
        all_classmate_profile_links = scraper.scrape_classmate_profile_links(your_profile_link, your_course_data[:2])
        print(f"\nFound {len(all_classmate_profile_links)} unique classmates in {len(your_course_data)} classes")
        
        # Scrape your classmates' data
        all_classmate_data = []
        for link in all_classmate_profile_links:
            classmate_data = scraper.scrape_profile(is_mine=False, profile_link=link)
            classmate_data['courses'] = scraper.scrape_courses(link)
            all_classmate_data.append(classmate_data)
            print(f"Successfully scraped {classmate_data['name']}'s data. He/She attended in {len(classmate_data['courses'])} classes.")
                
        return all_classmate_data

    finally:
        scraper.quit_driver()
        end_time = time.time()
        runtime = end_time - start_time
        print(f"\nRuntime of the program is {round(runtime//60)}m{round(runtime%60)}s")
  


if __name__ == "__main__":
    main()
