from rest_framework import serializers
from .models import Recipe, Ingridient, Recipe_ingredient, Measurement, Instruction, Image, Nutrition, Recipe_nutrition

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'cook_time_minutes', 'credit_name', 'description', 
            'num_servings', 'prep_time', 'thumbnail', 'rating_score', 'video_url'
        ]

class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ['id', 'name']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe_ingredient
        fields = ['id', 'recipe_id', 'ingredient_id', 'description']

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['id', 'recipe_ingredient_id', 'unit', 'quantity', 'abbreviaion']

class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ['id', 'recipe_id', 'step', 'description']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'recipe_id', 'image']

class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = ['id', 'name']

class RecipeNutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe_nutrition
        fields = ['id', 'recipe_id', 'nutrition_id', 'quantity']
