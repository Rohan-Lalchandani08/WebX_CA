import os
import logging
from app import app
from db import init_db

# Set up logging for easier debugging
logging.basicConfig(level=logging.DEBUG)

# Initialize database with default data
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
