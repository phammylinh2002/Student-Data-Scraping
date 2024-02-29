# Student Data Scraping

This project involves extracting information from students who have attended the same class with me on MLearning, a learning management platform utilized by my university. In addition to gathering data related to the students' accounts, the project aims to retrieve details about the courses they have taken.

## How did I come up with this project?

I've been considering taking on this project for some time now. Recently, a friend showed me how to navigate to the page displaying our class's student list. This helped me reach out to people I know to form a group with them (you understand how crucial teammates are for group projects at university). Upon exploring further, I discovered that I could also view other classmates' profiles, which typically included their student email, name, student ID (although sometimes it wasn't visible), and their enrolled classes. Since then, I've occasionally checked out what classes my friends are taking. I don't believe it's overly intrusive, especially considering that the administrators permit students like me to view other classmates' profiles. Thus, I don't see any harm in it.

## Why did I decide to do this project?

To address my questions, such as: How many people have I met throughout all these years and classes? How many of them have I befriended? Who is the person I've taken the same class with the most times? etc. Additionally, I want to hone my web scraping skills by practicing on a dynamic website, something I haven't done before. It's meant to be a small project to satisfy my curiosity, but I must admit, I've ended up spending a lot of time on it and learned some cool things I didn't expect.

## Can you access the data I scraped?

Just to be clear: the data I've scraped is for me to see. I won't be sharing it with anyone else. While I'm open to discussing what I've found, the raw data stays confidential.

## Can my fellow HSU students use my project to learn about your classmates as well?

Of course yes. It's crucial to understand that if fellow HSU students use my project to learn about classmates but in case that the data you obtained through my code is leaked, whether intentionally or unintentionally, I cannot accept responsibility for such occurrences.

## How to use it?

1. Clone this project (of course 😀)
2. Set up a database on MongoDB (because I use MongoDB). You'll need 1 collection to store the data. You may need to read these:
   * [Get Started with Atlas](https://www.mongodb.com/docs/atlas/getting-started/)
   * [Create, View, and Drop Databases](https://www.mongodb.com/docs/atlas/atlas-ui/databases/)
   * [Create, View, Drop, and Shard Collections](https://www.mongodb.com/docs/atlas/atlas-ui/collections/#create--view--drop--and-shard-collections)
3. Install the libraries by executing this command:
   `pip install -r requirements.txt`
4. Change the name of the `.env.example` file:
   `mv .env.example .env`
5. Fill in the values in the `.env` file. Remember that:
   **MLEARNING_USERNAME**: Your student email address
   **MLEARNING_PASSWORD**: Your password
   **MONGODB_CONNECTION_STRING**: The connection string to your cluster on MongoDB
   **MONGODB_DB_NAME**: The name of the database you want to store your data in
   **MONGODB_COLLECTION_NAME**: The name of the collection in the database
6. Run the `main.py` and you are done.

## My findings after completing the project

**1. Understanding the data is crucial**
<br>
I noticed that in the early phase, when I first entered my university and perhaps when teachers were just starting to use this platform, there was no standardized convention for class names. This inconsistency made it challenging for me to check and process the data. Additionally, some classes were not genuine courses; rather, they were created on MLearning solely for examinations. These classes, in my view, were not legitimate. Later on, class names began to follow a convention, but some classes still did not adhere to it, and new ones were created that also deviated from the convention. As a result, I labeled those that did not follow the convention as "invalid." The data of my classmates that I scraped is based on classes I deemed valid. However, for a comprehensive overview of all classes, I stored both invalid and valid classes. By considering data validation, I avoided including redundant data, particularly the information of classmates whom I never actually attended the same "real" class with.

**2. Performance is key**
<br>
The more I delve into this project, the more I realize that while I can accomplish most tasks I set my mind to, achieving optimal performance remains a constant challenge. Initially, the idea of scraping data from MLearning intrigued me. Once I immersed myself in the project, I found the initial stages relatively straightforward. However, as I progressed, I encountered the true difficulty: performance issues. When I ran the program to scrape all my classmates' data, it started off quickly but slowed down significantly afterward. It became so sluggish that I couldn't even wait for it to complete. I addressed this by implementing concurrency, which improved runtime, but it still took over an hour to scrape data from about 600 classmates in the last run. Realizing that further optimization would lead to an endless cycle of ideas and delays, I decided to move on to another project. Although I've learned a valuable lesson about performance, I regret having to abandon this project. Nevertheless, the insights gained from this experience are invaluable, and it's a lesson I'll always remember.

**3. I should use Google Chrome for web-scraping projects**
<br>
I initially chose Safari as the driver for my web scraping because it was my preferred browser. However, I soon encountered a persistent issue – I couldn't find a specific element. After investing a significant amount of time trying to figure out why the elements weren't being found despite using the correct path, I discovered the issue was with the Safari driver. After numerous attempts to troubleshoot on Safari, I decided to switch to Google Chrome. It wasn't clear whether the problem originated from Safari itself or if it was related to the Python library I was using (selenium). I set aside the question and proceeded to use Google Chrome as the driver for my web scraping project, and it has been my default browser ever since. And I promised myself to use Google Chrome for any other web-scraping projects in the future.

## So what are the anwsers to my questions?

Before going to the answer, here is how a classmate's data looks like in the database (I use MongoDB):

``` 
{'_id': ObjectId('65dd959c2b014f5b4032c965'),
 'courses': {'invalid': [{'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=8344',
                          'name': 'Giáo Dục Quốc Phòng - Học Kỳ Hè - 2020 '
                                  '-2021 - Nhóm 02 - (Từ Đại đội 13 (lớp '
                                  '1300)  đến Đại đội 24 (lớp 2400))'},
                         {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=3612',
                          'name': 'HƯỚNG DẪN SỬ DỤNG TURNITIN DÀNH CHO SINH '
                                  'VIÊN'}],
             'valid': [{'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18512',
                        'name': 'Business System Analysis_1314_2331'},
                       {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18019',
                        'name': 'Corporate Finance_1157_2234'},
                       {'link': 'https://mlearning.hoasen.edu.vn/course/view.php?id=18507',
                        'name': 'Đồ án Chuyên ngành HTTT_2056_2331'}]},
 'email': 'LINH.*******@SINHVIEN.HOASEN.EDU.VN',
 'name': 'Phạm Mỹ Linh',
 'profile_link': 'https://mlearning.hoasen.edu.vn/user/profile.php?id=99999'}
```

> Some values were truncated and edited

* **How many people have I met throughout all these years and classes?**

After a long time of scraping, in my valid **22 courses**, I have **632 unique classmates**. I am amazed at how many people passed by my life and little of them stay.
<br>

* **Which classes have the most of my classmates enrolled?**

Here are the top 5 classes which have the most of my classmates enrolled:
![Top 5 Classes Which Have The Most of My Classmates Enrolled](figures/Top%205%20Classes%20Which%20Have%20The%20Most%20of%20My%20Classmates%20Enrolled.png)

Here is the English names of the classes:

1. Fundamentals of Accounting
2. Critical Thinking
3. Introduction to International Business
4. Macro-economics
5. Database Management Systems

The interesting thing is that I attended all of them. It's worth noting that the majority of my classmates are majoring in business and technology fields.

* **Which classes have the most of my classmates enrolled?**

However, the bottom 5 classes are completely strange to me. Here are the bottom 5 classes which have the least of my classmates enrolled:
![Top 5 Classes Which Have The Most of My Classmates Enrolled](figures/Bottom%205%20Classes%20Which%20Have%20The%20Least%20of%20My%20Classmates%20Enrolled.png)

Here is the complete list of the English names of the classes:

1. Project Management
2. Behaviral Finance
3. Korean Level 2
4. English Grammar in Use
5. Music Perception

I only have one classmate in each of those bottom classes, which indicates that I didn't meet many people from other majors besides business and technology. That makes sense because my major is closely related to business and technology.

* **Who has taken the most classes with me?**

Quite a few, actually. I discovered that the highest number of classes I've attended with a single individual is 7, and there are 5 people who have reached that same number.

Here is the list of them, derived from [analysis.py](/src/analysis.py):

```
The maximum number of classes you took with a single person is: 7
Here are the top 5 people who have taken the most classes with me:
1. Tiến
2. DAT********
3. Thư
4. Duy
5. Vy
```

Of course, the names were truncated, and the second one was manually edited to ensure their identity remains protected.

## What improvements are needed?

**First and foremost:** Performance.
<br>
**Secondly:** Enhancing the data analysis. Perhaps, in the future, I'll revisit this data for more comprehensive analysis.
<br>
**Thirdly:** Refining my coding style 😀 Honestly, it's a bit convoluted. I need to focus on modularizing and effectively reusing code, as well as enhancing its readability.