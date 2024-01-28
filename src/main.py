#!/usr/local/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        # Get all courses page soup
        self.driver.get(profile_link)
        self.wait()
        self.driver.find_element(By.XPATH, '//*[@title="View more"]').click()
        self.wait()
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
        self.wait()
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        name = soup.find('div', class_='page-header-headings').find('h1').text
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
    
    
    def scrape_classmate_profile_links(self, my_profile_link, classmate_list_links):
        # Check if classmate_list_links is a dictionary
        if not isinstance(classmate_list_links, dict):
            raise TypeError('classmate_list_links must be a dictionary')

        all_classmate_profile_links = set()
        for class_id, link in classmate_list_links.items():
            # Prepare the soup
            self.driver.get(link)
            self.wait()
            show_all = self.driver.find_element(By.CSS_SELECTOR, "a[data-action='showcount']").get_attribute('href')
            self.driver.get(show_all)
            self.wait()
            # show_all.click()
            self.wait()
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # https://mlearning.hoasen.edu.vn/course/view.php?id=16928
            # https://mlearning.hoasen.edu.vn/user/index.php?id=18507
            # https://mlearning.hoasen.edu.vn/user/index.php?contextid=1247743&id=18507&perpage=5000
            
            # Print number of classmates
            no_of_classmates = int(self.driver.find_element(By.CSS_SELECTOR, 'p[data-region="participant-count"]').text.split()[0]) - 1
            print(f"There are {str(no_of_classmates)} classmates in class {class_id}.", end=" ")
                         
            # Scrape!
            classmates = soup.select('table#participants a')
            classmate_profile_links = set()
            current_no_of_classmates = len(all_classmate_profile_links)
            for classmate in classmates:
                profile_link = classmate['href'].replace('view', 'profile').split('&')[0]
                if profile_link != my_profile_link and 'profile' in profile_link:
                    classmate_profile_links.add(profile_link)
                else:
                    continue            
            
            # Update all_classmate_profile_links
            all_classmate_profile_links.update(classmate_profile_links)
            print(len(all_classmate_profile_links) - current_no_of_classmates, "new classmate(s).")
            
        return all_classmate_profile_links
    
    
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
        my_student_data = scraper.scrape_profile()
        my_profile_link = my_student_data['profile_link']
        my_student_data['courses'] = scraper.scrape_courses(my_profile_link)
        print(f"\nSuccessfully scraped my student data. I attended in {len(my_student_data['courses'])} classes.\n")
        # my_student_data = {
        #     'courses': {
        #         1157: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18019',
        #                 'name': 'Corporate Finance',
        #                 'sem_id': 2234},
        #         1202: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=17951',
        #                 'name': 'Luật và Đạo đức Kinh doanh',
        #                 'sem_id': 2234},
        #         1271: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=17039',
        #                 'name': 'Using and Managing IS',
        #                 'sem_id': 2233},
        #         1276: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18546',
        #                 'name': 'Interaction Design',
        #                 'sem_id': 2331},
        #         1277: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18547',
        #                 'name': 'Interaction Design',
        #                 'sem_id': 2331},
        #         1292: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16116',
        #                 'name': 'Thiết kế Web và Đồ họa',
        #                 'sem_id': 2232},
        #         1314: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18512',
        #                 'name': 'Business System Analysis',
        #                 'sem_id': 2331},
        #         1333: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=17853',
        #                 'name': 'Tư duy Phản biện',
        #                 'sem_id': 2234},
        #         1633: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=15937',
        #                 'name': 'Kinh tế Vĩ mô',
        #                 'sem_id': 2231},
        #         1844: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=12608',
        #                 'name': 'Human Resource Management',
        #                 'sem_id': 2133},
        #         1973: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16928',
        #                 'name': 'Hệ quản trị Cơ sở Dữ liệu',
        #                 'sem_id': 2233},
        #         1974: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16929',
        #                 'name': 'Hệ quản trị Cơ sở Dữ liệu',
        #                 'sem_id': 2233},
        #         1979: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16973',
        #                 'name': 'Phân tích thiết kế HĐT',
        #                 'sem_id': 2233},
        #         1980: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16974',
        #                 'name': 'Phân tích thiết kế HĐT',
        #                 'sem_id': 2233},
        #         1997: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=14943',
        #                 'name': 'Nhập môn Kinh doanh Quốc tế',
        #                 'sem_id': 2231},
        #         2056: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18507',
        #                 'name': 'Đồ án Chuyên ngành HTTT',
        #                 'sem_id': 2331},
        #         2072: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=15178',
        #                 'name': 'Nguyên lý Kế toán',
        #                 'sem_id': 2231},
        #         2546: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16985',
        #                 'name': 'Ứng dụng thương mại điện tử',
        #                 'sem_id': 2233},
        #         2547: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=17040',
        #                 'name': 'Quản lý Bảo mật Thông tin',
        #                 'sem_id': 2233},
        #         2548: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16931',
        #                 'name': 'Khai thác dữ liệu kinh doanh',
        #                 'sem_id': 2233},
        #         2555: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=16986',
        #                 'name': 'Ứng dụng thương mại điện tử',
        #                 'sem_id': 2233},
        #         2704: {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=14498',
        #                 'name': 'Nhập môn Cơ sở Dữ liệu',
        #                 'sem_id': 2231}},
        #     'email': 'LINH.PM07144@SINHVIEN.HOASEN.EDU.VN',
        #     'name': 'Phạm Mỹ Linh',
        #     'profile_link': 'https://mlearning.hoasen.edu.vn/user/profile.php?id=19701'}
        
        
        # Scrape my classmate profile links
        classmate_list_links = {key:value['link'].replace('course', 'user').replace('view', 'index') for key, value in my_student_data['courses'].items()}
        all_classmate_profile_links = scraper.scrape_classmate_profile_links(my_profile_link, classmate_list_links)
        print(f"\nFound {len(all_classmate_profile_links)} unique classmates in {len(classmate_list_links)} classes")
        
        print(f"\nMy student data:\n{my_student_data}")
        print(f"\nMy classmate profile links:\n{all_classmate_profile_links}")
        
        
    finally:
        scraper.quit_driver()
        # a=1


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    runtime = end_time - start_time
    print(f"\nRuntime of the program is {round(runtime//60)}m{round(runtime%60)}s")

                
# My profile and the chosen course: https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=16928
# My profile:                       https://mlearning.hoasen.edu.vn/user/profile.php?id=19701
# Course:       https://mlearning.hoasen.edu.vn/course/view.php?id=16928
# Participants: https://mlearning.hoasen.edu.vn/user/index.php?id=16928
# https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=18507&showallcourses=1
# https://mlearning.hoasen.edu.vn/user/index.php?id=18512
# Course: https://mlearning.hoasen.edu.vn/course/view.php?id=18512
# https://mlearning.hoasen.edu.vn/user/view.php?id=19701&course=18512