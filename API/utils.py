import requests

def get_tasty_recipes(query):
    url = "https://tasty.p.rapidapi.com/recipes/list"
    headers = {
        "X-RapidAPI-Key": "1591f07ae7msh7f10f55f8f7af3dp1c379cjsn3c55198ef7a5",
        "X-RapidAPI-Host": "tasty.p.rapidapi.com"
    }
    params = {
        "from": 0,   # Starting index
        "size": 10,  # Number of recipes to fetch
        "tags":"under_30_minutes",
        "q": query   # Search query (e.g., "pasta")
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch recipes. Status code: {response.status_code}"}
    