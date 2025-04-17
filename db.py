import logging
import json
import os
from datetime import datetime
from models import (User, Trip, ItineraryDay, Destination, TravelTip, Review, Expense,
                   JournalEntry, TripInvitation)
from mongo_like import mongo

# Convert datetime objects to strings for JSON serialization
def convert_dates(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# Helper function to initialize database with default data
def init_db():
    # Check if destinations collection is empty
    if mongo.db.destinations.count_documents({}) == 0:
        # Load default destinations data
        destinations_file = 'static/data/destinations.json'
        if os.path.exists(destinations_file):
            with open(destinations_file, 'r') as f:
                destinations = json.load(f)
                for dest in destinations:
                    # Convert id to _id for MongoDB
                    dest['_id'] = dest['id']
                    del dest['id']
                    mongo.db.destinations.insert_one(dest)
    
    # Check if travel tips collection is empty
    if mongo.db.travel_tips.count_documents({}) == 0:
        # Load default travel tips data
        tips_file = 'static/data/travel_tips.json'
        if os.path.exists(tips_file):
            with open(tips_file, 'r') as f:
                tips = json.load(f)
                for tip in tips:
                    # Convert id to _id for MongoDB
                    tip['_id'] = tip['id']
                    del tip['id']
                    mongo.db.travel_tips.insert_one(tip)

# User data functions
def get_user_by_id(user_id):
    user_data = mongo.db.users.find_one({"_id": user_id})
    return User.from_dict(user_data) if user_data else None

def get_user_by_email(email):
    user_data = mongo.db.users.find_one({"email": email})
    return User.from_dict(user_data) if user_data else None

def get_user_by_username(username):
    user_data = mongo.db.users.find_one({"username": username})
    return User.from_dict(user_data) if user_data else None

def create_user(user):
    user_dict = user.to_dict()
    result = mongo.db.users.insert_one(user_dict)
    return str(result.inserted_id)

def update_user(user):
    user_dict = user.to_dict()
    result = mongo.db.users.update_one({"_id": user.id}, {"$set": user_dict})
    return result.modified_count > 0

# Destination data functions
def get_all_destinations():
    destinations = list(mongo.db.destinations.find())
    for dest in destinations:
        # Convert _id back to id for consistency
        dest['id'] = str(dest['_id'])
    return destinations

def get_destination_by_id(destination_id):
    destination = mongo.db.destinations.find_one({"_id": destination_id})
    if destination:
        destination['id'] = str(destination['_id'])
    return destination

def search_destinations(query):
    # Case-insensitive search on name, country and tags
    result = mongo.db.destinations.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"country": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}}
        ]
    })
    destinations = list(result)
    for dest in destinations:
        dest['id'] = str(dest['_id'])
    return destinations

# Travel Tips functions
def get_all_travel_tips():
    tips = list(mongo.db.travel_tips.find())
    for tip in tips:
        tip['id'] = str(tip['_id'])
    return tips

def get_travel_tip_by_id(tip_id):
    tip = mongo.db.travel_tips.find_one({"_id": tip_id})
    if tip:
        tip['id'] = str(tip['_id'])
    return tip

# Trip and Itinerary functions
def get_user_trips(user_id):
    trips = list(mongo.db.trips.find({"user_id": user_id}))
    for trip in trips:
        trip['id'] = str(trip['_id'])
    return trips

def get_trip_by_id(trip_id):
    trip = mongo.db.trips.find_one({"_id": trip_id})
    if trip:
        trip['id'] = str(trip['_id'])
    return trip

def create_trip(trip):
    trip_dict = trip.to_dict()
    result = mongo.db.trips.insert_one(trip_dict)
    return str(result.inserted_id)

def update_trip(trip):
    trip_dict = trip.to_dict()
    result = mongo.db.trips.update_one({"_id": trip.id}, {"$set": trip_dict})
    return result.modified_count > 0

def delete_trip(trip_id):
    # Delete trip
    trip_result = mongo.db.trips.delete_one({"_id": trip_id})
    
    # Delete related itinerary days
    days_result = mongo.db.itinerary_days.delete_many({"trip_id": trip_id})
    
    # Delete related expenses
    expenses_result = mongo.db.expenses.delete_many({"trip_id": trip_id})
    
    return trip_result.deleted_count > 0

# Itinerary Day functions
def get_trip_days(trip_id):
    days = list(mongo.db.itinerary_days.find({"trip_id": trip_id}))
    # Sort by date
    days.sort(key=lambda x: x.get('date', ''))
    for day in days:
        day['id'] = str(day['_id'])
    return days

def get_day_by_id(day_id):
    day = mongo.db.itinerary_days.find_one({"_id": day_id})
    if day:
        day['id'] = str(day['_id'])
    return day

def create_itinerary_day(day):
    day_dict = day.to_dict()
    result = mongo.db.itinerary_days.insert_one(day_dict)
    return str(result.inserted_id)

def update_itinerary_day(day):
    day_dict = day.to_dict()
    result = mongo.db.itinerary_days.update_one({"_id": day.id}, {"$set": day_dict})
    return result.modified_count > 0

def delete_itinerary_day(day_id):
    result = mongo.db.itinerary_days.delete_one({"_id": day_id})
    return result.deleted_count > 0

# Expense tracking functions
def get_trip_expenses(trip_id):
    expenses = list(mongo.db.expenses.find({"trip_id": trip_id}))
    for expense in expenses:
        expense['id'] = str(expense['_id'])
    return expenses

def create_expense(expense):
    expense_dict = expense.to_dict()
    result = mongo.db.expenses.insert_one(expense_dict)
    return str(result.inserted_id)

def update_expense(expense):
    expense_dict = expense.to_dict()
    result = mongo.db.expenses.update_one({"_id": expense.id}, {"$set": expense_dict})
    return result.modified_count > 0

def delete_expense(expense_id):
    result = mongo.db.expenses.delete_one({"_id": expense_id})
    return result.deleted_count > 0

# Review functions
def get_destination_reviews(destination_id):
    reviews = list(mongo.db.reviews.find({"destination_id": destination_id}))
    for review in reviews:
        review['id'] = str(review['_id'])
    return reviews

def get_user_reviews(user_id):
    reviews = list(mongo.db.reviews.find({"user_id": user_id}))
    for review in reviews:
        review['id'] = str(review['_id'])
    return reviews

def create_review(review):
    review_dict = review.to_dict()
    result = mongo.db.reviews.insert_one(review_dict)
    return str(result.inserted_id)

def update_review(review):
    review_dict = review.to_dict()
    result = mongo.db.reviews.update_one({"_id": review.id}, {"$set": review_dict})
    return result.modified_count > 0

def delete_review(review_id):
    result = mongo.db.reviews.delete_one({"_id": review_id})
    return result.deleted_count > 0

# Helper functions for the existing app's compatibility
def load_destinations():
    """Load destination data from MongoDB (compatible with existing app)"""
    return get_all_destinations()

def get_itineraries():
    """Load all itineraries from MongoDB (compatible with existing app)"""
    # For now, load all trips without user filtering
    trips = list(mongo.db.trips.find())
    itineraries = []
    
    for trip in trips:
        trip['id'] = str(trip['_id'])
        # Get days for this trip
        days = get_trip_days(trip['id'])
        # Create compatible itinerary structure
        itinerary = {
            'id': trip['id'],
            'title': trip.get('title', 'Untitled Trip'),
            'destination_id': trip.get('destination_id', ''),
            'start_date': trip.get('start_date', ''),
            'end_date': trip.get('end_date', ''),
            'days': days
        }
        
        # Get destination details for name
        if 'destination_id' in trip and trip['destination_id']:
            destination = get_destination_by_id(trip['destination_id'])
            if destination:
                itinerary['destination_name'] = destination.get('name', 'Unknown')
        
        itineraries.append(itinerary)
    
    return itineraries

def get_itinerary_by_id(itinerary_id):
    """Get a specific itinerary by ID (compatible with existing app)"""
    trip = get_trip_by_id(itinerary_id)
    if not trip:
        return None
    
    # Get days for this trip
    days = get_trip_days(trip['id'])
    
    # Create compatible itinerary structure
    itinerary = {
        'id': trip['id'],
        'title': trip.get('title', 'Untitled Trip'),
        'destination_id': trip.get('destination_id', ''),
        'start_date': trip.get('start_date', ''),
        'end_date': trip.get('end_date', ''),
        'days': days
    }
    
    # Get destination details for name
    if 'destination_id' in trip and trip['destination_id']:
        destination = get_destination_by_id(trip['destination_id'])
        if destination:
            itinerary['destination_name'] = destination.get('name', 'Unknown')
    
    return itinerary

def save_itinerary(itinerary):
    """Save a new itinerary to MongoDB (compatible with existing app)"""
    # Create a Trip object
    trip = Trip(
        id=itinerary.get('id'),
        title=itinerary.get('title'),
        destination_id=itinerary.get('destination_id'),
        start_date=itinerary.get('start_date'),
        end_date=itinerary.get('end_date')
    )
    
    # Save the trip
    trip_id = create_trip(trip)
    
    # Save each day as an ItineraryDay
    for day_data in itinerary.get('days', []):
        day = ItineraryDay(
            trip_id=trip_id,
            date=day_data.get('date'),
            activities=day_data.get('activities', []),
            notes=day_data.get('notes', '')
        )
        create_itinerary_day(day)
    
    return True

def update_itinerary(updated_itinerary):
    """Update an existing itinerary (compatible with existing app)"""
    trip_id = updated_itinerary.get('id')
    
    # Update trip basic info
    trip = Trip(
        id=trip_id,
        title=updated_itinerary.get('title'),
        destination_id=updated_itinerary.get('destination_id'),
        start_date=updated_itinerary.get('start_date'),
        end_date=updated_itinerary.get('end_date')
    )
    update_trip(trip)
    
    # Delete existing days
    mongo.db.itinerary_days.delete_many({"trip_id": trip_id})
    
    # Create new days
    for day_data in updated_itinerary.get('days', []):
        day = ItineraryDay(
            trip_id=trip_id,
            date=day_data.get('date'),
            activities=day_data.get('activities', []),
            notes=day_data.get('notes', '')
        )
        create_itinerary_day(day)
    
    return True

def delete_itinerary(itinerary_id):
    """Delete an itinerary by ID (compatible with existing app)"""
    return delete_trip(itinerary_id)

def load_travel_tips():
    """Load travel tips from MongoDB (compatible with existing app)"""
    return get_all_travel_tips()

# Journal Entry functions
def get_trip_journal_entries(trip_id):
    """Get all journal entries for a trip"""
    entries = list(mongo.db.journal_entries.find({"trip_id": trip_id}))
    for entry in entries:
        entry['id'] = str(entry['_id'])
    return entries

def get_user_journal_entries(user_id):
    """Get all journal entries by a user"""
    entries = list(mongo.db.journal_entries.find({"user_id": user_id}))
    for entry in entries:
        entry['id'] = str(entry['_id'])
    return entries

def get_journal_entry_by_id(entry_id):
    """Get a specific journal entry by ID"""
    entry = mongo.db.journal_entries.find_one({"_id": entry_id})
    if entry:
        entry['id'] = str(entry['_id'])
    return entry

def create_journal_entry(entry):
    """Create a new journal entry"""
    entry_dict = entry.to_dict()
    result = mongo.db.journal_entries.insert_one(entry_dict)
    return str(result.inserted_id)

def update_journal_entry(entry):
    """Update an existing journal entry"""
    entry_dict = entry.to_dict()
    result = mongo.db.journal_entries.update_one({"_id": entry.id}, {"$set": entry_dict})
    return result.modified_count > 0

def delete_journal_entry(entry_id):
    """Delete a journal entry by ID"""
    result = mongo.db.journal_entries.delete_one({"_id": entry_id})
    return result.deleted_count > 0

# Trip Sharing & Invitation functions
def get_trip_invitations(trip_id):
    """Get all invitations for a trip"""
    invitations = list(mongo.db.invitations.find({"trip_id": trip_id}))
    for invitation in invitations:
        invitation['id'] = str(invitation['_id'])
    return invitations

def get_user_invitations(user_email):
    """Get all invitations sent to a user's email"""
    invitations = list(mongo.db.invitations.find({
        "email": user_email, 
        "status": TripInvitation.STATUS_PENDING
    }))
    for invitation in invitations:
        invitation['id'] = str(invitation['_id'])
    return invitations

def get_invitation_by_code(code):
    """Get an invitation by its unique code"""
    invitation = mongo.db.invitations.find_one({"invitation_code": code})
    if invitation:
        invitation['id'] = str(invitation['_id'])
    return invitation

def create_invitation(invitation):
    """Create a new trip invitation"""
    invitation_dict = invitation.to_dict()
    result = mongo.db.invitations.insert_one(invitation_dict)
    return str(result.inserted_id)

def update_invitation(invitation):
    """Update an existing invitation (e.g., to accept/decline)"""
    invitation_dict = invitation.to_dict()
    result = mongo.db.invitations.update_one({"_id": invitation.id}, {"$set": invitation_dict})
    return result.modified_count > 0

def get_shared_trips(user_id):
    """Get all trips shared with a user"""
    trips = list(mongo.db.trips.find({"shared_with": user_id}))
    for trip in trips:
        trip['id'] = str(trip['_id'])
    return trips

def add_user_to_shared_trip(trip_id, user_id):
    """Add a user to a trip's shared_with list"""
    result = mongo.db.trips.update_one(
        {"_id": trip_id},
        {"$addToSet": {"shared_with": user_id}}
    )
    return result.modified_count > 0

def remove_user_from_shared_trip(trip_id, user_id):
    """Remove a user from a trip's shared_with list"""
    result = mongo.db.trips.update_one(
        {"_id": trip_id},
        {"$pull": {"shared_with": user_id}}
    )
    return result.modified_count > 0