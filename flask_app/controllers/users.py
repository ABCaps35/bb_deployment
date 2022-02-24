from flask_app import app
from flask import render_template,redirect,request,session,flash
from datetime import datetime, timedelta
from flask_app.models.user import User
from flask_app.models.show import Show

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route("/")
def load_site():
    return redirect("/login")

@app.route("/login")
def load_login():
    return render_template("login.html")

@app.route("/process_login",methods=["POST"])
def process_login():
    if not User.validate_login(request.form):
        return redirect('/login')
    data = {
        "email": request.form['email']
    }
    user_in_db = User.get_by_email(data)
    
    if not user_in_db:
        flash("There is no user associated with that email address")
        return redirect('/')
    if not bcrypt.check_password_hash(user_in_db.password,request.form['password']):
        flash("Incorrect Password")
        return redirect('/')
    
    session['user_id'] = user_in_db.id
    return redirect("/dashboard")

@app.route("/register")
def load_registration():
    return render_template("register.html")

@app.route("/process_register",methods=["POST"])
def process_registration():
    if not User.validate_registration(request.form):
        return redirect('/register')
    
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": pw_hash,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    session['user_id'] = User.save(data)
    return redirect("/dashboard")

@app.route("/dashboard")
def display_user():
    if 'user_id' not in session.keys():
        return redirect('/login')
    data = {
        "id": session['user_id']
    }
    
    user = User.get_one(data)
    shows = Show.get_all()
    user_shows = User.get_likes(data)
    
    for show in shows:
        for item in user_shows.likes:
            if show.id==item.id:
                show.was_liked = True
                
    
    return render_template("dashboard.html", info=user, liked_shows=user_shows.likes, all_shows=shows)

@app.route("/shows/like/<idIn>")
def like_show(idIn):
    data={
        "user_id": session['user_id'],
        "show_id": idIn,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    User.add_liked_show(data)
    return redirect('/dashboard')

@app.route("/shows/unlike/<idIn>")
def unlike_show(idIn):
    data={
        "user_id": session['user_id'],
        "show_id": idIn,
    }
    
    User.remove_liked_show(data)
    return redirect('/dashboard')

@app.route('/logout')
def sign_out():
    session.clear()
    return redirect("/dashboard")