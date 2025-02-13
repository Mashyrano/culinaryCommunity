import datetime
import math
import random
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serializer import RecipeSerializer, Root_tagsSerializer, Parent_tagsSerializer, TaggsSerializer
from .models import Recipe, SavedRecipe, Root_tags, Parent_tags, Tags
from rest_framework.response  import Response
from rest_framework  import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt



from django.db.models import F
from concurrent.futures import ThreadPoolExecutor


#Offline APIs

# ======== account ==============
@api_view(['POST'])
def create_account(request):
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    password = request.POST.get('password', '').strip()

    user = User.objects.create_user(
        username = username,
        password = password,
        email = email,
        first_name = first_name,
        last_name = last_name
    )
    return JsonResponse(f'{user.username} created', safe=False ,status=status.HTTP_201_CREATED)

# ======== recipes ==============

# return all recipes saved by user

@login_required
def my_recipes(request):
    user = request.user

    # Fetch saved recipe IDs and sources efficiently
    saved_recipes = SavedRecipe.objects.filter(user_id=user).values_list("recipe_id", "recipe_source")
    # Separate recipe IDs by source using dictionary grouping
    recipe_groups = {"local": [], "api": []}
    for recipe_id, source in saved_recipes:
        recipe_groups[source].append(recipe_id)

    # Fetch local recipes in batch
    local_recipes = [
        normalize_recipe(recipe, "local")
        for recipe in map(get_local_recipe, recipe_groups["local"])
        if recipe  # Ensure recipe is not None
    ]# NEXT LEVEL LIST comprehension

    # Fetch online recipes concurrently
    def fetch_online_recipe(recipe_id):
        try:
            url = f"https://tasty.p.rapidapi.com/recipes/get-more-info?id={recipe_id}"
            response = requests.get(url, headers=API_HEADERS)
            return normalize_recipe(response.json(), "online") if response.status_code == 200 else None
        except Exception as e:
            print(f"Failed to fetch online recipe {recipe_id}: {e}")
            return None

    with ThreadPoolExecutor() as executor:
        online_recipes = list(filter(None, executor.map(fetch_online_recipe, recipe_groups["api"])))

    # Combine results and return response
    combined_recipes = local_recipes + online_recipes
    if not combined_recipes:
        return JsonResponse({"error": "No recipes found"}, status=status.HTTP_404_NOT_FOUND)

    return JsonResponse(combined_recipes, safe=False, status=status.HTTP_200_OK)


@api_view(['GET'])
# get a local recipe by id
def local_recipes(request, pk):
    recipe = get_local_recipe(pk)

    if recipe:   
        return Response(recipe, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)
    
# Category of recipes
@api_view(['GET'])
def fetch_root_categories(request):
    roots = Root_tags.objects.all()
    serializer = Root_tagsSerializer(roots, many=True)
    return  JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_parent_categories(request):
    root = request.GET.get('root')
    root_id = Root_tags.objects.filter(name=root)
    try:
        parents = Parent_tags.objects.filter(root=root_id.first())
        serializer = Parent_tagsSerializer(parents, many=True)
        return  JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        return  JsonResponse(f"not fund + {e}", safe=False, status=status.HTTP_404_NOT_FOUND)

def fetch_categories(request):
    parent = request.GET.get('parent')
    parent_id = Parent_tags.objects.filter(name=parent).first()
    tags = Tags.objects.filter(parent=parent_id)
    serializer = TaggsSerializer(tags, many=True)
    return  JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


#Online APIs
url = "https://tasty.p.rapidapi.com/recipes/list"
API_HEADERS = {
    "X-RapidAPI-Key" : "ed4336eccbmsh603b5213ddfc726p131fddjsn9786bbd2fdb8",
    #"X-RapidAPI-Key": "7af5ecd32bmsh926189c0c2b057ap15ac7ajsn61dccf4b27aa",
    #"X-RapidAPI-Key": "1591f07ae7msh7f10f55f8f7af3dp1c379cjsn3c55198ef7a5",
    "X-RapidAPI-Host": "tasty.p.rapidapi.com"
}
# search a recipes by name or by tag
def search_recipes(request):
    query = request.GET.get('query', '')
    tags = request.GET.get('tags', '')
    size = request.GET.get('size', 10)  # Default size to 10
    recipe_list = []

    if query or tags:
        params = {
            "from": 0,
            "size": size,
            "q": query,
            "tags": tags
        }

        try:
            response = requests.get(url, headers=API_HEADERS, params=params)
            if response.status_code == 200:
                recipes = response.json()
                recipe_list = [normalize_recipe(recipe, "online") for recipe in recipes.get('results', [])]
                return JsonResponse(recipe_list, safe=False, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"error": "Failed to fetch recipes"}, status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({"error": "Query or tag parameter is required"}, status=400)

# Search a recipe by ID
@api_view(['GET'])
def get_recipe_by_id(request, pk):
    url = f"https://tasty.p.rapidapi.com/recipes/get-more-info?id={pk}"
    response = requests.get(url, headers=API_HEADERS)

    if response.status_code == 200:
        return JsonResponse( normalize_recipe(response.json(), 'online'), safe=False, status=200)
    else:
        return JsonResponse({"error": "Failed to fetch recipe"}, status=response.status_code)

# Fetch random recipe daily
@api_view(['GET'])
def get_daily_random_recipe(request):
    # Generate a random ID based on the date
    today = datetime.date.today()
    random_id = today.toordinal() % 1000  # Generate a number between 0 and 999

    url = f"https://tasty.p.rapidapi.com/recipes/get-more-info?id={random_id}"
    response = requests.get(url, headers=API_HEADERS)

    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False, status=200)
    else:
        return JsonResponse({"error": "Failed to fetch random recipe"}, status=response.status_code)

# ============= Helper functions ===============
def get_local_recipe(id):
    try:
        # Fetch the recipe by ID
        recipe = Recipe.objects.get(id=id)
        
        # Serialize the recipe with all nested data
        serializer = RecipeSerializer(recipe)
        
        return serializer.data
    except Recipe.DoesNotExist:
        return None
    
def normalize_recipe(recipe, source):
    """
    Standardizes the recipe data for both local and online sources.
    :param recipe: The raw recipe data (dict or model instance).
    :param source: 'local' or 'online'.
    :return: A dictionary with a consistent structure.
    """
    if not isinstance(recipe, dict):
        print("Unexpected recipe format:", recipe)  # Debug unexpected types
        return {}  

    if source == 'local':
        # Convert nutrition list to a dictionary
        nutrition_dict = {
            item.get('nutrition', {}).get('name'): item.get('quantity')
            for item in recipe.get('recipe_nutrition', []) if item.get('nutrition')
        }

        return {
            "id": recipe.get("id"),
            "title": recipe.get("name"),
            "description": recipe.get("description"),
            "ingredients": recipe.get("recipe_ingredients", []),
            "instructions": recipe.get("instructions", []),
            "image": recipe.get("thumbnail", []),
            "num_servings": recipe.get("num_servings"),
            "nutrition": nutrition_dict,
            "user_ratings": recipe.get("rating_score"),
            "credit": recipe.get("credit_name"),
            "prep_time": recipe.get("prep_time"),
            "cook_time": recipe.get("cook_time_minutes"),
            "tips": "",
            "video": "",
            "date": "",
            "source": "local",
        }

    elif source == 'online':
        # Normalize ingredients list
        ingredients = [
            {
                "ingredient": {"name": component.get("ingredient", {}).get("name")},
                "description": component.get("raw_text"),
                "measurements": [
                    {
                        "abbreviation": measurement.get("unit", {}).get("abbreviation"),
                        "quantity": measurement.get("quantity"),
                        "unit": measurement.get("unit", {}).get("name"),
                    }
                    for measurement in component.get("measurements", [])
                ],
            }
            for component in recipe.get("sections", [{}])[0].get("components", [])
        ]

        # Normalize instructions list
        instructions = [
            {
                "step": instruction.get("position"),
                "description": instruction.get("display_text"),
            }
            for instruction in recipe.get("instructions", [])
        ]

        #Normalize ratings
        rating = float(recipe.get("user_ratings", {}).get("score", ""))
        rating = rating * 10
        rating = math.floor(rating)

        return {
            "id": recipe.get("id"),
            "title": recipe.get("name"),
            "description": recipe.get("description"),
            "ingredients": ingredients,
            "instructions": instructions,
            "image": recipe.get("thumbnail_url"),
            "num_servings": recipe.get("num_servings"),
            "nutrition": recipe.get("nutrition", {}),
            "user_ratings": rating,
            "credit": recipe.get("credits", [{}])[0].get("name", ""),
            "prep_time": recipe.get("prep_time_minutes"),
            "cook_time": recipe.get("cook_time_minutes", ""),
            "tips": recipe.get("tips_summary", {}).get("content", ""),
            "video": recipe.get("video_url",""),
            "date": recipe.get("created_at", ""),
            "source": "online",
        }

    return {}




