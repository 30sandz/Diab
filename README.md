git clone https://github.com/yourusername/diabetes-advisor.git

Create a .env file in the root directory and add the following:
USDA_API_KEY= your usda api key 
CLARIFAI_API_KEY= your clarifai api key
GEMINI_API_KEY= your gemini api key



1. python manage.py makemigrations - to see any changes in the database structure and to store the changes 
2. python manage.py migrate - to apply the changes to the database
3. python manage.py createsuper  - to create a admin user.......in that enter the username, email, passoword(the password won't be shown in the terminal just type it!)
3. python manage.py runserver - to run this project
