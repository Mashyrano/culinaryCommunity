from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("contact/", views.contact, name='contact'),
    path("archive/", views.archive, name='archive'),
    path("explore/<str:tag>", views.explore, name='explore'),
    path("recipe/", views.recipe_search, name='recipes'),
    path("login/", views.login_view, name='login'),
    path("logout/", views.logout_user, name="logout"),
    path("single/<int:pk>", views.single_recipe, name='single'),

]