from rest_framework import serializers
from .models import Recipe, Ingridient, Recipe_ingredient, Measurement, Instruction, Image, Nutrition, Recipe_nutrition, SavedRecipe,  Root_tags,  Parent_tags, Tags

class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ['id', 'unit', 'quantity', 'abbreviaion']

class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ['id', 'name']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngridientSerializer(source='ingredient_id')  # Get ingredient details
    measurements = MeasurementSerializer(many=True, source='measurement_set')  # Include related measurements

    class Meta:
        model = Recipe_ingredient
        fields = ['id', 'ingredient', 'description', 'measurements']

class NutritionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrition
        fields = ['id', 'name']

class RecipeNutritionSerializer(serializers.ModelSerializer):
    nutrition = NutritionSerializer(source='nutrition_id')  # Include nutrition details

    class Meta:
        model = Recipe_nutrition
        fields = ['id', 'nutrition', 'quantity']

class InstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instruction
        fields = ['id', 'step', 'description']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class RecipeSerializer(serializers.ModelSerializer):
    recipe_nutrition = RecipeNutritionSerializer(many=True, source='recipe_nutrition_set')
    recipe_ingredients = RecipeIngredientSerializer(many=True, source='recipe_ingredient_set')
    instructions = InstructionSerializer(many=True, source='instruction_set')
    images = ImageSerializer(many=True, source='image_set')

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'cook_time_minutes', 'credit_name', 'description', 
            'num_servings', 'prep_time', 'thumbnail', 'rating_score', 'video_url',
            'recipe_nutrition', 'recipe_ingredients', 'instructions', 'images'
        ]

class SavedRecipeSeializer(serializers.ModelSerializer):
    class Meta:
        model = SavedRecipe
        fields = ['id','user','recipe_id','recipe_source','recipe_name','saved_at']
        read_only_fields = ['id','user','saved_at']

class Root_tagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Root_tags
        fields = ['id', 'name', 'image_url']

class Parent_tagsSerializer(serializers.ModelSerializer):
    root = Root_tagsSerializer()
    class Meta:
        model = Parent_tags
        fields = ['id', 'name', 'root', 'image_url']

class TaggsSerializer(serializers.ModelSerializer):
    parent = Parent_tagsSerializer()
    class Meta:
        model = Parent_tags
        fields = ['id', 'name', 'parent', 'image_url']