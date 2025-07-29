import requests

def get_oclc_number(isbn):
    url = f"https://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        book_list = data.get("list", [])
        if not book_list:
            print(f"[DEBUG] No book found for ISBN: {isbn}")
            return None

        oclcnums = book_list[0].get("oclcnum", [])
        if not oclcnums:
            print(f"[DEBUG] No OCLC number in response for ISBN: {isbn}")
            return None

        print(f"[DEBUG] Found OCLC number: {oclcnums[0]} for ISBN: {isbn}")
        return oclcnums[0]

    except Exception as e:
        print(f"[ERROR] Failed to get OCLC number for ISBN {isbn}: {e}")
        return None

