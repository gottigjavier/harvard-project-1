from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    score = db.Column(db.Float, nullable=True)
    reviews = db.relationship("Reviews", backref= "book", lazy=True)
    
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    registered_on = db.Column(db.DateTime, nullable=True)    


class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    single_score = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=True)
    username_user = db.Column(db.String, db.ForeignKey("users.username"), nullable=False)
    id_book = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    review_on = db.Column(db.DateTime, nullable=True)
