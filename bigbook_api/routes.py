from flask import Flask, render_template, request
from bigbook_api.book_api_client import search_books as get_recommendations
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def home():
    return render_template('books.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    titles = request.args.get('titles', 'Dune,1984').split(',')
    recommendations = []

    for title in titles:
        books = get_recommendations(title.strip())  # query each title separately
        recommendations.extend(books)

    return render_template('books.html', books=recommendations)

if __name__ == '__main__':
    app.run(debug=True)