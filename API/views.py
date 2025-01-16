import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .serializer import RecipeSerializer
from .models import Recipe, Ingridient, Recipe_ingredient, Measurement, Instruction, Image, Nutrition, Recipe_nutrition
from rest_framework.response  import Response
from rest_framework  import status

import json
from django.forms.models import model_to_dict
#Offline APIs

@api_view(['GET'])
# returns a list of all the recipes dictionary
def local_recipes(request):
    recipes = Recipe.objects.all()
    recipesSeliarizer = RecipeSerializer(recipes, many=True)
    #return JsonResponse(recipesSeliarizer.data, safe=False)
    return Response(recipesSeliarizer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def local_recipe(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    #recipeSeliarizer = RecipeSerializer(recipe)
    #return JsonResponse(recipesSeliarizer.data, safe=False)

    recipe_dict = model_to_dict(recipe, exclude=['thumbnail'])
    #recipe_json = json.dumps(recipe_dict)
    #return JsonResponse(recipe_dict, safe=False)

    ingredients = Recipe_ingredient.objects.filter(recipe_id=1)
    ingredients_dict = model_to_dict(ingredients)
    return Response(recipe_dict, status=status.HTTP_200_OK)

#Online to Offline


#Online APIs
def search_recipes(request):
    query = request.GET.get('query', '')
    if query:
        url = "https://tasty.p.rapidapi.com/recipes/list"
        headers = {
            "X-RapidAPI-Key": "1591f07ae7msh7f10f55f8f7af3dp1c379cjsn3c55198ef7a5",
            "X-RapidAPI-Host": "tasty.p.rapidapi.com"
        }
        params = {
            "from": 0,   # Starting index
            "size": 1,  # Number of recipes to fetch
            "tags":"under_30_minutes",
            "q": query   # Search query (e.g., "pasta")
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            with open('nested_data.txt', 'w') as file:
                write_nested_dict(response.json(), file)
                print('added')
            return JsonResponse(response.json())
        else:
            return JsonResponse({"error": "Failed to fetch recipes"}, status=response.status_code)
    return JsonResponse({"error": "Query parameter is required"}, status=400)



def write_nested_dict(data, file, indent=0):
    # If the data is a dictionary
    if isinstance(data, dict):
        for key, value in data.items():
            file.write(' ' * indent + f"{key}:\n")
            write_nested_dict(value, file, indent + 4)  # Increase indentation for nested items
    # If the data is a list
    elif isinstance(data, list):
        for index, item in enumerate(data):
            file.write(' ' * indent + f"[{index}]\n")
            write_nested_dict(item, file, indent + 4)
    else:
        # Write the value if it's a simple data type (string, int, etc.)
        file.write(' ' * indent + str(data) + '\n')