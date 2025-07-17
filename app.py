from flask import Flask, render_template, request, redirect, url_for, flash, session
<<<<<<< HEAD
from database import (init_database, Create_User, Create_Book, Create_User_And_Book, Get_User_Books, Remove_Books_From_User, Session, User, or_, Get_User_By_Identifier)
=======
import os
import sqlite3
from dotenv import load_dotenv
from database import init_database, create_user
from google_books import search_book


load_dotenv()
>>>>>>> 6d992f13184c32b1852930f7a4ede58f106755ea

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for sessions & flash

# Ensure DB is created
def setup_db():
    init_database()

#======================== AUTH ROUTES =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        #one or more fields not filled out
        if not username or not password or not email:
            flash("Fill out all fields", "error")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template('register.html')
        
        if '@' not in email:
            flash("Please enter a valid email", 'error')
            return render_template('register.html')

        result = Create_User(username, password, email)
        #result will return "username or email already exists"
        if isinstance(result, str):
            flash(result, "Error")
        else:
            flash("Account was created succesfully, go ahead and log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        password = request.form['password'].strip()

        user = Get_User_By_Identifier(identifier)
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            flash("login succesful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username/email/password", "error")

    return render_template('login.html')

<<<<<<< HEAD
=======

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])


@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        results = search_book(query)
    else:
        results = []
    return render_template('results.html', query=query, results=results)


>>>>>>> 6d992f13184c32b1852930f7a4ede58f106755ea
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))
#=================================================================

#============== BOOK ROUTES ======================================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/search_books')
def search_books():
    pass

@app.route('/add_book')
def add_book():
    pass
@app.route('/remove_book')
def remove_book():
    pass

#=====================================================================


if __name__ == '__main__':
    setup_db()
    app.run(debug=True)
