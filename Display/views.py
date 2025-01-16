from django.http import HttpResponse
from django.shortcuts import render
import requests

def home(request):
    return render(request, 'home.html')

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