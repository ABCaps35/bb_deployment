from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from datetime import datetime
from flask_app.models import user

class Show:
    def __init__(self,data):
        self.id = data['id']
        self.title = data['title']
        self.network = data['network']
        self.release_date = data['release_date']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.poster_id = data['poster_id']
        self.liked_by = []
        
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM shows;"

        results = connectToMySQL('shows_bb_schema').query_db(query)

        shows = []

        for show in results:
            shows.append( cls(show) )
        return shows
    
    @classmethod
    def get_all_by_user(cls, data):
        query = "SELECT * FROM shows LEFT JOIN users ON shows.poster_id = users.id"

        results = connectToMySQL('shows_bb_schema').query_db(query,data)
        
        if len(results)==0:
            return False
        
        shows = []

        for show in results:
            shows.append( cls(show) )
        return shows
    
    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM shows WHERE id=%(id)s;"

        result = connectToMySQL('shows_bb_schema').query_db(query,data)

        show = cls(result[0])
        return show
    
    @classmethod
    def get_one_with_user(cls, data):
        query = "SELECT * FROM shows LEFT JOIN users ON shows.poster_id = users.id WHERE shows.poster_id=%(poster_id)s AND shows.id=%(id)s"

        results = connectToMySQL('shows_bb_schema').query_db(query,data)
        
        if len(results)==0:
            return False
        
        show = cls(results[0])
        
        poster_name = {
            "first_name": results[0]['first_name'],
            "last_name": results[0]['last_name'],
        }
        
        show.poster_info = poster_name
        return show
    
    @classmethod
    def get_for_user(cls, data):
        query = "SELECT * FROM shows LEFT JOIN users ON shows.poster_id = users.id WHERE shows.poster_id=%(id)s"

        results = connectToMySQL('shows_bb_schema').query_db(query,data)
        
        if len(results)==0:
            return False
        
        shows = []

        for show in results:
            shows.append( cls(show) )
        return shows
    
    @classmethod
    def get_others(cls, data):
        query = "SELECT * FROM shows WHERE id!=%(id)s;"

        results = connectToMySQL('shows_bb_schema').query_db(query,data)

        if len(results)==0:
            return False
        
        shows = []

        for show in results:
            shows.append( cls(show) )
        return shows
    
    @classmethod
    def edit(cls, data ):
        query = "UPDATE shows SET title=%(title)s, network=%(network)s, release_date=%(release_date)s, description=%(description)s, poster_id=%(poster_id)s, updated_at=NOW() WHERE id=%(id)s"
        
        result = connectToMySQL('shows_bb_schema').query_db(query,data)
        return result
    
    @classmethod
    def save(cls, data ):
        query = "INSERT INTO shows ( title, network, release_date, description, created_at, updated_at, poster_id ) VALUES ( %(title)s , %(network)s , %(release_date)s , %(description)s ,  NOW() , NOW() , %(poster_id)s );"

        return connectToMySQL('shows_bb_schema').query_db( query, data )
    
    @classmethod
    def delete(cls, data ):
        query = "DELETE FROM shows WHERE id=%(id)s"
        
        result = connectToMySQL('shows_bb_schema').query_db(query,data)
        return result
    
    @staticmethod
    def validate_show(response):
        isValid = True
        
        for field in response:
            if response[field]=='':
                flash("Must fill out all fields")
                isValid=False
                break
        
        if len(response['title'])<3 or len(response['title'])>255:
            flash("Show title must be between 3 and 255 characters long")
            isValid = False
        
        
        if len(response['network'])<3 or len(response['network'])>255:
            flash("Network name must be between 3 and 255 characters long")
            isValid = False
        
        try:
            datetime.strptime(response["release_date"],'%Y-%m-%d')
        except (TypeError, ValueError):
            flash("Please input a show release date in the format: mm/dd/yyyy")
            isValid = False
       
        if len(response['description'])<3 or len(response['description'])>255:
            flash("Show description must be between 3 and 255 characters long")
            isValid = False
            
        return isValid
    
    @classmethod
    def get_liked_by(cls, data ):
        query = "SELECT * FROM shows LEFT JOIN likes ON likes.show_id=shows.id LEFT JOIN users ON likes.user_id=users.id WHERE shows.id=%(id)s"
        results = connectToMySQL('shows_bb_schema').query_db(query,data)
        
        print(results[0])
        
        show = cls(results[0])
        for row in results:
            if row['users.id'] != None:
                user_data = {
                    "id": row['users.id'],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "password": row["password"],
                    "created_at": row["created_at"],
                    "updated_at": row['updated_at']
                }
                show.liked_by.append( user.User(user_data) )
        return show
    
    @classmethod
    def add_like_from_user(cls,data):
        query = "INSERT INTO likes (user_id, show_id, created_at, updated_at) VALUES (%(user_id)s, %(show_id)s, NOW(), NOW())"

        return connectToMySQL('shows_bb_schema').query_db(query,data)
    
    @classmethod
    def remove_like_from_user(cls,data):
        query = "DELETE FROM likes WHERE user_id=%(user_id)s AND show_id=%(show_id)s"
        
        return connectToMySQL('shows_bb_schema').query_db(query,data)