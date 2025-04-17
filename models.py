from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# User model for authentication
class User(UserMixin):
    def __init__(self, id=None, username=None, email=None, password=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = created_at or datetime.utcnow()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }

# Trip model for user trips
class Trip:
    def __init__(self, id=None, title=None, user_id=None, destination_id=None, 
                 start_date=None, end_date=None, budget=None, notes=None, 
                 created_at=None, is_public=False, companions=None, 
                 shared_with=None, sharing_enabled=False, budget_shared=False):
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.user_id = user_id
        self.destination_id = destination_id
        self.start_date = start_date
        self.end_date = end_date
        self.budget = budget
        self.notes = notes
        self.created_at = created_at or datetime.utcnow()
        self.is_public = is_public
        self.companions = companions or []
        self.shared_with = shared_with or []  # List of user IDs who have access
        self.sharing_enabled = sharing_enabled  # Enable group planning
        self.budget_shared = budget_shared  # Whether budget is shared with group
        
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            title=data.get('title'),
            user_id=data.get('user_id'),
            destination_id=data.get('destination_id'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            budget=data.get('budget'),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            is_public=data.get('is_public', False),
            companions=data.get('companions', []),
            shared_with=data.get('shared_with', []),
            sharing_enabled=data.get('sharing_enabled', False),
            budget_shared=data.get('budget_shared', False)
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'title': self.title,
            'user_id': self.user_id,
            'destination_id': self.destination_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'budget': self.budget,
            'notes': self.notes,
            'created_at': self.created_at,
            'is_public': self.is_public,
            'companions': self.companions,
            'shared_with': self.shared_with,
            'sharing_enabled': self.sharing_enabled,
            'budget_shared': self.budget_shared
        }

# Itinerary day model
class ItineraryDay:
    def __init__(self, id=None, trip_id=None, date=None, activities=None, notes=None):
        self.id = id or str(uuid.uuid4())
        self.trip_id = trip_id
        self.date = date
        self.activities = activities or []
        self.notes = notes
        
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            trip_id=data.get('trip_id'),
            date=data.get('date'),
            activities=data.get('activities', []),
            notes=data.get('notes')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'trip_id': self.trip_id,
            'date': self.date,
            'activities': self.activities,
            'notes': self.notes
        }

# Activity model for itinerary days
class Activity:
    def __init__(self, id=None, name=None, time=None, location=None, notes=None, cost=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.time = time
        self.location = location
        self.notes = notes
        self.cost = cost
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'time': self.time,
            'location': self.location,
            'notes': self.notes,
            'cost': self.cost
        }

# Expense model for trip budget tracking
class Expense:
    def __init__(self, id=None, trip_id=None, amount=None, category=None, 
                 description=None, date=None, currency=None):
        self.id = id or str(uuid.uuid4())
        self.trip_id = trip_id
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date or datetime.utcnow()
        self.currency = currency or 'USD'
        
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            trip_id=data.get('trip_id'),
            amount=data.get('amount'),
            category=data.get('category'),
            description=data.get('description'),
            date=data.get('date'),
            currency=data.get('currency', 'USD')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'trip_id': self.trip_id,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date,
            'currency': self.currency
        }

# Destination model
class Destination:
    def __init__(self, id=None, name=None, country=None, description=None, 
                image_url=None, attractions=None, tags=None, best_time_to_visit=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.country = country
        self.description = description
        self.image_url = image_url
        self.attractions = attractions or []
        self.tags = tags or []
        self.best_time_to_visit = best_time_to_visit
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            name=data.get('name'),
            country=data.get('country'),
            description=data.get('description'),
            image_url=data.get('image_url'),
            attractions=data.get('attractions', []),
            tags=data.get('tags', []),
            best_time_to_visit=data.get('best_time_to_visit')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'name': self.name,
            'country': self.country,
            'description': self.description,
            'image_url': self.image_url,
            'attractions': self.attractions,
            'tags': self.tags,
            'best_time_to_visit': self.best_time_to_visit
        }

# TravelTip model
class TravelTip:
    def __init__(self, id=None, category=None, title=None, tips=None):
        self.id = id or str(uuid.uuid4())
        self.category = category
        self.title = title
        self.tips = tips or []
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            category=data.get('category'),
            title=data.get('title'),
            tips=data.get('tips', [])
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'category': self.category,
            'title': self.title,
            'tips': self.tips
        }

# User Review model
class Review:
    def __init__(self, id=None, user_id=None, destination_id=None, rating=None, 
                 comment=None, date=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.destination_id = destination_id
        self.rating = rating
        self.comment = comment
        self.date = date or datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            user_id=data.get('user_id'),
            destination_id=data.get('destination_id'),
            rating=data.get('rating'),
            comment=data.get('comment'),
            date=data.get('date')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'user_id': self.user_id,
            'destination_id': self.destination_id,
            'rating': self.rating,
            'comment': self.comment,
            'date': self.date
        }

# Travel Journal Entry model
class JournalEntry:
    def __init__(self, id=None, trip_id=None, user_id=None, date=None, title=None,
                content=None, location=None, image_urls=None, mood=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.trip_id = trip_id
        self.user_id = user_id
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.title = title
        self.content = content
        self.location = location
        self.image_urls = image_urls or []
        self.mood = mood
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            trip_id=data.get('trip_id'),
            user_id=data.get('user_id'),
            date=data.get('date'),
            title=data.get('title'),
            content=data.get('content'),
            location=data.get('location'),
            image_urls=data.get('image_urls', []),
            mood=data.get('mood'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'trip_id': self.trip_id,
            'user_id': self.user_id,
            'date': self.date,
            'title': self.title,
            'content': self.content,
            'location': self.location,
            'image_urls': self.image_urls,
            'mood': self.mood,
            'created_at': self.created_at
        }

# Trip Invitation model
class TripInvitation:
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    
    def __init__(self, id=None, trip_id=None, user_id=None, invited_by_id=None, 
                email=None, status=None, invitation_code=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.trip_id = trip_id
        self.user_id = user_id  # Will be None until accepted
        self.invited_by_id = invited_by_id
        self.email = email
        self.status = status or self.STATUS_PENDING
        self.invitation_code = invitation_code or str(uuid.uuid4())
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data):
        if not data:
            return None
        return cls(
            id=data.get('_id') or data.get('id'),
            trip_id=data.get('trip_id'),
            user_id=data.get('user_id'),
            invited_by_id=data.get('invited_by_id'),
            email=data.get('email'),
            status=data.get('status'),
            invitation_code=data.get('invitation_code'),
            created_at=data.get('created_at')
        )
    
    def to_dict(self):
        return {
            '_id': self.id,
            'trip_id': self.trip_id,
            'user_id': self.user_id,
            'invited_by_id': self.invited_by_id,
            'email': self.email,
            'status': self.status,
            'invitation_code': self.invitation_code,
            'created_at': self.created_at
        }