import os
import requests


api_key = os.getenv("GOOGLE_BOOKS_API_KEY")

def search_book(query, max_results = 20):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}"

    response = requests.get(url)
    data = response.json()

    books = []

    for item in data.get("items", []):
        volume_info = item.get("volumeInfo", {})
        
        google_book_id = item.get("id")
        title = volume_info.get("title", "Unknown Title")
        
        subtitle = volume_info.get("subtitle")
        if subtitle:
            title = f"{title}: {subtitle}"
        
        authors = volume_info.get("authors", [])
        author = ', '.join(authors) if authors else "Unknown Author"
        
        description = volume_info.get("description")
        if not description:
            search_info = item.get("searchInfo", {})
            description = search_info.get("textSnippet", "No description available")
        
        image_links = volume_info.get("imageLinks", {})
        thumbnail = (image_links.get("thumbnail") or 
                    image_links.get("smallThumbnail") or
                    image_links.get("small") or
                    image_links.get("medium"))
        
        page_count = volume_info.get("pageCount")

        isbn = None
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier["type"] in ["ISBN_13", "ISBN_10"]:
                isbn = identifier["identifier"]
                break
            
                    
        book_data = {
            'google_book_id': google_book_id,
            'title': title,
            'author': author,
            'description': description,
            'thumbnail': thumbnail,
            'page_count': page_count
        }
        
        books.append(book_data)
    

    return books