from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=150)
    cook_time_minutes = models.IntegerField()
    credit_name = models.CharField(max_length=50)
    description = models.TextField()
    num_servings = models.IntegerField()
    prep_time = models.IntegerField()
    thumbnail = models.ImageField(upload_to='recipe/')
    rating_score = models.IntegerField() #will be calculated from likes & dislikes
    video_url = models.URLField()

    def __str__(self):
        return self.name

class Ingridient(models.Model):
    name = models.CharField(max_length=150)
    def __str__(self):
        return self.name

class Recipe_ingredient(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient_id = models.ForeignKey(Ingridient, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    def __str__(self):
        return self.recipe_id.name + '-' + self.ingredient_id.name

class Measurement(models.Model):
    recipe_ingredient_id =  models.ForeignKey(Recipe_ingredient, on_delete=models.CASCADE)
    unit = models.CharField(max_length=50)
    quantity = models.FloatField(null=True)
    abbreviaion = models.CharField(max_length=50,  null=True)

    def __str__(self):
        return self.recipe_ingredient_id.recipe_id.name + ' - ' + self.recipe_ingredient_id.ingredient_id.name + ' - ' + self.unit + 's'

class Instruction(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step = models.IntegerField(null=True)
    description = models.TextField()

    def __str__(self):
        return self.recipe_id.name + " - instruction - " + str(self.step)

class Image(models.Model):
    recipe_id =  models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='recipe_more/')

class Nutrition(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Recipe_nutrition(models.Model):
    recipe_id =  models.ForeignKey(Recipe, on_delete=models.CASCADE)
    nutrition_id =  models.ForeignKey(Nutrition, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return self.recipe_id.name + " - " + self.nutrition_id.name
    
class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.CharField(max_length=100)
    recipe_source = models.CharField(max_length=50, choices=[('api', 'API'), ('local', 'Local')])
    recipe_name = models.CharField(max_length=100)
    saved_at = models.DateTimeField(auto_now_add=True)

class Root_tags(models.Model):
    name = models.CharField(max_length=50)
    image_url = models.URLField(blank=True, null=True)  # New field for image URL

    def __str__(self):
        return self.name


class Parent_tags(models.Model):
    name = models.CharField(max_length=50)
    root = models.ForeignKey(Root_tags, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)  # New field for image URL

    def __str__(self):
        return self.name


class Tags(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(Parent_tags, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)  # New field for image URL

    def __str__(self):
        return self.name



    