import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.environ["GOOGLE_API_KEY"]

def search_book(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"

    response = requests.get(url)
    data = response.json()
    print(data)

    for item in data.get("items", []):
        volume_info = item["volumeInfo"]
        title = volume_info.get("title")
        authors = volume_info.get("authors", [])
        print(f"{title} by {', '.join(authors)}")

if __name__ == "__main__":
    query = input("Enter book name: ")
    search_book(query)
    