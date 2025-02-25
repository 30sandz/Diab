"""
WSGI config for diabetes_advisor project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diabetes_advisor.settings')

application = get_wsgi_application() 