from book_api_client import search_books

if __name__ == "__main__":
    query = "books about wizards"
    recommendations = search_books(query)

    print("Recommended Books:")
    for book in recommendations:
        print(f"- {book['title']} by {book['author']} (Rating: {book['rating']})")
