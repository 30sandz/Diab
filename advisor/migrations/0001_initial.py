# Generated by Django 3.2.25 on 2025-02-19 21:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('height', models.FloatField(help_text='Height in cm')),
                ('weight', models.FloatField(help_text='Weight in kg')),
                ('location', models.CharField(max_length=100)),
                ('diabetes_type', models.CharField(choices=[('1', 'Type 1'), ('2', 'Type 2'), ('O', 'Other')], max_length=1)),
                ('diagnosis_date', models.DateField()),
                ('last_hba1c', models.FloatField(blank=True, help_text='Last HbA1c reading', null=True)),
                ('default_insulin_level', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High')], default='normal', max_length=10)),
                ('other_conditions', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dietary_restriction', models.CharField(choices=[('none', 'No Restrictions'), ('vegetarian', 'Vegetarian'), ('vegan', 'Vegan'), ('other', 'Other')], default='none', max_length=20)),
                ('food_allergies', models.TextField(blank=True)),
                ('cultural_restrictions', models.TextField(blank=True)),
                ('preferred_cuisines', models.JSONField(default=list, help_text='List of preferred cuisines')),
                ('cooking_skill', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20)),
                ('max_cooking_time', models.IntegerField(default=60, help_text='Maximum cooking time in minutes')),
                ('serving_size', models.IntegerField(default=1)),
                ('meal_reminders', models.BooleanField(default=True)),
                ('sugar_check_reminders', models.BooleanField(default=True)),
                ('recipe_suggestions', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
