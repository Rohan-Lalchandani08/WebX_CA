import os

# App configuration
SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')

# API Keys
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')