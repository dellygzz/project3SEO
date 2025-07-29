from flask import Flask, render_template, request
from bigbook_api.book_api_client import get_recommendations

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('books.html')

@app.route('/recommend', methods=['GET'])
def recommend():
    titles = request.args.get('titles', 'Dune,1984').split(',')
    recommendations = get_recommendations(titles)
    return render_template('books.html', books=recommendations)
if __name__ == '__main__':
    app.run(debug=True)