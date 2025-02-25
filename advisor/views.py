import os
import json
import requests
import tempfile
import google.generativeai as genai
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FoodInputForm, UserProfileForm, UserPreferencesForm
from .models import UserProfile, UserPreferences
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc, service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2

# Configuring Gemini API from env file
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def get_sugar_content(food_name):
    """Query USDA API for sugar content of a food item."""
    api_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        'api_key': settings.USDA_API_KEY,
        'query': food_name,
        'pageSize': 1,
        'dataType': ['Survey (FNDDS)', 'Foundation', 'SR Legacy']  # Include more data types, if wanted
    }
    
    try:
        print(f"Searching USDA database for: {food_name}")
        response = requests.get(api_url, params=params)
        
        if response.status_code != 200:
            print(f"USDA API Error: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        data = response.json()
        print(f"USDA API Response for {food_name}: {json.dumps(data, indent=2)}")
        
        if not data.get('foods'):
            print(f"No foods found for: {food_name}")
            return None
            
        food = data['foods'][0]
        print(f"Found food: {food.get('description', 'No description')}")
        
        # It Looks for sugar content in nutrients
        for nutrient in food.get('foodNutrients', []):
            nutrient_name = nutrient.get('nutrientName', '').lower()
            if 'sugar' in nutrient_name or 'sugars' in nutrient_name:
                value = nutrient.get('value', 0)
                print(f"Found sugar content for {food_name}: {value}g")
                return value
                
        print(f"No sugar content found in nutrients for: {food_name}")
        return None
        
    except Exception as e:
        print(f"Error fetching nutrition data for {food_name}: {str(e)}")
        return None

def analyze_food_image(image_file):
    """Analyze image using Clarifai API to identify food items for food advice.
    Returns only the top confident food items for nutritional analysis."""
    try:
        # Create the Clarifai channel and stub
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)

        # Create the metadata with your API key
        metadata = (('authorization', f'Key {settings.CLARIFAI_API_KEY}'),)

        # Read the image file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        with open(temp_file_path, 'rb') as f:
            file_bytes = f.read()

        # Clean up temporary file
        os.unlink(temp_file_path)

        # Create the request
        request = service_pb2.PostModelOutputsRequest(
            model_id='bd367be194cf45149e75f01d59f77ba7',  # This is Clarifai's food recognition model
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file_bytes
                        )
                    )
                )
            ]
        )

        # Make the request
        response = stub.PostModelOutputs(request, metadata=metadata)

        # Check if the request was successful
        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception(f"Request failed, status: {response.status.description}")

        # Extract only the top 3 most confident food items
        food_items = []
        for concept in response.outputs[0].data.concepts:
            if concept.value > 0.7:  # Higher confidence threshold for food advice
                food_items.append(concept.name)
                if len(food_items) >= 1:  # Limit to top 3 items
                    break

        return food_items

    except Exception as e:
        print(f"Error analyzing food image: {str(e)}")
        return []

def analyze_recipe_image(image_file):
    """Analyze image using Clarifai API to identify ingredients for recipe generation.
    Returns a broader range of identified ingredients with their confidence scores."""
    try:
        # Create the Clarifai channel and stub
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)

        # Create the metadata with your API key
        metadata = (('authorization', f'Key {settings.CLARIFAI_API_KEY}'),)

        # Read the image file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        with open(temp_file_path, 'rb') as f:
            file_bytes = f.read()

        # Clean up temporary file
        os.unlink(temp_file_path)

        # Create the request
        request = service_pb2.PostModelOutputsRequest(
            model_id='bd367be194cf45149e75f01d59f77ba7',  # This is Clarifai's food recognition model
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file_bytes
                        )
                    )
                )
            ]
        )

        # Make the request
        response = stub.PostModelOutputs(request, metadata=metadata)

        # Check if the request was successful
        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception(f"Request failed, status: {response.status.description}")

        # Extract ingredients with lower confidence threshold
        ingredients = []
        for concept in response.outputs[0].data.concepts:
            if concept.value > 0.4:  # Lower confidence threshold for recipe ingredients
                ingredients.append({
                    'name': concept.name,
                    'confidence': round(concept.value * 100, 1)  # Convert to percentage
                })
                if len(ingredients) >= 3:  # Allow more ingredients for recipes
                    break

        return ingredients

    except Exception as e:
        print(f"Error analyzing recipe image: {str(e)}")
        return []

def generate_advice(total_sugar, insulin_level):
    """Generate advice based on total sugar content and insulin level."""
    # Base thresholds (in grams)
    thresholds = {
        'low': {'danger': 30, 'caution': 20, 'average': 15, 'good': 10},
        'normal': {'danger': 40, 'caution': 30, 'average': 20, 'good': 15},
        'high': {'danger': 50, 'caution': 40, 'average': 30, 'good': 20}
    }
    
    t = thresholds[insulin_level]
    
    if total_sugar > t['danger']:
        return {
            'level': 'Danger',
            'class': 'bg-red-100 text-red-800',
            'message': 'Sugar content is very high for your insulin level. Avoid consuming this.'
        }
    elif total_sugar > t['caution']:
        return {
            'level': 'Caution',
            'class': 'bg-yellow-100 text-yellow-800',
            'message': 'Sugar content is high. Consider reducing portion size or finding alternatives.'
        }
    elif total_sugar > t['average']:
        return {
            'level': 'Average',
            'class': 'bg-blue-100 text-blue-800',
            'message': 'Sugar content is moderate. Monitor your portion size.'
        }
    elif total_sugar > t['good']:
        return {
            'level': 'Good',
            'class': 'bg-green-100 text-green-800',
            'message': 'Sugar content is within acceptable range.'
        }
    else:
        return {
            'level': 'Great',
            'class': 'bg-green-200 text-green-800',
            'message': 'Sugar content is very low. This is a great choice!'
        }

@csrf_exempt
def analyze_food(request):
    """Main view for analyzing food and providing advice."""
    if request.method == 'POST':
        form = FoodInputForm(request.POST, request.FILES)
        
        if form.is_valid():
            food_items = []
            input_source = None
            
            # Handle image upload
            if form.cleaned_data['food_image']:
                input_source = "Image Analysis"
                food_items = analyze_food_image(form.cleaned_data['food_image'])
                if not food_items:
                    return JsonResponse({
                        'error': 'Could not identify any food items in the image. Please try uploading a clearer image of food items.'
                    })
            
            # Handle text input
            elif form.cleaned_data['food_name']:
                input_source = "Text Input"
                food_items = [
                    item.strip() 
                    for item in form.cleaned_data['food_name'].split(',')
                    if item.strip()  # Only include non-empty items
                ]
                if not food_items:
                    return JsonResponse({
                        'error': 'Please enter at least one food item.'
                    })
            
            # Get sugar content for each food item
            total_sugar = 0
            food_data = []
            foods_with_data = 0
            
            for food in food_items:
                sugar_content = get_sugar_content(food)
                if sugar_content is not None:
                    total_sugar += sugar_content
                    foods_with_data += 1
                    food_data.append({
                        'name': food,
                        'sugar_content': round(sugar_content, 1)
                    })
                else:
                    food_data.append({
                        'name': food,
                        'sugar_content': None,
                        'error': 'Nutrition data not found in USDA database'
                    })
            
            if not foods_with_data:
                return JsonResponse({
                    'error': 'Could not find nutrition data for any of the specified foods. Please try different food items or check your spelling.'
                })
            
            # Generate advice
            insulin_level = form.cleaned_data['insulin_level']
            advice = generate_advice(total_sugar, insulin_level)
            
            # Add warning if some foods were missing data
            if len(food_data) > foods_with_data:
                missing_foods = len(food_data) - foods_with_data
                advice['message'] = f"Note: Nutrition data was not found for {missing_foods} food item(s). The advice is based only on foods with available data. " + advice['message']
            
            return JsonResponse({
                'success': True,
                'input_source': input_source,
                'food_data': food_data,
                'total_sugar': round(total_sugar, 1),
                'insulin_level': insulin_level,
                'advice': advice
            })
        
        return JsonResponse({'error': form.errors})
    
    form = FoodInputForm()
    return render(request, 'advisor/food_advice.html', {'form': form})

@login_required
def user_profile(request):
    """View and edit user profile."""
    try:
        profile = UserProfile.objects.get(user=request.user)
        form = UserProfileForm(instance=profile)
    except UserProfile.DoesNotExist:
        form = UserProfileForm()
    
    return render(request, 'advisor/user_profile.html', {'form': form})

@login_required
def update_profile(request):
    """Update user profile."""
    try:
        profile = UserProfile.objects.get(user=request.user)
        form = UserProfileForm(request.POST, instance=profile)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        form = UserProfileForm(request.POST, instance=profile)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')
    
    return render(request, 'advisor/user_profile.html', {'form': form})

@login_required
def user_preferences(request):
    """View and edit user preferences."""
    try:
        preferences = UserPreferences.objects.get(user=request.user)
        form = UserPreferencesForm(instance=preferences)
    except UserPreferences.DoesNotExist:
        form = UserPreferencesForm()
    
    return render(request, 'advisor/user_preferences.html', {'form': form})

@login_required
def update_preferences(request):
    """Update user preferences."""
    try:
        preferences = UserPreferences.objects.get(user=request.user)
        form = UserPreferencesForm(request.POST, instance=preferences)
    except UserPreferences.DoesNotExist:
        preferences = UserPreferences(user=request.user)
        form = UserPreferencesForm(request.POST, instance=preferences)
    
    if form.is_valid():
        preferences = form.save(commit=False)
        preferences.preferred_cuisines = request.POST.getlist('preferred_cuisines')
        preferences.save()
        messages.success(request, 'Preferences updated successfully!')
        return redirect('user_preferences')
    
    return render(request, 'advisor/user_preferences.html', {'form': form})

def check_profile_completion(user):
    """Check if user has completed their profile and preferences."""
    try:
        profile = UserProfile.objects.get(user=user)
        preferences = UserPreferences.objects.get(user=user)
        return True
    except (UserProfile.DoesNotExist, UserPreferences.DoesNotExist):
        return False

@login_required
def recipe_generator(request):
    """Handle recipe generation page and API endpoints."""
    # Check if profile is complete
    if not check_profile_completion(request.user):
        messages.warning(request, 'Please complete your profile and preferences before using the recipe generator.')
        return redirect('user_profile')
        
    if request.method == 'POST':
        # Check if this is a recipe generation request
        if request.POST.get('action') == 'generate_recipes':
            try:
                ingredients = json.loads(request.POST.get('ingredients', '[]'))
                if not ingredients:
                    return JsonResponse({
                        'error': 'No ingredients provided'
                    })
                
                # Get user's dietary restrictions and preferences
                preferences = UserPreferences.objects.get(user=request.user)
                
                # Include dietary restrictions in recipe generation
                dietary_context = f"The user follows a {preferences.dietary_restriction} diet"
                if preferences.food_allergies:
                    dietary_context += f" and has allergies to {preferences.food_allergies}"
                
                print("Calling get_recipe_suggestions...")
                recipes = get_recipe_suggestions(ingredients, dietary_context)
                print(f"Recipe generation response: {recipes}")
                
                if not recipes.get('success', False):
                    return JsonResponse({
                        'error': recipes.get('error', 'Failed to generate recipes. Please try again.')
                    })
                
                return JsonResponse({
                    'success': True,
                    'complete_recipes': recipes.get('complete_recipes', []),
                    'partial_recipes': recipes.get('partial_recipes', [])
                })
                
            except UserPreferences.DoesNotExist:
                return JsonResponse({
                    'error': 'Please complete your preferences before generating recipes.'
                })
            except Exception as e:
                print(f"Error in recipe_generator view: {str(e)}")
                return JsonResponse({
                    'error': f'Error generating recipes: {str(e)}'
                })
        
        # Handle image upload and ingredient detection
        elif 'image' in request.FILES:
            try:
                image_file = request.FILES['image']
                ingredients = analyze_recipe_image(image_file)
                
                if not ingredients:
                    return JsonResponse({
                        'error': 'Could not identify any ingredients in the image'
                    })
                
                return JsonResponse({
                    'ingredients': [item['name'] for item in ingredients],
                    'confidences': {item['name']: item['confidence'] for item in ingredients}
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': f'Error processing image: {str(e)}'
                })
    
    # Render the template for GET requests
    return render(request, 'advisor/recipe_generator.html')

def get_recipe_suggestions(ingredients, dietary_context=""):
    """Generate recipe suggestions using Gemini API, considering dietary restrictions."""
    try:
        print(f"Generating recipes for ingredients: {ingredients}")
        print(f"Dietary context: {dietary_context}")
        
        # Prepare the prompt
        prompt = f"""You are a culinary expert specializing in diabetes-friendly recipes.
        Create recipes using these ingredients: {', '.join(ingredients)}
        Consider these dietary restrictions: {dietary_context}

        Provide exactly two lists of recipes:
        1. Recipes using most of these ingredients (2-3 recipes)
        2. Popular recipes using at least one of these ingredients (2-3 recipes)

        Each recipe must include:
        - A creative name
        - A brief description of the dish
        - Difficulty level (Easy/Medium/Hard)

        Format your response EXACTLY as a JSON object with this structure:
        {{
            "complete_recipes": [
                {{
                    "name": "Recipe Name",
                    "description": "Brief description",
                    "difficulty": "Easy"
                }}
            ],
            "partial_recipes": [
                {{
                    "name": "Recipe Name",
                    "description": "Brief description",
                    "difficulty": "Easy"
                }}
            ]
        }}

        Requirements:
        - All recipes must be diabetes-friendly with low sugar content
        - Respect the user's dietary restrictions
        - Keep descriptions concise but informative
        - Use realistic combinations of ingredients
        """

        print("Sending prompt to Gemini API...")
        # Generate response
        response = model.generate_content(prompt)
        print(f"Raw Gemini response: {response.text}")
        
        # Clean and parse the response
        response_text = response.text.strip()
        
        # Remove any markdown code block indicators
        if response_text.startswith('```'):
            response_text = response_text.strip('```')
        if response_text.startswith('json'):
            response_text = response_text[4:].strip()
            
        # Try to find the JSON object if there's additional text
        try:
            start_idx = response_text.index('{')
            end_idx = response_text.rindex('}') + 1
            json_str = response_text[start_idx:end_idx]
        except ValueError:
            json_str = response_text
            
        print(f"Cleaned JSON string: {json_str}")
        
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to parse recipe suggestions. Please try again.',
                'complete_recipes': [],
                'partial_recipes': []
            }
        
        # Validate the response structure
        if not isinstance(result.get('complete_recipes'), list) or not isinstance(result.get('partial_recipes'), list):
            print("Invalid response structure")
            return {
                'success': False,
                'error': 'Invalid recipe format received. Please try again.',
                'complete_recipes': [],
                'partial_recipes': []
            }
        
        # Format recipes for display
        complete_recipes = []
        partial_recipes = []
        
        for recipe in result.get('complete_recipes', []):
            if all(key in recipe for key in ['name', 'description', 'difficulty']):
                complete_recipes.append(
                    f"{recipe['name']}\n" +
                    f"Difficulty: {recipe['difficulty']}\n" +
                    f"{recipe['description']}"
                )
            
        for recipe in result.get('partial_recipes', []):
            if all(key in recipe for key in ['name', 'description', 'difficulty']):
                partial_recipes.append(
                    f"{recipe['name']}\n" +
                    f"Difficulty: {recipe['difficulty']}\n" +
                    f"{recipe['description']}"
                )
        
        if not complete_recipes and not partial_recipes:
            print("No valid recipes found in response")
            return {
                'success': False,
                'error': 'No valid recipes could be generated. Please try different ingredients.',
                'complete_recipes': [],
                'partial_recipes': []
            }
        
        final_result = {
            'success': True,
            'complete_recipes': complete_recipes,
            'partial_recipes': partial_recipes
        }
        print(f"Final result: {final_result}")
        return final_result
        
    except Exception as e:
        print(f"Error generating recipes: {str(e)}")
        return {
            'success': False,
            'error': f'Error generating recipes: {str(e)}',
            'complete_recipes': [],
            'partial_recipes': []
        } 