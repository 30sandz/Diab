from django.urls import path
from . import views

urlpatterns = [
    path('', views.analyze_food, name='analyze_food'),
    path('recipe-generator/', views.recipe_generator, name='recipe_generator'),
    path('profile/', views.user_profile, name='user_profile'),
    path('preferences/', views.user_preferences, name='user_preferences'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),
] 