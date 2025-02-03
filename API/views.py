import datetime
import random
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serializer import RecipeSerializer, SavedRecipeSeializer, Root_tagsSerializer, Parent_tagsSerializer, TaggsSerializer
from .models import Recipe, SavedRecipe, Root_tags, Parent_tags, Tags
from rest_framework.response  import Response
from rest_framework  import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


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

#@api_view(['POST'])
@csrf_exempt
def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse(f'{user.username} logged  in', safe=False ,status=status.HTTP_200_OK)
    else:
        return JsonResponse(f'invalid credentials', safe=False ,status=status.HTTP_401_UNAUTHORIZED)
        #return render(request, 'login.html')

#@api_view(['POST'])
@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse(f'logout success', safe=False ,status=status.HTTP_200_OK)

# ======== recipes ==============

# return all recipes saved by user
@login_required
def my_recipes(request):
    # Get the logged-in user's ID
    user = request.user
    saved_recipes = SavedRecipe.objects.filter(user_id=user)
    
    # Separate recipe IDs by source
    local_recipe_ids = []
    online_recipe_ids = []
    for recipe in saved_recipes:
        if recipe.recipe_source == 'local':
            local_recipe_ids.append(recipe.recipe_id)
        else:
            online_recipe_ids.append(recipe.recipe_id)

    # Fetch local recipes
    local_recipes = []
    for recipe_id in local_recipe_ids:
        recipe = get_local_recipe(recipe_id)
        if recipe:
            local_recipes.append(normalize_recipe(recipe, 'local'))

    # Fetch online recipes
    online_recipes = []
    for recipe_id in online_recipe_ids:
        try:
            url = f"https://tasty.p.rapidapi.com/recipes/get-more-info?id={recipe_id}"
            response = requests.get(url, headers=API_HEADERS)
            if response.status_code == 200:
                online_recipes.append(normalize_recipe(response.json(), 'online'))
        except Exception as e:
            # Log errors if needed
            print(f"Failed to fetch online recipe with ID {recipe_id}: {e}")

    # Combine all recipes and return the response
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
    parents = Parent_tags.objects.filter(root=root_id.first())
    serializer = Parent_tagsSerializer(parents, many=True)
    return  JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

def fetch_categories(request):
    parent = request.GET.get('parent')
    parent_id = Parent_tags.objects.filter(name=parent).first()
    tags = Tags.objects.filter(parent=parent_id)
    serializer = TaggsSerializer(tags, many=True)
    return  JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


#Online APIs
url = "https://tasty.p.rapidapi.com/recipes/list"
API_HEADERS = {
    "X-RapidAPI-Key": "7af5ecd32bmsh926189c0c2b057ap15ac7ajsn61dccf4b27aa",
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

# for categories
def search_recipes_lightweight(request):
    tags = request.GET.get('tags', '')
    if not tags:
        return JsonResponse({"error": "Tag parameter is required"}, status=400)

    params = {
        "from": 0,
        "size": 10,
        "tags": tags
    }

    try:
        response = requests.get(url, headers=API_HEADERS, params=params)
        if response.status_code == 200:
            recipes = response.json()
            results = recipes.get('results', [])
            if results:
                # Extract random int url
                random_indice = random.sample(range(len(results)), 1)
                first_result = results[random_indice[0]]
                thumbnail_url = first_result.get('thumbnail_url', '')
                name = first_result.get('name', '')
                return JsonResponse({"category": tags, "image": thumbnail_url, "name": name}, safe=False)
            else:
                return JsonResponse({"category": tags, "image": None}, safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch recipes"}, status=response.status_code)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)


# Search a recipe by ID
@api_view(['GET'])
def get_recipe_by_id(request, pk):
    url = f"https://tasty.p.rapidapi.com/recipes/get-more-info?id={pk}"
    response = requests.get(url, headers=API_HEADERS)

    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False, status=200)
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
        return {}  # Skip non-dictionary recipes

    if source == 'local':
        nutrition_list = recipe.get('recipe_nutrition')
        nutrition_dict = {}
        for nutrition in nutrition_list:
            nutrition_dict[nutrition.get('nutrition').get('name')] = nutrition.get('quantity')

        return {
            "id": recipe.get('id'), # matches 
            "title": recipe.get('name'), # matches 
            "description": recipe.get('description'), # matches 
            "ingredients": recipe.get('recipe_ingredients', []), # matches 
            "instructions": recipe.get('instructions', []), # matches 
            "image": recipe.get('thumbnail', []), # matches 
            "num_servings": recipe.get('num_servings', []),# matches 
            "nutrition": nutrition_dict, # matches 
            "source": "local",
            # user_ratings
            # tips_summary #content
            # credits # name
            
        }
    elif source == 'online':
        # normalize ingredients list
        ingredient_list = []
        component_list = recipe.get('sections')[0].get('components')
        for component in component_list:
            ingredient_dict = {
            'ingredient': {},
            'measurements' : []
            }
            ingredient_dict['ingredient']['name'] = component.get('ingredient').get('name')
            ingredient_dict['description'] = component.get('raw_text')
            for measurement in component.get('measurements'):
                ingredient_dict['measurements'].append({
                    'abbreviation': measurement.get('unit').get('abbreviation'),
                    'quantity': measurement.get('quantity'),
                    'unit': measurement.get('unit').get('name')
                })
            ingredient_list.append(ingredient_dict)

        # normalize instructions list
        instructions = []
        instruction_list = recipe.get('instructions')
        for instruction in instruction_list:
            instructions.append({
                'step': instruction.get('position'),
                'description' : instruction.get('display_text')
            })

        return {
            "id": recipe.get('id'), # matches 
            "title": recipe.get('name'), # matches 
            "description": recipe.get('description'), # matches 
            "ingredients": ingredient_list, # matches 
            "instructions": instructions, # matches 
            "image": recipe.get('thumbnail_url'), # matches 
            "num_servings": recipe.get('num_servings', []),# matches 
            "nutrition": recipe.get('nutrition', []), # matches 
            "source": "online",
            # user_ratings
            # tips_summary #content
            # credits # name
        }
    return {}



