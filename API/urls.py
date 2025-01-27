from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("search/", views.search_recipes, name="recipe_search"),
    path("local_recipes/", views.local_recipes, name="local_recipes"),
    path("local_recipes/<int:pk>/", views.local_recipes, name="local_recipes"),
    path("my_recipes/", views.my_recipes, name="my_recipes"),
    path("online_recipes/<int:pk>/", views.get_recipe_by_id, name="online_recipes"),
    path("random_recipe/", views.get_daily_random_recipe, name="random_recipe"),
    
    path("create_account/", views.create_account, name="create_account"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
]