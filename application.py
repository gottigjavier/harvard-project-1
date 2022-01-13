import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mypackages.mymodels import *
from flask import Flask, render_template, jsonify, abort, request, redirect, url_for, flash, session, g
from flask_bootstrap import Bootstrap
from mypackages.loginuser import *
from werkzeug.security import generate_password_hash, check_password_hash

from myconfig.myconfig import *


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

bootstrap = Bootstrap(app)


columns=("ISBN", "Title", "Author", "Year")

# Section: index
@app.route("/")
def index():
    return render_template("index.html")


# Section: user management
@app.before_request
def before_request():
    if "username" in session:
        g.user = session["username"]
        g.nameuser=session["nameuser"]
    else:
        g.user = None
        g.nameuser = "Visitor"


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.execute("SELECT * FROM users WHERE username = :username", {"username":form.username.data}).fetchone()
        if user and check_password_hash(user.password, form.password.data):
            session["username"]= user.username
            session["nameuser"]= user.name
            flash('Already you have access!')
            return redirect(url_for('searching'))
        return render_template('login.html', form=form, message='Something went wrong, please try again.')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Users(name=form.name.data, username=form.username.data, email=form.email.data, password=hashed_password, registered_on=datetime.now())
        user_name = db.execute("SELECT *FROM users WHERE username=:username", {"username":form.username.data}).fetchone()
        user_mail = db.execute("SELECT *FROM users WHERE email=:email", {"email":form.email.data}).fetchone()
        if user_name is None and user_mail is None:
            db.add(new_user)
            db.commit()
            flash('Your account has been created.')
            return redirect(url_for('login'))
        else:
            flash('A user already exists with that username or email address.')
            return redirect(url_for('signup'))
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.pop("username", None)
    flash('You have successfully logged out.')
    return redirect(url_for('index'))


# Section: book searching
@app.route('/searching')
def searching():
    if g.user:    
        return render_template('searching.html', columns=columns)
    else:
        flash('Please, login first or create your account.')
        return redirect(url_for('login'))

@app.route("/search", methods=["POST"])
def search():
    if g.user:    
        # Get form information.
        column= request.form.get("columns")
        column_low= column.lower()
        book_data = request.form.get("book_data")
        book_data_low= book_data.lower()    
        books = db.execute("SELECT * FROM books ORDER BY id").fetchall()
        booklist=[] 
        for book in books:
            bookt= getattr(book, column_low)
            bookl= bookt.lower()
            if book_data_low in bookl:
                booklist.append(book)
        if len(booklist)==0:
            return render_template("error.html", message="Book not found."), 404
        return render_template("books.html", books=booklist)
    else:
        flash('Please, login first or create your account.')
        return redirect(url_for('login'))

@app.route("/books")
def books():
    if g.user:
        #List all books.
        books= db.execute("SELECT * FROM books ORDER BY id").fetchall()    
        return render_template("books.html", books=books)
    else:
        flash('Please, login first or create your account.')
        return redirect(url_for('login'))


# Section: book found
@app.route("/book/<int:book_id>")
def book(book_id):
    if g.user:
        book= db.execute("SELECT * FROM books WHERE id= :id", {"id":book_id}).fetchone()
        # Make sure book exists.
        if book is None:
            return render_template("error.html", message="Page not found."), 404
        # Goodreads request
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "gAj6mH7RFp0SaDcMEQA8w", "isbns": book.isbn})
        data= res.json()
        goodreads_rating=data['books'][0]['average_rating']
        goodreads_ratings_count=data['books'][0]['work_ratings_count']
        # Get all reviews of this book.
        reviews= db.execute("SELECT * FROM reviews WHERE id_book=:book_id", {"book_id":book_id}).fetchall()
        new_book_score=0
        book_score=0
        count=0
        for review in reviews:
            book_score=book_score + review.single_score
            count+=1
        if count != 0:
            new_book_score= book_score/count  
            db.execute("UPDATE books SET score=:new_book_score WHERE id=:book_id" , {"book_id":book_id, "new_book_score": new_book_score})  
            db.commit()
        jscore=new_book_score
        past_reviews= db.execute("SELECT * FROM reviews WHERE username_user=:user AND id_book=:book_id", {"user":g.user, "book_id":book_id}).fetchall()
        return render_template("book.html", past_reviews=past_reviews, book=book, jscore=jscore, reviews=reviews, review_count=count, goodreads_rating=goodreads_rating, data=data, goodreads_ratings_count=goodreads_ratings_count)
    else:
        flash('Please, login first or create your account.')
        return redirect(url_for('login'))
    
# Section: book found --> rating
@app.route("/score/<int:id_book>", methods=['POST'])
def score(id_book):
    if g.user:
        if request.method == 'POST':
            stars= request.form.get("stars")
            if stars is None:
                stars=0
            review= request.form.get("text")
            book= db.execute("SELECT * FROM books WHERE id=:id_book", {"id_book": id_book}).fetchone()
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "gAj6mH7RFp0SaDcMEQA8w", "isbns": book.isbn})
            data= res.json()
            goodreads_rating=data['books'][0]['average_rating']
            goodreads_ratings_count=data['books'][0]['work_ratings_count']
            db.execute("INSERT INTO reviews (id_book, single_score, review, username_user, review_on) VALUES (:id_book, :stars, :review, :username_user, :review_on)", {"id_book":id_book, "stars":stars, "review":review, "username_user":g.user, "review_on":datetime.now()})
            db.commit()
            return redirect(url_for('book', book_id=id_book))


# Section: api --> documentation page
@app.route("/apis")
def apis():
    if g.user:
        isbn='074349671X'
        #Request json from api
        book_res = requests.get('http://127.0.0.1:5000/api/' + isbn)
        res= book_res.json()
        return render_template('bookjson.html', book=res)
    else:
        flash('Please, login first or create your account.')
        return redirect(url_for('login'))

# Section: api --> json response
@app.route("/api/<isbn>", methods=['GET'])
def api(isbn):
    # Make sure Book with this ISBN exists.
    book_api= db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
    if book_api is None:
        abort(404)    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "gAj6mH7RFp0SaDcMEQA8w", "isbns": book_api.isbn})
    data= res.json()
    goodreads_rating=data['books'][0]['average_rating']
    goodreads_ratings_count=data['books'][0]['work_ratings_count']
    return jsonify({
            "isbn": book_api.isbn,
            "title": book_api.title,
            "author": book_api.author,
            "year": book_api.year,
            "review_count": goodreads_ratings_count,
            "average_score": goodreads_rating
    })

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404