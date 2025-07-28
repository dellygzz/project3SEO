worldcat.py
import requests

def get_oclc_number(isbn):
    url = f"https://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["list"][0]["oclcnum"][0]
    except Exception:
        return None

