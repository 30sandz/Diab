from django import forms
from .models import UserProfile, UserPreferences

class FoodInputForm(forms.Form):
    INSULIN_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]
    
    food_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input px-4 py-3 rounded-lg border focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter food name(s), separated by commas'
        })
    )
    
    food_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input px-4 py-3 rounded-lg border focus:ring-2 focus:ring-blue-500',
            'accept': 'image/*'
        })
    )
    
    insulin_level = forms.ChoiceField(
        choices=INSULIN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select px-4 py-3 rounded-lg border focus:ring-2 focus:ring-blue-500'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        food_name = cleaned_data.get('food_name')
        food_image = cleaned_data.get('food_image')
        
        if not food_name and not food_image:
            raise forms.ValidationError(
                "Please either enter food names or upload an image"
            )
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': '1',
                'max': '120'
            }),
            'gender': forms.Select(attrs={'class': 'form-select rounded-lg'}),
            'height': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'step': '0.1',
                'min': '1'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'step': '0.1',
                'min': '1'
            }),
            'location': forms.TextInput(attrs={'class': 'form-input rounded-lg'}),
            'diabetes_type': forms.Select(attrs={'class': 'form-select rounded-lg'}),
            'diagnosis_date': forms.DateInput(attrs={
                'class': 'form-input rounded-lg',
                'type': 'date'
            }),
            'last_hba1c': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'step': '0.1'
            }),
            'default_insulin_level': forms.Select(attrs={'class': 'form-select rounded-lg'}),
            'other_conditions': forms.Textarea(attrs={
                'class': 'form-textarea rounded-lg',
                'rows': 3
            }),
        }

class UserPreferencesForm(forms.ModelForm):
    preferred_cuisines = forms.MultipleChoiceField(
        choices=[
            ('italian', 'Italian'),
            ('mexican', 'Mexican'),
            ('chinese', 'Chinese'),
            ('indian', 'Indian'),
            ('japanese', 'Japanese'),
            ('mediterranean', 'Mediterranean'),
            ('american', 'American'),
            ('thai', 'Thai'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-checkbox'}),
        required=False
    )

    class Meta:
        model = UserPreferences
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'dietary_restriction': forms.Select(attrs={'class': 'form-select rounded-lg'}),
            'food_allergies': forms.Textarea(attrs={
                'class': 'form-textarea rounded-lg',
                'rows': 3,
                'placeholder': 'List any food allergies...'
            }),
            'cultural_restrictions': forms.Textarea(attrs={
                'class': 'form-textarea rounded-lg',
                'rows': 3,
                'placeholder': 'List any cultural dietary restrictions...'
            }),
            'cooking_skill': forms.Select(attrs={'class': 'form-select rounded-lg'}),
            'max_cooking_time': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': '15',
                'max': '240',
                'step': '15'
            }),
            'serving_size': forms.NumberInput(attrs={
                'class': 'form-input rounded-lg',
                'min': '1',
                'max': '10'
            }),
            'meal_reminders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'sugar_check_reminders': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'recipe_suggestions': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        } 