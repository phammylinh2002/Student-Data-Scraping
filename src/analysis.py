from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()
# Connect to MongoDB
connection_string = os.environ['MONGODB_CONNECTION_STRING']
db_name = os.environ['MONGODB_DB_NAME']
collection_name = os.environ['MONGODB_COLLECTION_NAME']
collection = MongoClient(connection_string)[db_name][collection_name]

# Get the list of the valid courses I took
classmate_counts = {}
my_courses = [course['name'] for course in collection.find_one({"email": os.environ['MLEARNING_USERNAME']})["courses"]["valid"]]

# Get a dictionary of lists of valid courses for each classmate
classmate_courses = {document["name"]:[course["name"]for course in document["courses"]["valid"]] for document in collection.find({"email": {"$ne": os.environ['MLEARNING_USERNAME']}}, {"courses.valid.name": 1, "name": 1, "_id": 0})}

# Find the number of classes I took with each classmate and print the top 5
class_counts = {name: len(set(my_courses).intersection(set(courses))) for name, courses in classmate_courses.items()}
sorted_class_counts = sorted(class_counts.items(), key=lambda item: item[1], reverse=True)
max_class_count = sorted_class_counts[0][1]
print(f"The maximum number of classes I took with a single person is: {max_class_count}")
top_classmates = [name for name, count in sorted_class_counts if count == max_class_count]
print("Here are the top 5 people who have taken the most classes with me:")
for i, name in enumerate(top_classmates, start=1):
    print(f"{i}. {name.split(' ')[-1]}")