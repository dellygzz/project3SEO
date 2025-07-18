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
    try:
        parent_id = get_id(page_url)
    except ValueError:
        return {}
    
    print(f"\n\nCreate database '{db_name}' in page {parent_id}...")
    properties = {
        "Title": {"title": {}},
        "Author": {"rich_text": {}},
        "Description": {"rich_text": {}},
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

def clear_database(database_url):
    try:
        database_id = get_id(database_url)
    except ValueError:
        return False
    
    has_more = True
    start_cursor = None

    while has_more:
        # Query pages in the database
        response = notion.databases.query(
            **{
                "database_id": database_id,
                "start_cursor": start_cursor
            }
        )

        pages = response.get("results", [])
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

        # Archive each page
        for page in pages:
            page_id = page["id"]
            notion.pages.update(page_id=page_id, archived=True)
            print(f"Archived page: {page_id}")

    print("All pages archived successfully!")
    return True

def add_book_to_reading_list(database_url, title, author, description, status="To Read"):
    try:
        database_id = get_id(database_url)
    except ValueError:
        return None
    
    properties = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Author": {"rich_text": [{"text": {"content": author}}]},
        "Description": {"rich_text": [{"text": {"content": description}}]},
        "Status": {"select": {"name": status}},
    }

    return notion.pages.create(
        parent={"database_id": database_id}, properties=properties
    )
