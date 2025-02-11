import random
from django.http import JsonResponse
import requests
from API.serializer import TaggsSerializer
from API.models import Tags
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from rest_framework  import status
from rest_framework.decorators import api_view

def home(request):
    context = get_context()
    return render(request, 'home.html', context)

def contact(request):
    return render(request, 'contact.html')

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to home or dashboard
    else:
        form = AuthenticationForm()

    return render(request, "account/login.html", {"form": form})

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return redirect('home')

def single_recipe(request, pk):
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
        response = requests.get(f'http://127.0.0.1:8000/API/search?tags={tag.lower().replace('&', 'and').replace('-', ' ')}&size=10&from=0')
        if response.status_code == 200:
            context = {
            "recipes"  :  response.json(),
            "source" : "tag"
        }
        else:
            context = {
                    "recipes" :   [{
                        "title":"offline title",
                        "image":"hhttp://ghhjsd.cb",
                        "description":"offline description",
                        "nutrition": {
                            "offline":"offline"
                        }
                    }],
                    "source" : "recipe"
                    }
        return render(request, 'recipe.html', context)


    return render(request, 'archive.html', context)

def recipe_search(request):
    query = request.GET.get('query', '')
    recipes = []

    if query:
        # Call the API to get recipe data
        response = requests.get(f'http://127.0.0.1:8000/API/search/?query={query}')
        if response.status_code == 200:
            recipes = response.json()
            # Paginate recipes (10 per page)
            #paginator = Paginator(recipes, 3)
            #page_number = request.GET.get("page", 1)
            #page_obj = paginator.get_page(page_number)
            #return render(request, "recipe.html", {"page_obj": page_obj, 'query': query})
        elif response.status_code == 500:
            recipes = [
                {
                    "title":"offline title",
                    "image":"hhttp://ghhjsd.cb",
                    "description":"offline description",
                    "nutrition": {
                        "offline":"offline"
                    }

                }

                ]
    
    return render(request, 'recipe.html', {'recipes': recipes, 'query': query})

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