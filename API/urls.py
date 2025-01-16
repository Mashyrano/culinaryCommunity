from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.search_recipes, name="recipe_search"),
    path("local_recipes/", views.local_recipes, name="local_recipes"),
    path("local_recipe/<int:pk>/", views.local_recipe, name="local_recipe"),
]