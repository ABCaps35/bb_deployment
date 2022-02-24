from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from datetime import datetime
from flask_app.models import show

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

class User:
    def __init__(self,data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.likes = []
        
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"

        results = connectToMySQL('shows_bb_schema').query_db(query)

        users = []

        for user in results:
            users.append( cls(user) )
        return users
    
    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM users WHERE id=%(id)s;"

        result = connectToMySQL('shows_bb_schema').query_db(query,data)

        user = cls(result[0])
        return user
    
    @classmethod
    def get_others(cls, data):
        query = "SELECT * FROM users WHERE id!=%(id)s;"

        results = connectToMySQL('shows_bb_schema').query_db(query,data)

        if len(results)==0:
            return False
        
        users = []

        for user in results:
            users.append( cls(user) )
        return users
    
    @classmethod
    def get_by_email(cls, data):
        query = "SELECT * FROM users WHERE email=%(email)s;"

        result = connectToMySQL('shows_bb_schema').query_db(query,data)
        if len(result)<1:
            return False
        user = cls(result[0])
        return user
    
    @classmethod
    def edit(cls, data ):
        query = "UPDATE users SET first_name=%(first_name)s, last_name=%(first_name)s, email=%(email)s, password=%(password)s,  updated_at=NOW() WHERE id=%(id)s"
        
        result = connectToMySQL('shows_bb_schema').query_db(query,data)
        return result
    
    @classmethod
    def save(cls, data ):
        query = "INSERT INTO users ( first_name, last_name, email, password, created_at, updated_at ) VALUES ( %(first_name)s , %(last_name)s , %(email)s , %(password)s ,  NOW() , NOW() );"

        return connectToMySQL('shows_bb_schema').query_db( query, data )
    
    @classmethod
    def delete(cls, data ):
        query = "DELETE FROM users WHERE id=%(id)s"
        
        result = connectToMySQL('shows_bb_schema').query_db(query,data)
        return result
    
    @staticmethod
    def validate_login(response):
        is_valid = True
        
        for field in response:
            if response[field]=='':
                flash("Must fill out all fields")
                is_valid=False
                break
        
        if not EMAIL_REGEX.match(response["email"]):
            flash("Invalid email address")
            is_valid = False
        else:
            data={"email":response['email']}
            user = User.get_by_email(data)
            if not user:
                flash("That email address does not match any users.")
                is_valid = False
            if user != False and not bcrypt.check_password_hash(user.password,response['password']):
                flash("Incorrect password.")
                is_valid = False
        return is_valid
    
    @staticmethod
    def validate_registration(response):
        is_valid = True
        
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm']
        for field in response:
            if response[field]=='':
                flash("Must fill out all fields")
                is_valid=False
                break
            
        if len(response["first_name"]) < 3:
            flash("First name must be at least 3 characters")
            is_valid = False
        if len(response["last_name"]) < 3:
            flash("Last name must be at least 3 characters")
            is_valid = False
        
        data={"email":response['email']}
        if User.get_by_email(data) != False:
            flash("Email already in use. Please enter a new email address")
            is_valid = False
        
        if not EMAIL_REGEX.match(response["email"]):
            flash("Enter a valid email address")
            is_valid = False
        
        if len(response["password"])<8:
            flash("Password must be at least 8 characters long")
            is_valid = False
        if sum(1 for c in response["password"] if c.isupper())==0:
            flash("Password must contain at least 1 capital letter")
            is_valid = False
        if sum(1 for c in response["password"] if c.isnumeric())==0:
            flash("Password must contain at least 1 number")
            is_valid = False
        if response["password"] != response["confirm"]:
            flash("Passwords must match")
            is_valid = False
            
        return is_valid
    
    @classmethod
    def get_likes(cls, data ):
        query = "SELECT * FROM users LEFT JOIN likes ON likes.user_id=users.id LEFT JOIN shows ON likes.show_id=shows.id WHERE users.id=%(id)s"
        results = connectToMySQL('shows_bb_schema').query_db(query,data)
        
        user = cls(results[0])
        
        for row in results:
            if row['show_id'] != None:
                show_data = {
                    "id": row['shows.id'],
                    "title": row["title"],
                    "network": row["network"],
                    "release_date": row["release_date"],
                    "description": row["description"],
                    "poster_id": row["poster_id"],
                    "created_at": row['shows.created_at'],
                    "updated_at": row['shows.updated_at']
                }
                user.likes.append( show.Show(show_data) )
            
        return user
    
    @classmethod
    def add_liked_show(cls,data):
        query = "INSERT INTO likes (user_id, show_id, created_at, updated_at) VALUES (%(user_id)s, %(show_id)s, NOW(), NOW())"
        
        return connectToMySQL('shows_bb_schema').query_db(query,data)
    
    @classmethod
    def remove_liked_show(cls,data):
        query = "DELETE FROM likes WHERE user_id=%(user_id)s AND show_id=%(show_id)s"
        
        return connectToMySQL('shows_bb_schema').query_db(query,data)