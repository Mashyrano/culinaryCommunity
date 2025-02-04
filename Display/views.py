import random
from django.http import HttpResponse
from django.shortcuts import render
import requests
from API.serializer import TaggsSerializer
from API.models import Tags

def home(request):
    context = get_context()
    return render(request, 'home.html', context)

def contact(request):
    return render(request, 'contact.html')

def singles(request):
    return render(request, 'singles.html')

#### root categories ######
def archive(request):
    response = requests.get('http://127.0.0.1:8000/API/root_categories/')
    if response.status_code == 200:
        context = {
            "categories"  :  response.json(),
            "source" : "root"
        }
    return render(request, 'archive.html', context)
#### parent categories ######
def explore(request, tag):
    context = {}
    source = request.GET.get('source')
    if source == 'root':
        response = requests.get(f'http://127.0.0.1:8000/API/parent_categories?root={tag}')
        if response.status_code == 200:
            context = {
            "categories"  :  response.json(),
            "source" : "parent"
        }

    elif source == 'parent':
        response = requests.get(f'http://127.0.0.1:8000/API/tags?parent={tag}')
        if response.status_code == 200:
            context = {
            "categories"  :  response.json(),
            "source" : "tag"
        }

    elif source == 'tag':
        response = requests.get(f'http://127.0.0.1:8000/API/search?tags={tag.lower().replace('&', 'and')}&size=10&from=0')
       
    return render(request, 'archive.html', context)

def recipe(request):
    return render(request, 'recipe.html')

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


def get_4_categories():
    tags = Tags.objects.all()
    data = TaggsSerializer(tags, many=True)
    tags_data = data.data
    print(type(tags_data))
    fourTags = []
    random_indice = random.sample(range(len(tags_data)), 4)
    for indice in random_indice:
        fourTags.append(tags_data[indice])
    return fourTags