from flask_app import app
from flask import render_template,redirect,request,session,flash
from datetime import datetime, timedelta
from flask_app.models.show import Show
from flask_app.models.user import User

@app.route("/shows/add")
def add_show():
    if 'user_id' not in session.keys():
        return redirect('/login')
    
    data = {
        "id": session['user_id']
    }
    
    user = User.get_one(data)
    
    return render_template("add_show.html", info=user)

@app.route("/shows/add_process",methods=['POST'])
def save_show():
    if 'user_id' not in session.keys():
        return redirect('/login')
    
    if not Show.validate_show(request.form):
        return redirect('/shows/add')
    
    data = {
        "title": request.form["title"],
        "network": request.form["network"],
        "release_date": request.form["release_date"],
        "description": request.form["description"],
        "user_id": session["user_id"],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    Show.save(data)
    return redirect('/dashboard')

@app.route("/shows/view/<idIn>")
def view_show(idIn):
    if 'user_id' not in session.keys():
        return redirect('/login')
    
    data1={
        'id': idIn
    }
    show = Show.get_one(data1)
    likes = Show.get_liked_by(data1)
    print(likes.liked_by)
    
    data2 = {
        "id": idIn,
        "poster_id": show.poster_id
    }
    show_w_poster = Show.get_one_with_user(data2)
    
    data3 = {
        "id": session['user_id']
    }
    user = User.get_one(data3)
    
    
    return render_template("view_show.html", show=show_w_poster, info=user, likes=likes)

@app.route("/shows/edit/<idIn>")
def edit_show(idIn):
    if 'user_id' not in session.keys():
        return redirect('/login')
    
    data1={
        'id': idIn
    }
    
    show = Show.get_one(data1)
    if show.poster_id != session['user_id']:
        return redirect('/dashboard')
    
    data2 = {
        "id": session['user_id']
    }
    
    show = Show.get_one(data1)
    user = User.get_one(data2)
    
    return render_template("edit_show.html", show=show, info=user)

@app.route("/shows/edit_process",methods=['POST'])
def edit_process():
    if 'user_id' not in session.keys():
        return redirect('/login')
    
    if not Show.validate_show(request.form):
        return redirect(f'/shows/edit/{request.form["id"]}')
    
    data = {
        "id": request.form["id"],
        "title": request.form["title"],
        "network": request.form["network"],
        "release_date": request.form["release_date"],
        "description": request.form["description"],
        "user_id": session["user_id"],
        "updated_at": datetime.now()
    }
    
    Show.edit(data)
    
    return redirect ('/dashboard')

@app.route("/shows/delete/<idIn>")
def delete_show(idIn):
    data = {
        "id":idIn
    }
    
    show = Show.get_one(data)
    if show.poster_id != session['user_id']:
        return redirect('/dashboard')
    
    Show.delete(data)
    
    return redirect('/dashboard')