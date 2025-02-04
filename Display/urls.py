from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("contact/", views.contact, name='contact'),
    path("search/", views.recipe_search, name="recipe_search"),
    path("archive/", views.archive, name='archive'),
    path("explore/<str:tag>", views.explore, name='explore'),
    path("recipe/", views.recipe, name='recipe'),
    path("single/", views.recipe, name='single'),


]