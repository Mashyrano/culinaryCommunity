from django.contrib import admin
from API.models import Recipe
from API.models import Recipe_ingredient
from API.models import Ingridient
from API.models import Image
from API.models import Instruction
from API.models import Recipe_nutrition
from API.models import  Nutrition
from API.models import Measurement
# Register your models here.

admin.site.register(Recipe)
admin.site.register(Recipe_ingredient)
admin.site.register(Ingridient)
admin.site.register(Instruction)
admin.site.register(Image)
admin.site.register(Recipe_nutrition)
admin.site.register(Nutrition)
admin.site.register(Measurement)