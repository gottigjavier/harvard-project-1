# CS50's Web Programming with Python and JavaScript.

# Project 1

Make sure you have installed the modules listed in the "requirements.txt".

This project allows a logged user to search for a book from a list of 5000 books.
(Optionally, the entire list can be expanded.)

The search can be done by categories: ISBN, title, author or year.

The result will return a list of books that matches all or part of what has been entered in the search box, without distinguishing between upper and lower case.

If there are no matches, the app will report that.

If the book is in the list, a simple click on it will take the user to the page with the data of this book.

These data include, in addition to the categories mentioned above, the average score, the number of times it was rated and the comments given by users of this API.

Data recorded on the goodreads.com site, such as ID, average score, and the number of times it was rated, will also be displayed.

Can be do only review of the book and one rating per user.

If no score is checked, the value 0 is given.

After grading, the form will no longer be available to that user and that particular book.

The "Api" section details how users can query book details and book reviews programmatically to get data in JSON format.

Raw SQL commands are used for database queries, as requested by Project-1 requirements.
Since it is not familiar with SQLAlchemy ORM, also it built a version based on it as a personal challenge.
From that version it was decided to use the loginuser module, and thus have better control of the fields of the login and signup forms, although their full potential is not used.

Folder and file content:

The myconfig.py file contains the path to interact with the Heroku site database as well as the secret key necessary for password management.

The "dbbuilder" folder contains the files repeated "myconfig.py" and "mymodels.py" for export and use independent.

The "create.py" file creates the tables "books", "users" and "reviews" in the database assigned in "/dbbuider/myconfig.py".

The "import.py" file imports the data from "books.csv" into the "books" table in the database.

The "mypackages" folder contains the file "mymodels.py", which is the module that shapes the tables and allows interaction via SQLAlchemy.

The "loginuser.py" file, also included in the "mypackages" folder, allows user management.

The "application.py" file handles all the logic between the parts of the application, allowing interaction between the client, server and Goodreads API.

Sceencast: https://www.youtube.com/watch?v=j8TCWAj2cqo