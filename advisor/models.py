from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    location = models.CharField(max_length=100)
    
    DIABETES_TYPE_CHOICES = [
        ('1', 'Type 1'),
        ('2', 'Type 2'),
        ('O', 'Other')
    ]
    diabetes_type = models.CharField(max_length=1, choices=DIABETES_TYPE_CHOICES)
    diagnosis_date = models.DateField()
    last_hba1c = models.FloatField(null=True, blank=True, help_text="Last HbA1c reading")
    default_insulin_level = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')],
        default='normal'
    )
    other_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    DIETARY_CHOICES = [
        ('none', 'No Restrictions'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('other', 'Other')
    ]
    dietary_restriction = models.CharField(max_length=20, choices=DIETARY_CHOICES, default='none')
    food_allergies = models.TextField(blank=True)
    cultural_restrictions = models.TextField(blank=True)
    
    preferred_cuisines = models.JSONField(default=list, help_text="List of preferred cuisines")
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]
    cooking_skill = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='beginner')
    max_cooking_time = models.IntegerField(help_text="Maximum cooking time in minutes", default=60)
    serving_size = models.IntegerField(default=1)
    
    # Notification preferences
    meal_reminders = models.BooleanField(default=True)
    sugar_check_reminders = models.BooleanField(default=True)
    recipe_suggestions = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences" 