import datetime
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serializer import RecipeSerializer, SavedRecipeSeializer
from .models import Recipe, SavedRecipe,Ingridient, Recipe_ingredient, Measurement, Instruction, Image, Nutrition, Recipe_nutrition
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

@login_required
# return all recipes saved by user
def my_recipes(request):
    userQuery = User.objects.filter(username=request.user)
    recipes =  SavedRecipe.objects.filter(user_id=userQuery.first())
    myRecipesSerializer = SavedRecipeSeializer(recipes, many=True)
    local_recipe_ids = []
    online_recipe_ids = []
    local_recipes=[]

    # go through recipes and check source
    for link in myRecipesSerializer.data:
        if link['recipe_source'] == 'local':
            local_recipe_ids.append(link['recipe_id'])
        else:
            online_recipe_ids.append(link['recipe_id'])

    if len(local_recipe_ids) == 0 and len(online_recipe_ids) == 0:
        return JsonResponse('no recipes found', safe=False ,status=status.HTTP_404_NOT_FOUND)
    
    # if offline source query database and compile list 
    for recipe_id in local_recipe_ids:
        recipe = get_local_recipe(recipe_id)
        if recipe:
            local_recipes.append(recipe)

    # if online call the api and  compile

    # compile into one response and return response
    return JsonResponse(local_recipes, safe=False ,status=status.HTTP_200_OK)


@api_view(['GET'])
# get a local recipe by id
def local_recipes(request, pk):
    recipe = get_local_recipe(pk)

    if recipe:   
        return Response(recipe, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)
    


#Online APIs
url = "https://tasty.p.rapidapi.com/recipes/list"
API_HEADERS = {
    "X-RapidAPI-Key": "1591f07ae7msh7f10f55f8f7af3dp1c379cjsn3c55198ef7a5",
    "X-RapidAPI-Host": "tasty.p.rapidapi.com"
}
# search a recipes by name
def search_recipes(request):
    query = request.GET.get('query', '')
    if query:
        params = {
            "from": 0,   # Starting index
            "size": 10,  # Number of recipes to fetch
            "q": query   # Search query (e.g., "pasta")
        }

        response = requests.get(url, headers=API_HEADERS, params=params)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({"error": "Failed to fetch recipes"}, status=response.status_code)
    return JsonResponse({"error": "Query parameter is required"}, status=400)

# Search a recipe by ID
@api_view(['GET'])
def get_recipe_by_id(request, recipe_id):
    url = f"https://tasty.p.rapidapi.com/recipes/get-more-info?id={recipe_id}"
    response = requests.get(url, headers=API_HEADERS)

    if response.status_code == 200:
        return JsonResponse(response.json(), safe=False, status=200)
    else:
        return JsonResponse({"error": "Failed to fetch recipe"}, status=response.status_code)

# Search by Category of recipes


# View 2: Fetch random recipe daily
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