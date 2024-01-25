# Student Data Scraping

This is a small project which scrapes the data of the students whom attended the same class with me on MLearning - a learning management platform my university uses. Beside the data about the student accounts, the project also scrapes and stores the courses they attended. The raw data is stored in MongoDB.

## Preparation

* Remove all your courses from the view

* On MongoDB:
  * Create a project
  * Create a cluster in that project
  * Create a database user
  * Add your IP address
    > Remember to check if your IP address changes over time. If it changes, you have to add your new IP address. You can allow access to your cluster from anywhere by adding 0.0.0.0/0 as your IP address but this option is not recommended due to the concern of security.
  * Create a database in that cluster
  * Create a collection in that database
  * Get the connection string to you cluster, remember to change `<password>` to your password of the database user account you created
