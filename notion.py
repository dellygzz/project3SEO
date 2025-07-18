import os
from dotenv import load_dotenv

from notion_client import Client
from notion_client.helpers import get_id

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")

while NOTION_TOKEN == "":
    print("NOTION_TOKEN not found.")
    NOTION_TOKEN = input("Enter your integration token: ").strip()

# Initialize the client
notion = Client(auth=NOTION_TOKEN)


def create_database(page_url: str, db_name: str) -> dict:
    parent_id = get_id(page_url)
    print(f"\n\nCreate database '{db_name}' in page {parent_id}...")
    properties = {
        "Title": {"title": {}},
        "Author": {"rich_text": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "To Read", "color": "gray"},
                    {"name": "Reading", "color": "blue"},
                    {"name": "Completed", "color": "green"},
                ]
            }
        },
        "Rating": {
            "select": {
                "options": [
                    {"name": "⭐️"},
                    {"name": "⭐️⭐️"},
                    {"name": "⭐️⭐️⭐️"},
                    {"name": "⭐️⭐️⭐️⭐️"},
                    {"name": "⭐️⭐️⭐️⭐️⭐️"},
                ]
            }
        },
    }

    title = [{"type": "text", "text": {"content": db_name}}]
    icon = {"type": "emoji", "emoji": "📚"}
    parent = {"type": "page_id", "page_id": parent_id}

    return notion.databases.create(
        parent=parent, title=title, properties=properties, icon=icon
    )


def add_book_to_reading_list(database_url, title, author, status="To Read"):
    database_id = get_id(database_url)
    properties = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Author": {"rich_text": [{"text": {"content": author}}]},
        "Status": {"select": {"name": status}},
    }

    return notion.pages.create(
        parent={"database_id": database_id}, properties=properties
    )


if __name__ == "__main__":
    database_url = input("Database URL: ")
    title = input("Title: ")
    author = input("Author: ")
    new_row = add_book_to_reading_list(database_url, title, author)
    print(new_row)
