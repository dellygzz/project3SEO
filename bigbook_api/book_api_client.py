import requests

API_KEY = '9ef98e92382845d0bbfb17487c53d5f7'
BASE_URL = 'https://api.bigbookapi.com/search-books'

def search_books(query, number=5):
    """
    Search books using the Big Book API based on a query string.
    Args:
        query (str): What you're looking for (e.g., "books about wizards")
        number (int): Number of books to return
    Returns:
        list of dicts: Book titles with author names and rating
    """
    params = {
        "query": query,
        "number": number,
        "api-key": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        if "application/json" in response.headers.get("Content-Type", ""):
            data = response.json()
            results = []

            for book_group in data.get("books", []):
                if book_group:
                    book = book_group[0]
                    results.append({
                        "title": book.get("title"),
                        "author": book.get("authors", [{}])[0].get("name", "Unknown"),
                        "rating": book.get("rating", {}).get("average", "N/A"),
                        "cover": book.get("image")
                    })
            return results
        else:
            print("Unexpected response format:", response.text[:300])
            return []

    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return []
