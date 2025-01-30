import random
from django.http import HttpResponse
from django.shortcuts import render
import requests

def home(request):
    context = get_context()
    return render(request, 'home.html', context)

def contact(request):
    return render(request, 'contact.html')

def recipe_search(request):
    query = request.GET.get('query', '')
    recipes = []

    if query:
        # Call the API to get recipe data
        response = requests.get(f'http://127.0.0.1:8000/API/search/?query={query}')
        if response.status_code == 200:
            recipes = response.json().get('results', [])
    
    return render(request, 'recipe_search.html', {'recipes': recipes, 'query': query})

# helper  functions
def get_context():
    try:
        # Fetch random recipe
        response = requests.get('http://127.0.0.1:8000/API/random_recipe')
    except Exception as e:
        print(f"Error fetching random recipe: {e}")
        response = None

    # Fetch categories
    try:
        categories = get_4_categories()
    except Exception as e:
        print(f"Error fetching categories: {e}")
        categories = []

    # Debugging output
    print("Categories:", categories)

    # Build the context
    context = {
        "random": response.json() if response and response.status_code == 200 else {
            "name": "offline name",
            "description": "offline description",
            "thumbnail_url": "######"
        },
        "categories": categories if categories else [
            {"name": "Default Category", "description": "No categories available"}
        ]
    }

    return context



import random
import requests

def get_4_categories():
    categories = [
        "Under 30 Minutes",
        "Under 45 Minutes",
        "5 Ingredients or Less",
        "Easy",
        "Under 1 Hour",
        "Under 15 Minutes",
        "Cinco de Mayo",
        "Mother's Day",
        "New Years",
        "4th of July",
        "Christmas",
        "Thanksgiving",
        "Breakfast",
        "Dinner",
        "Appetizers",
        "Brunch",
        "Desserts",
        "Drinks",
        "Lunch",
        "Snacks",
        "Sides",
        "Deep-Fry",
        "Comfort Food",
        "No Bake Desserts",
        "Steam",
        "Meal Prep",
        "Grill",
        "One-Pot or Pan",
        "Budget"
    ]
    for i in range(len(categories)):
        categories[i] = categories[i].lower()
        

    # Generate four random unique indices for categories
    random_indices = random.sample(range(len(categories)), 5)
    category_images = []
    for category in random_indices:
        url = f'http://127.0.0.1:8000/API/search_light/?tags={categories[category]}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                category_images.append({
                    "category": categories[category],
                    "image": data.get("image", None)
                })
            else:
                category_images.append({
                    "category": categories[category],
                    "image": None
                })
        except Exception as e:
            print(f"Error fetching category {categories[category]}: {e}")
            category_images.append({
                "category": categories[category],
                "image": None
            })
        
    return category_images