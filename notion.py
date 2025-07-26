from notion_client import Client
from notion_client.helpers import get_id


def create_database(token, parent_id: str, db_name: str) -> dict:
    notion = Client(auth=token)
    
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


def clear_database(token, database_id):
    notion = Client(auth=token)
    
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


def get_user_pages(access_token):
    notion = Client(auth=access_token)
    response = notion.search(filter={"property": "object", "value": "page"})
    
    pages = []
    for result in response["results"]:
        title = "Untitled"
        if "properties" in result and "title" in result["properties"]:
            title_property = result["properties"]["title"]["title"]
            if title_property:
                title = title_property[0]["plain_text"]
        pages.append({"id": result["id"], "title": title})
    return pages


def get_user_databases(access_token):
    notion = Client(auth=access_token)
    response = notion.search(filter={"property": "object", "value": "database"})
    
    databases = []
    for result in response["results"]:
        title = "Untitled"
        # Databases have a "title" property at the root
        if "title" in result and result["title"]:
            title = "".join([t["plain_text"] for t in result["title"]])
        databases.append({"id": result["id"], "title": title})
    return databases


def add_book_to_reading_list(token, database_id, title, author, description, status="To Read"):
    notion = Client(auth=token)
    
    properties = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Author": {"rich_text": [{"text": {"content": author}}]},
        "Description": {"rich_text": [{"text": {"content": description}}]},
        "Status": {"select": {"name": status}},
    }

    return notion.pages.create(
        parent={"database_id": database_id}, properties=properties
    )
