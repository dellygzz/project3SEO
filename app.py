from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import (init_database, create_user, create_user_and_book, get_user_books, remove_books_from_user, get_user_by_identifier)
import os
from dotenv import load_dotenv
from google_books import search_book
from notion import create_database, add_book_to_reading_list


load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"


def setup_db():
    init_database()


# ======================== AUTH ROUTES =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        # one or more fields not filled out
        if not username or not password or not email:
            flash("Fill out all fields", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template("register.html")

        if "@" not in email:
            flash("Please enter a valid email", "error")
            return render_template("register.html")

        result = create_user(username, password, email)
        # result will return "username or email already exists"
        if isinstance(result, str):
            flash(result, "Error")
        else:
            flash("Account was created succesfully, go ahead and log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["identifier"].strip()
        password = request.form["password"].strip()

        user = get_user_by_identifier(identifier)
        if user and user.password == password:
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username/email/password", "error")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))
#=================================================================

# ============== BOOK ROUTES ======================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    books = get_user_books(session["user_id"])
    return render_template("dashboard.html", books=books)


@app.route("/search")
def search():
    query = request.args.get("q")
    if query:
        results = search_book(query)
    else:
        results = []
    return render_template('results.html', query=query, results=results)

@app.route('/add_book', methods = ['POST'])
def add_book():
    google_book_id = request.form.get('google_book_id')
    title = request.form.get('title')
    author = request.form.get('author')
    description = request.form.get('description', '')
    
    if not google_book_id or not title or not author:
        flash('Missing book information', 'error')
        return redirect(request.referrer)
    
    success = create_user_and_book(
        session['user_id'], 
        google_book_id, 
        title, 
        author, 
        description
    )
    
    if success:
        flash('Book added to your reading list!', 'success')
    else:
        flash('Book is already in your reading list or failed to add', 'error')
    
    return redirect(request.referrer)

@app.route("/remove_book")
def remove_book():
    google_book_id = request.form.get('google_book_id')
    
    if not google_book_id:
        flash('Invalid book ID', 'error')
        return redirect(request.referrer)
    
    result = remove_books_from_user(session['user_id'], google_book_id)
    
    if result is True:
        flash('Book removed from your reading list', 'success')
    else:
        flash(f'Failed to remove book: {result}', 'error')
    
    return redirect(request.referrer)


# ============== NOTION ROUTES ======================================

@app.route("/create_notion")
def create_notion():
    url = request.args.get("url")
    response = create_database(url, "Reading List")
    if response:
        flash("Notion database created successfully!", "success")
    else:
        flash("Error in creating Notion database", "error")

    return redirect(url_for("dashboard"))

@app.route("/add_notion")
def add_notion():
    url = request.args.get("url")
    books = get_user_books(session["user_id"])
    for book in books:
        response = add_book_to_reading_list(url, book["title"], book["author"])
        if not response:
            break
    if not response:
        flash("Error in adding to Notion database", "error")
    else:
        flash("Added to Notion database successfully!", "success")
    
    return redirect(url_for("dashboard"))
    

# =====================================================================


if __name__ == "__main__":
    setup_db()
    app.run(debug=True)
