from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Food(models.Model):
    name = models.CharField(max_length=200, unique=True)
    carbs = models.FloatField(help_text="Carbohydrates in grams")
    protein = models.FloatField(help_text="Protein in grams")
    fats = models.FloatField(help_text="Fats in grams")
    calories = models.IntegerField(help_text="Total calories")

    def __str__(self):
        return self.name

class Consume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_consumed = models.ForeignKey(Food, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.food_consumed.name} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
