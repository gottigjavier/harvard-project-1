import csv
import time

from mymodels import *
from myconfig import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        book = Books(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Added to Table of Books isbn: {isbn}, Title: {title}, Author: {author}, Year: {year}.")
    start_time = time.time()
    db.session.commit()
    stop_time = time.time()
    delay= stop_time - start_time
    print("Complete in:", delay, " seconds." ) # Around 17 minutes for Heroku

if __name__ == "__main__":
    with app.app_context():
        main()
