#!/usr/local/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from random import randint
from pymongo import MongoClient, errors
import traceback
import time
import os
import re
    


class Scraper:
    def __init__(self, url, username, password):
        self.driver = webdriver.Chrome()
        self.url = url
        self.username = username
        self.password = password
    
    
    def __enter__(self):
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
    
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Quits the driver and prints any exceptions that were raised within the with block.

        Args:
            self (object): The instance of the class.

        Returns:
            None
        """
        
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        self.driver.quit()


    def wait(self):
        time.sleep(randint(3, 10))   

    
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
    
    
    def scrape_classmate_profile_links(self, your_profile_link, your_course_data, is_update=False, old_classmate_profile_links=set()):
        """
        Scrapes the profile links of classmates based on the provided course data.

        Args:
            your_profile_link (str): The link to your own profile.
            your_course_data (list): A list of dictionaries containing course data.
            is_update (bool, optional): Indicates whether this is an update or not. Defaults to False.
            old_classmate_profile_links (set, optional): The set of old classmate profile links. Required when is_update is False. Defaults to an empty set.

        Returns:
            set: The set of profile links based on the update.

        Raises:
            TypeError: If your_course_data is not a list.
            ValueError: If old_classmate_profile_links is not provided when is_update is False.
        """
        # Check if your_course_data is a list
        if not isinstance(your_course_data, list):
            raise TypeError('your_course_data must be a list')

        # Check if this is an update
        if is_update == True and len(old_classmate_profile_links) != 0:
            all_classmate_profile_links = old_classmate_profile_links
            current_no_of_classmates = len(all_classmate_profile_links)
        elif is_update == False and len(old_classmate_profile_links) == 0:
            all_classmate_profile_links = set()
        else:
            raise ValueError('`old_classmate_profile_links` must be provided when `is_update` is False')
        
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
            for classmate in classmates:
                profile_link = classmate['href'].replace('view', 'profile').split('&')[0]
                if profile_link != your_profile_link and 'profile' in profile_link:
                    classmate_profile_links.add(profile_link)
                else:
                    continue            
                
            # Update all_classmate_profile_links
            all_classmate_profile_links.update(classmate_profile_links)
            print(f"{len(all_classmate_profile_links) - current_no_of_classmates} new classmate(s).")
            current_no_of_classmates = len(all_classmate_profile_links)
        
        # Return the set of profile links based on the update
        if is_update == True:
            return all_classmate_profile_links.difference(old_classmate_profile_links)
        else:
            return all_classmate_profile_links



### TO-DO: Write a MongoDB collection class and its methods to insert, update, delete, and query data ###
class MongoDBCollection:
    def __init__(self, connection_string, db_name, collection_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        self.client.close()

    def insert(self, data):
        try:
            if isinstance(data, list):
                result = self.collection.insert_many(data)
                print(f"Successfully inserted {len(result.inserted_ids)} documents into the collection `{self.collection.name}`")
            else:
                raise ValueError("Data must be provided as a list of dictionaries")
        except errors.PyMongoError as e:
            print(f"An error occurred while inserting the data: {e}")            
            
    def update(self, query, new_data):
        return self.collection.update_one(query, {'$set': new_data})

    def delete(self, query):
        return self.collection.delete_one(query)

    def find(self, amount='one', query={}):
        if amount == 'one':
            return self.collection.find_one(query)
        elif amount == 'many':
            return self.collection.find(query)



def scrape_all_student_data(scraper):
    """
    Scrapes student data for the logged-in user and their classmates.

    Args:
        scraper: An instance of the scraper class used for scraping student data.

    Returns:
        None
    """
    scraper.log_in()
    
    # Scrape your student data
    your_student_data = scraper.scrape_profile()
    your_profile_link = your_student_data['profile_link']
    your_course_data = scraper.scrape_courses(your_profile_link)
    your_student_data['courses'] = your_course_data
    print(f"\nSuccessfully scraped your student data. You attended in {len(your_student_data['courses'])} classes.\n")
    
    # Scrape your classmate profile links
    all_classmate_profile_links = scraper.scrape_classmate_profile_links(your_profile_link, your_course_data)
    print(f"\nFound {len(all_classmate_profile_links)} unique classmates in {len(your_course_data)} classes")
    
    # Scrape your classmates' data
    all_classmate_data = []
    for link in all_classmate_profile_links:
        classmate_data = scraper.scrape_profile(is_mine=False, profile_link=link)
        classmate_data['courses'] = scraper.scrape_courses(link)
        all_classmate_data.append(classmate_data)
        print(f"Successfully scraped {classmate_data['name']}'s data. He/She attended in {len(classmate_data['courses'])} classes.")
    
    # Insert all scraped data into the collection
    all_scraped_data = all_classmate_data.append(your_student_data)
    with MongoDBCollection(os.environ['MONGODB_CONNECTION_STRING'], os.environ['MONGODB_DB_NAME'], os.environ['MONGODB_COLLECTION_NAME']) as collection:
        collection.insert(all_scraped_data)



def scrape_new_student_data(scraper):
    """
    Scrapes and inserts new student data into the collection.

    Args:
        scraper: An instance of the scraper class used for scraping data.

    Returns:
        None
    """
    # Check data in the collection
    collection = MongoDBCollection(os.environ['MONGODB_CONNECTION_STRING'], os.environ['MONGODB_DB_NAME'], os.environ['MONGODB_COLLECTION_NAME'])
    data_count = collection.find().count()
    if data_count == 0:
        print("No data found in the collection. Please scrape all student data first.")
        return 
    
    # Scrape and insert your new courses
    your_old_student_data = collection.find(amount='one', query={'email': os.environ['MLEARNING_USERNAME']})
    your_profile_link = your_old_student_data['profile_link']
    your_old_courses = [course['name'] for course in your_old_student_data['courses']]
    your_all_current_courses = scraper.scrape_courses(your_profile_link)
    your_new_courses = [course for course in your_all_current_courses if course['name'] not in your_old_courses]
    if len(your_new_courses) > 0:
        print(f"\nYou have {len(your_new_courses)} new courses.")
        collection.update({'email': os.environ['MLEARNING_USERNAME']}, {'courses': your_all_current_courses})
    else:
        print("\nYou do not have any new course.")
        return
    
    # Scrape and insert your new classmates
    old_classmate_profile_links = set([classmate['profile_link'] for classmate in collection.find(amount='many', query={'email': {'$ne': os.environ['MLEARNING_USERNAME']}})])
    new_classmate_profile_links = scraper.scrape_classmate_profile_links(your_profile_link, your_new_courses, is_update=True, old_classmate_profile_links=old_classmate_profile_links)
    no_new_classmates = len(new_classmate_profile_links)
    if no_new_classmates == 0:
        print("No new classmates found.")
        return
    else:
        print(f"\nFound {no_new_classmates} unique classmates in your {len(your_new_courses)} new classes.")
        new_classmate_data = []
        for link in new_classmate_profile_links:
            classmate_data = scraper.scrape_profile(is_mine=False, profile_link=link)
            classmate_data['courses'] = scraper.scrape_courses(link)
            new_classmate_data.append(classmate_data)
            print(f"Successfully scraped {classmate_data['name']}'s data. He/She attended in {len(classmate_data['courses'])} classes.")
        collection.insert(new_classmate_data)
    


def update_my_classmate_courses(scraper):
    """
    Updates the courses of your classmates.

    Args:
        scraper: An instance of the scraper class used for scraping data.

    Returns:
        None
    """
    # Check data in the collection
    collection = MongoDBCollection(os.environ['MONGODB_CONNECTION_STRING'], os.environ['MONGODB_DB_NAME'], os.environ['MONGODB_COLLECTION_NAME'])
    data_count = collection.find().count()
    if data_count == 0:
        print("No data found in the collection. Please scrape all student data first.")
        return 
    
    
    classmate_data = collection.find(amount='many', query={'email': {'$ne': os.environ['MLEARNING_USERNAME']}})
    for classmate in classmate_data:
        profile_link = classmate['profile_link']
        classmate_course_data = scraper.scrape_courses(profile_link)
        current_no_classes = len(classmate['courses'])
        updated_no_classes = len(classmate_course_data)
        print(f"{classmate['name']} has {updated_no_classes - current_no_classes} new class(es). Total class(es): {updated_no_classes}.")
        collection.update({classmate['_id']}, {'courses': classmate_course_data})
        
    

def main():
    start_time = time.time()
    load_dotenv()
    url = 'https://mlearning.hoasen.edu.vn'
    username = os.environ['MLEARNING_USERNAME']
    password = os.environ['MLEARNING_PASSWORD']
    
    with Scraper(url, username, password) as scraper:
        try:
            which_action = input("Which action do you want to perform?\n[1] Scrape all student data\n[2] Scrape new student data\n[3] Update my classmate course data\nYour answer: ")
            if which_action == '1':
                scrape_all_student_data(scraper)
            elif which_action == '2':
                scrape_new_student_data(scraper)
            elif which_action == '3':
                update_my_classmate_courses(scraper)
            else:
                print("Invalid input. Please try again.")
        finally:
            end_time = time.time()
            runtime = end_time - start_time
            print(f"\nRuntime of the program is {round(runtime//60)}m{round(runtime%60)}s")
  


if __name__ == "__main__":
    main()
