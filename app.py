import os
import base64
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import (
    init_database,
    create_user,
    create_user_and_book,
    get_user_books,
    remove_books_from_user,
    get_user_by_identifier,
)
from google_books import search_book
from notion import (
    create_database,
    add_book_to_reading_list,
    clear_database,
    get_user_pages,
    get_user_databases,
)



load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

CLIENT_ID = os.getenv("NOTION_CLIENT_ID")
CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET")
REDIRECT_URI = os.getenv("NOTION_REDIRECT_URI")

NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"

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
            flash(result, "error")
        else:
            flash("Account was created successfully, go ahead and log in.", "success")
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


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("access_token", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# =================================================================


# ============== BOOK ROUTES ======================================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    books = get_user_books(session["user_id"])

    amazon_search_url = None
    search_query = None

    if request.method == "POST":
        search_query = request.form.get("search_book_title", "").strip()
        if search_query:
            amazon_search_url = get_amazon_search_url(search_query)

    return render_template(
        "dashboard.html",
        books=books,
        amazon_search_url=amazon_search_url,
        search_query=search_query,
    )

import urllib.parse

def get_amazon_search_url(book_title: str) -> str:
    query = urllib.parse.quote("book " + book_title)
    return f"https://www.amazon.com/s?k={query}"



@app.route("/search")
def search():
    query = request.args.get("q")
    if query:
        results = search_book(query)
    else:
        results = []
    return render_template("results.html", query=query, results=results)


@app.route("/add_book", methods=["POST"])
def add_book():
    google_book_id = request.form.get("google_book_id")
    title = request.form.get("title")
    author = request.form.get("author")
    description = request.form.get("description", "")

    if not google_book_id or not title or not author:
        flash("Missing book information", "error")
        return redirect(request.referrer)

    success = create_user_and_book(
        session["user_id"], google_book_id, title, author, description
    )

    if success:
        flash("Book added to your reading list!", "success")
    else:
        flash("Book is already in your reading list or failed to add", "error")

    return redirect(request.referrer)


@app.route("/remove_book", methods=["POST"])
def remove_book():
    google_book_id = request.form.get("google_book_id")

    if not google_book_id:
        flash("Invalid book ID", "error")
        return redirect(request.referrer)

    result = remove_books_from_user(session["user_id"], google_book_id)

    if result is True:
        flash("Book removed from your reading list", "success")
    else:
        flash(f"Failed to remove book: {result}", "error")

    return redirect(request.referrer)

@app.route("/find_libraries", methods=["POST"])
def find_libraries():
    title = request.form.get("title")
    zip_code = request.form.get("zip")  # get ZIP from form input

    if not title or not zip_code:
        flash("Please provide both book title and ZIP code.", "error")
        return redirect(request.referrer or url_for("dashboard"))

    books = search_book(title)
    if not books:
        flash("No books found with that title.", "error")
        return redirect(request.referrer or url_for("dashboard"))

    book = next((b for b in books if b.get("isbn")), None)
    if not book:
        flash("No books with a valid ISBN found.", "error")
        return redirect(request.referrer or url_for("dashboard"))

    isbn = book["isbn"]
    worldcat_url = f"https://www.worldcat.org/isbn/{isbn}?loc={zip_code}"
    return redirect(worldcat_url)



# ====================================================================


# ============== NOTION ROUTES ======================================
@app.route("/notion_login")
def notion_login():
    auth_url = os.getenv("NOTION_AUTH_URL")
    return redirect(auth_url)


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    token_response = requests.post(NOTION_TOKEN_URL, headers=headers, json=data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        return f"Error getting token: {token_json}", 400

    session["access_token"] = token_json["access_token"]
    return redirect(url_for("dashboard"))


@app.route("/create_notion", methods=["POST"])
def create_notion():
    page_id = request.form.get("page_id")
    if not page_id:
        flash("Please select a valid Notion page.", "error")
        return redirect(url_for("dashboard"))
    token = session.get("access_token")
    response = create_database(token, page_id, "Reading List")
    if response:
        flash("Notion database created successfully!", "success")
    else:
        flash("Error in creating Notion database", "error")

    return redirect(url_for("dashboard"))




@app.route("/add_notion", methods=["POST"])
def add_notion():
    database_id = request.form.get("database_id")
    if not database_id:
        flash("Please select a valid Notion database.", "error")
        return redirect(url_for("dashboard"))
    token = session.get("access_token")
    books = get_user_books(session["user_id"])

    if not clear_database(token, database_id):
        flash("Invalid URL", "error")
        return redirect(url_for("dashboard"))

    for book in books:
        response = add_book_to_reading_list(
            token, database_id, book["title"], book["author"], book["description"]
        )
        if not response:
            break

    if not response:
        flash("Error in adding to Notion database", "error")
    else:
        flash("Added to Notion database successfully!", "success")

    return redirect(url_for("dashboard"))


# =====================================================================

if __name__ == "__main__":
    app.run()
