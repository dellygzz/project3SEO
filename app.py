from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import sqlite3
from dotenv import load_dotenv
from database import init_database, create_user
from google_books import search_book


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]  # Needed for sessions & flash


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        new_user = create_user(username, password, email)
        if not new_user:
            flash("An account with that username or email already exists.", "error")
        else:
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND email = ? AND password = ?", (username, email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")

    return render_template('login.html')


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


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_database()
    app.run(debug=True)
