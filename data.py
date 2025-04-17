import os
import json
from datetime import datetime

# File paths for data storage
DESTINATIONS_FILE = 'static/data/destinations.json'
ITINERARIES_FILE = 'static/data/itineraries.json'
TRAVEL_TIPS_FILE = 'static/data/travel_tips.json'

def ensure_file_exists(file_path, default_content=None):
    """Ensure the data file exists, create it if it doesn't"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            if default_content is None:
                json.dump([], f)
            else:
                json.dump(default_content, f)

# Initialize data files if they don't exist
ensure_file_exists(DESTINATIONS_FILE, [
    {
        "id": "1",
        "name": "Paris",
        "country": "France",
        "description": "The City of Light draws millions of visitors every year with its unforgettable ambiance. Of course, the divine cuisine and vast art collections deserve some of the credit as well.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8cGFyaXN8ZW58MHx8MHx8fDA%3D",
        "attractions": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Champs-Élysées"],
        "tags": ["romantic", "cultural", "historic", "food"],
        "best_time_to_visit": "April to June, October to early November"
    },
    {
        "id": "2",
        "name": "Tokyo",
        "country": "Japan",
        "description": "Tokyo is a city of contrasts, from ancient temples to ultramodern skyscrapers. It's a hub of cutting-edge technology, iconic fashion, and delicious cuisine.",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8dG9reW98ZW58MHx8MHx8fDA%3D",
        "attractions": ["Tokyo Skytree", "Senso-ji Temple", "Shibuya Crossing", "Tokyo Disneyland"],
        "tags": ["modern", "cultural", "food", "shopping"],
        "best_time_to_visit": "March to May, September to November"
    },
    {
        "id": "3",
        "name": "New York City",
        "country": "United States",
        "description": "The Big Apple boasts with world-famous attractions, diverse cultures, iconic landmarks, and electric atmosphere. It truly is the city that never sleeps.",
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8bmV3JTIweW9yayUyMGNpdHl8ZW58MHx8MHx8fDA%3D",
        "attractions": ["Statue of Liberty", "Central Park", "Empire State Building", "Times Square"],
        "tags": ["urban", "cultural", "food", "shopping"],
        "best_time_to_visit": "April to June, September to early November"
    },
    {
        "id": "4",
        "name": "Rome",
        "country": "Italy",
        "description": "The Eternal City is a must-visit for history buffs, food lovers, and romantics. Its ancient ruins, Renaissance art, and vibrant street life make it an unforgettable destination.",
        "image_url": "https://images.unsplash.com/photo-1525874684015-58379d421a52?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cm9tZXxlbnwwfHwwfHx8MA%3D%3D",
        "attractions": ["Colosseum", "Vatican City", "Trevi Fountain", "Roman Forum"],
        "tags": ["historic", "cultural", "food", "romantic"],
        "best_time_to_visit": "April to May, September to October"
    },
    {
        "id": "5",
        "name": "Bali",
        "country": "Indonesia",
        "description": "Bali enchants with its dramatic dances and colorful ceremonies, its arts and crafts, its luxurious beach resorts and exciting nightlife, and its lush mountains and sacred volcanoes.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8YmFsaXxlbnwwfHwwfHx8MA%3D%3D",
        "attractions": ["Ubud Monkey Forest", "Tanah Lot", "Uluwatu Temple", "Tegallalang Rice Terraces"],
        "tags": ["beach", "cultural", "relaxation", "adventure"],
        "best_time_to_visit": "April to June, September to October"
    },
    {
        "id": "6",
        "name": "Barcelona",
        "country": "Spain",
        "description": "Barcelona is an enchanting seaside city with boundless culture, fabled architecture, and a world-class drinking and dining scene. Gaudi's influence is everywhere.",
        "image_url": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YmFyY2Vsb25hfGVufDB8fDB8fHww",
        "attractions": ["Sagrada Familia", "Park Güell", "La Rambla", "Casa Batlló"],
        "tags": ["beach", "cultural", "architecture", "food"],
        "best_time_to_visit": "May to June, September to October"
    }
])

ensure_file_exists(ITINERARIES_FILE, [])

ensure_file_exists(TRAVEL_TIPS_FILE, [
    {
        "id": "1",
        "category": "Packing",
        "title": "Essential Packing Tips",
        "tips": [
            "Roll clothes instead of folding to save space and prevent wrinkles",
            "Pack a small first-aid kit with basic medications",
            "Bring a universal power adapter for international travel",
            "Use packing cubes to organize your suitcase",
            "Always pack a change of clothes in your carry-on"
        ]
    },
    {
        "id": "2",
        "category": "Safety",
        "title": "Staying Safe While Traveling",
        "tips": [
            "Keep digital copies of important documents",
            "Share your itinerary with a trusted friend or family member",
            "Research common scams at your destination",
            "Register with your country's travel advisory program",
            "Know basic phrases in the local language, especially for emergencies"
        ]
    },
    {
        "id": "3",
        "category": "Budget",
        "title": "Money-Saving Travel Tips",
        "tips": [
            "Book flights in incognito mode to avoid price increases",
            "Use local transportation instead of taxis when possible",
            "Eat where the locals eat for better prices and authentic food",
            "Consider accommodations with kitchen access to save on meals",
            "Research free activities and attractions at your destination"
        ]
    },
    {
        "id": "4",
        "category": "Health",
        "title": "Staying Healthy While Traveling",
        "tips": [
            "Stay hydrated, especially on flights",
            "Bring sanitizing wipes for high-touch surfaces",
            "Check if you need vaccines before traveling",
            "Know how to say 'I have an allergy' in the local language",
            "Carry probiotics to help with digestive issues"
        ]
    }
])

def load_destinations():
    """Load destination data from JSON file"""
    try:
        with open(DESTINATIONS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, return empty list
        return []

def get_destination_by_id(destination_id):
    """Get a specific destination by ID"""
    destinations = load_destinations()
    for destination in destinations:
        if destination['id'] == destination_id:
            return destination
    return None

def load_travel_tips():
    """Load travel tips from JSON file"""
    try:
        with open(TRAVEL_TIPS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_itineraries():
    """Load all itineraries from JSON file"""
    try:
        with open(ITINERARIES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_itinerary_by_id(itinerary_id):
    """Get a specific itinerary by ID"""
    itineraries = get_itineraries()
    for itinerary in itineraries:
        if itinerary['id'] == itinerary_id:
            return itinerary
    return None

def save_itinerary(itinerary):
    """Save a new itinerary to the JSON file"""
    itineraries = get_itineraries()
    itineraries.append(itinerary)
    with open(ITINERARIES_FILE, 'w') as f:
        json.dump(itineraries, f, indent=2)
    return True

def update_itinerary(updated_itinerary):
    """Update an existing itinerary"""
    itineraries = get_itineraries()
    for i, itinerary in enumerate(itineraries):
        if itinerary['id'] == updated_itinerary['id']:
            itineraries[i] = updated_itinerary
            with open(ITINERARIES_FILE, 'w') as f:
                json.dump(itineraries, f, indent=2)
            return True
    return False

def delete_itinerary(itinerary_id):
    """Delete an itinerary by ID"""
    itineraries = get_itineraries()
    for i, itinerary in enumerate(itineraries):
        if itinerary['id'] == itinerary_id:
            del itineraries[i]
            with open(ITINERARIES_FILE, 'w') as f:
                json.dump(itineraries, f, indent=2)
            return True
    return False
