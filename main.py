import sqlite3
import requests
import random
import os 
from google import genai
from google.genai import types



def setup_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()



def create_account():
    email = input("Choose your email: ").strip()
    password = input("Choose your password: ").strip()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        print("Account created successfully! Logged in!")
        loggedIn()
    except sqlite3.IntegrityError:
        print("An account with that email already exists.")
    finally:
        conn.close()


def login():
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    result = cursor.fetchone()

    conn.close()

    if result:
        loggedIn()

    else:
        print("Invalid email or password. Please run the program again.")


def loggedIn():
    print("Login successful!")
    # Call Dog API

    url = "https://api.thedogapi.com/v1/images/search"
    headers = {
        'x-api-key': 'live_lYvNHFVb44Md9LN8D7kNtzPWtOdZrfhqrLG15u3gdZwgG0JOOb3V7ZNK6srMwZnS'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            dog_image_url = data[0]['url']
            print(f"Click here for your dog image: {dog_image_url}")
        else:
            print("No dog image found.")
    else:
        print("Failed to fetch dog image.")

    color = getmood()
    find_local_dog(color)


#pet finder
CLIENT_ID = "BK09a99NhuhirWVIbgR3Svy20vdWyKEvsMRW237GtqatDkUvPe"
CLIENT_SECRET = "IRpnquDucc1o8dkaJwZzVvQYcixJ6OY9S2O9JtWV"

def get_access_token():
    url = "https://api.petfinder.com/v2/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    token = response.json().get("access_token")
    #print("Access token received:", token)
    return token



def find_local_dog(color=None):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "type": "dog",
        "limit": 1,
        "sort": "random"
    }
    if color:
        params["color"] = color  # Make sure this matches Petfinder colors exactly

    url = "https://api.petfinder.com/v2/animals"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 401:
        print("Unauthorized: Token invalid or expired")
        return

    response.raise_for_status()

    data = response.json()
    dogs = data.get("animals", [])

    if not dogs:
        print(f"No dogs found matching your criteria: color={color}")
        return

    dog = dogs[0]
    name = dog.get("name", "Unknown")
    desc = dog.get("description", "No description available.")
    link = dog.get("url", "No link provided.")

    print(f"\nWe found you a {color or ''} dog! Meet {name}!\n")
    print(f"---{desc}\n")
    print(f"---Learn more: {link}")



my_api_key = 'AIzaSyCciB6bFHQnxXucRCfBBc-kt2NLsHy5pLQ'
genai.api_key = my_api_key

def getmood():
    usermood= input("Enter your mood. An AI will find a dog for you based on your mood: ")
    client = genai.Client( api_key=my_api_key,)

    response= client.models.generate_content( 

    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
    system_instruction= "You are a helpful assistant that recommends dog colors"
    "based on the user's emotional state. Pick from black, sable, golden"
    "Give only one sentence explaining why the color is suitable."),  
    
    contents="I am currently feeling \"" + usermood + "\". Recommend a dog breed.")


    response_text = response.text.strip()
    print("AI response:", response_text)

    petfinder_colors = ["Black", "Sable", "Golden"]
    recommended_color = None
    for color in petfinder_colors:
        if color.lower() in response_text.lower():
            recommended_color = color  # Use the exact casing here
            break


    if recommended_color:
        print(f"Recommended dog color based on mood: {recommended_color}")
        return recommended_color
    else:
        print("Could not find a recommended color in the response.")



def main():
    setup_db()

    print("Welcome! Please choose an option:")
    print("1. Log in")
    print("2. Create a new account")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        login()
        # call genAI to return color
    
    elif choice == "2":
        create_account()
    else:
        print("Invalid choice. Please run the program again.")


if __name__ == "__main__":
    main()









