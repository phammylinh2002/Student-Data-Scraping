#!/usr/local/bin/python3

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from pymongo import MongoClient, errors
import time
import os
import re
    

class Scraper:
    def __init__(self, url, username, password):
        self.driver = webdriver.Chrome()
        self.url = url
        self.username = username
        self.password = password
    
    def login(self):
        # Navigate to MLearning login page
        self.driver.get(self.url)
        # Find and fill in the login form
        username_input = self.driver.find_element(By.NAME, 'username')
        password_input = self.driver.find_element(By.NAME, 'password')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        # Submit the login form
        password_input.send_keys(Keys.RETURN)
        self.wait()
        if self.driver.current_url == self.url:
            print("\nLogin failed. Please check your username and password.")
        else:
            print("\nSuccessfully logged in.")    
            return self
       
    def wait(self, seconds=0):
        try: 
            if time == 0:
                WebDriverWait(self.driver, 100).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            else:
                time.sleep(seconds)
        except Exception as e:
            print(f"An error occurred while waiting: {e}")

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
        all_course_data = {'valid':[], 'invalid':[]}
        for course in courses:
            course_link = self.url + '/course/view.php?id=' + re.search(r'course=(\d+)', course['href']).group(1)
            course_name_match = re.search(r"(.+_\d{4}_\d{4})", course.text)
            if course_name_match is not None:
                course_name = course_name_match.group(1).strip()
                course_data = {'link': course_link, 'name': course_name}
                all_course_data['valid'].append(course_data)
            else:
                course_name = course.text.strip()
                course_data = {'link': course_link, 'name': course_name}
                all_course_data['invalid'].append(course_data)
                continue
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
        profile_data = {
                'name': name,
                'profile_link': profile_link
            }
        try:
            email_element = soup.find('dt', string='Email address')
            if email_element is not None:
                profile_data['email'] = email_element.find_next_sibling('dd').find('a').text

            id_element = soup.find('dt', string='Yahoo ID')
            if id_element is not None:
                profile_data['_id'] = int(id_element.find_next_sibling('dd').find('a').text)
        except Exception as e:
            print(f"An error occurred while scraping {name}'s data: {e}. Profile link: {profile_link}.")

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
            current_no_of_classmates = 0
        else:
            raise ValueError('`old_classmate_profile_links` must be provided when `is_update` is False')
        
        for index, course in enumerate(your_course_data, start=1):
            # Prepare the soup
            classmate_list_link = course['link'].replace('course', 'user').replace('view', 'index')
            self.driver.get(classmate_list_link)
            self.wait()
            show_all = self.driver.find_element(By.CSS_SELECTOR, "a[data-action='showcount']").get_attribute('href')
            self.driver.get(show_all)
            self.wait(1)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Print number of classmates
            no_of_classmates = int(self.driver.find_element(By.CSS_SELECTOR, 'p[data-region="participant-count"]').text.split()[0]) - 1
            print(f"{str(index)}. {course['name']}: {str(no_of_classmates)} classmates.", end=" ")

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
            print(f"{len(all_classmate_profile_links) - current_no_of_classmates} is new.")
            current_no_of_classmates = len(all_classmate_profile_links)
        
        # Return the set of profile links based on the update
        if is_update == True:
            return list(all_classmate_profile_links.difference(old_classmate_profile_links))
        else:
            return list(all_classmate_profile_links)

class MongoDBCollection:
    def __init__(self, connection_string, db_name, collection_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def insert(self, data):
        try:
            if isinstance(data, dict):
                self.collection.insert_one(data)
            else:
                raise ValueError("Data must be provided as a dictionary. Only 1 document can be inserted at a time.")
        except errors.PyMongoError as e:
            print(f"An error occurred while inserting the data: {e}")            
            
    def update(self, query, new_data):
        return self.collection.update_one(query, {'$set': new_data})

    def delete(self, amount='all', query={}):
        if amount == 'one' and len(query) != 0:
            return self.collection.delete_one(query)
        elif (amount == 'some' and len(query) != 0) or (amount == 'all' and len(query) == 0):
            return self.collection.delete_many(query)
        else:
            raise ValueError("`amount` must be 'one', 'some', or 'all'. If `amount` is 'one' or 'some', `query` must be provided.")

    def find(self, amount='one', query={}):
        if amount == 'one':
            return self.collection.find_one(query)
        elif amount == 'many':
            return self.collection.find(query)

    def count(self, filter={}):
        if filter:
            return self.collection.count_documents(filter)
        else:
            return self.collection.count_documents({})

    def replace(self, filter, data):
        return self.collection.replace_one(filter, data)


def scrape_your_student_data():
    with MongoDBCollection(connection_string, db_name, collection_name) as collection:
        your_data_in_db = collection.count(filter={'email': username})
        if your_data_in_db != 0:
            if your_data_in_db > 1:
                delete_one = input("There are duplicates of your student data in the collection. Do you want to delete one? (y/n):").lower()
                if delete_one in ['y', 'n']:
                    if delete_one == 'y':
                        collection.delete(amount='one', query={'email': username})
                        print("Successfully deleted one duplicate of your student data in the collection.")
                        scrape_your_student_data()
                    else:
                        print("No data was deleted.")
                else:
                    print("Invalid input. Please try again.")
                    return
            if your_data_in_db == 1:
                is_updated = input("Your data is already in the collection. It will be updated. Do you want to continue? (y/n): ").lower()
                if is_updated in ['y', 'n']:
                    if is_updated == 'y':
                        pass
                    else:
                        print("No data was updated.")
                else:
                    print("Invalid input. Please try again.")            
                    return 
        if your_data_in_db == 0 or is_updated == 'y':
            scraper = Scraper(url, username, password).login()
            your_student_data = scraper.scrape_profile()
            your_profile_link = your_student_data['profile_link']
            your_course_data = scraper.scrape_courses(your_profile_link)
            your_student_data['courses'] = your_course_data
            scraper.driver.quit()
            print(f"Successfully scraped your student data. You attended in {len(your_student_data['courses']['valid']) + len(your_student_data['courses']['invalid'])} classes. {len(your_student_data['courses']['valid'])} of them are valid.\n")
            if your_data_in_db is None:
                collection.insert(your_student_data)
                print("Your student data has been successfully inserted into the collection.")
            else:
                collection.replace({'email': username}, your_student_data)
                print("Your student data has been successfully updated in the collection.")


def scrape_classmate_links():
    with MongoDBCollection(connection_string, db_name, collection_name) as collection:
        data_count = collection.count()
        if data_count > 1:
            print("There is already classmate data in the collection. Please clear the data to perform this action.")
            delete = input("Do you want to delete all data (except your student data) in the collection right now? (y/n): ").lower()
            if delete in ['y', 'n']:
                if delete == 'y':
                    result = collection.delete(amount='some', query={'email': {'$ne': username}})
                    print(f"Successfully deleted all data ({result.deleted_count} documents) in the collection.\n")
                    scrape_classmate_links()
                else:
                    print("No data was deleted.")
            else:
                print("Invalid input. Please try again.")
            return
        else:
            scraper = Scraper(url, username, password).login()
            your_student_data = collection.find(amount='one', query={'email': username})
            your_profile_link = your_student_data['profile_link']
            your_valid_course_data = your_student_data['courses']['valid']
            print(f"\nScraping your classmates' profile links based on your {len(your_valid_course_data)} valid classes...")
            all_classmate_profile_links = scraper.scrape_classmate_profile_links(your_profile_link, your_valid_course_data)
            print(f"\nFound {len(all_classmate_profile_links)} unique classmates in {len(your_valid_course_data)} valid classes.\n")
            scraper.driver.quit()
    return all_classmate_profile_links


def scrape_classmate_data(scraper, links):
    """
    Scrapes student data for the logged-in user and their classmates.

    Args:
        scraper: An instance of the scraper class used for scraping student data.

    Returns:
        None
    """
    with MongoDBCollection(connection_string, db_name, collection_name) as collection:
        for i, link in enumerate(links, start=1):
            try:
                if i % 10 == 0:
                    time.sleep(30)
                classmate_data = scraper.scrape_profile(is_mine=False, profile_link=link)
                classmate_data['courses'] = scraper.scrape_courses(link)
                collection.insert(classmate_data)
                print(f"{classmate_data['name']}'s data was scraped.")
            except Exception as e:
                print(f"{e}")


def scrape_new_student_data():
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
    scraper = Scraper(url, username, password).login()
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
        collection.insert(new_classmate_data)
    scraper.driver.quit()


def update_your_classmate_courses():
    """
    Updates the courses of your classmates.

    Args:
        scraper: An instance of the scraper class used for scraping data.

    Returns:
        None
    """
    # Check data in the collection
    collection = MongoDBCollection(connection_string, db_name, collection_name)
    data_count = collection.find().count()
    if data_count == 0:
        print("No data found in the collection. Please scrape all student data first.")
        return 
    
    
    classmate_data = collection.find(amount='many', query={'email': {'$ne': username}})
    scraper = Scraper(url, username, password).login()
    for classmate in classmate_data:
        profile_link = classmate['profile_link']
        classmate_course_data = scraper.scrape_courses(profile_link)
        current_no_classes = len(classmate['courses'])
        updated_no_classes = len(classmate_course_data)
        print(f"{classmate['name']} has {updated_no_classes - current_no_classes} new class(es). Total class(es): {updated_no_classes}.")
        collection.update({classmate['_id']}, {'courses': classmate_course_data})
    scraper.driver.quit()
    

def main():
    start_time = time.time()
    load_dotenv()
    global url, username, password, connection_string, db_name, collection_name
    url = 'https://mlearning.hoasen.edu.vn'
    username = os.environ['MLEARNING_USERNAME']
    password = os.environ['MLEARNING_PASSWORD']
    connection_string = os.environ['MONGODB_CONNECTION_STRING']
    db_name = os.environ['MONGODB_DB_NAME']
    collection_name = os.environ['MONGODB_COLLECTION_NAME']
    
    option1 = '\n[1] Scrape your data'
    option2 = '\n[2] Scrape ALL classmate data'
    option3 = '\n[3] Scrape NEW classmate data'
    option4 = '\n[4] Update your classmate course data'
    which_action = input(f"Which action do you want to perform?{option1}{option2}{option3}{option4}\nYour answer: ")
    if which_action in ['1', '2', '3', '4']:
        if which_action == '1':
            scrape_your_student_data()
        elif which_action == '2':
            all_classmate_profile_links = scrape_classmate_links()
            # Split the links into equal-sized chunks for each scraper
            no_of_scrapers = 10
            links_per_scraper = len(all_classmate_profile_links) // no_of_scrapers
            links_chunks = [all_classmate_profile_links[i*links_per_scraper:(i+1)*links_per_scraper] for i in range(no_of_scrapers)]
            if len(all_classmate_profile_links) % no_of_scrapers != 0:
                links_chunks[-1].extend(all_classmate_profile_links[no_of_scrapers*links_per_scraper:])
            # Scrape the data
            with ThreadPoolExecutor(max_workers=no_of_scrapers) as executor:
                scrapers = list(executor.map(lambda _: Scraper(url, username, password).login(), range(no_of_scrapers)))
                futures = [executor.submit(scrape_classmate_data, scraper, links_chunk) for scraper, links_chunk in zip(scrapers, links_chunks)]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"An error occurred: {e}")
            for scraper in scrapers:
                scraper.driver.quit()
        elif which_action == '3':
            scrape_new_student_data()
        elif which_action == '4':
            update_your_classmate_courses()
    else:
        print("Invalid input. Please try again.")
    
    end_time = time.time()
    runtime = end_time - start_time
    print(f"\nRuntime of the program is {round(runtime//60)}m{round(runtime%60)}s")


if __name__ == "__main__":
    main()
