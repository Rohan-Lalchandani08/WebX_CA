import os
import uuid
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from config import SECRET_KEY
from weather import get_weather_for_city
from forms import (LoginForm, RegistrationForm, ResetPasswordRequestForm, 
                  ResetPasswordForm, TripForm, ActivityForm, ExpenseForm, ReviewForm)
from models import User, Trip, Expense, Review, JournalEntry, TripInvitation

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import database functions after app initialization to avoid circular imports
from db import (load_destinations, get_destination_by_id, 
               load_travel_tips, get_itineraries, save_itinerary, 
               get_itinerary_by_id, delete_itinerary, update_itinerary,
               get_user_by_id, get_user_by_email, get_user_by_username,
               create_user, update_user, get_user_trips, get_trip_expenses, 
               create_trip, update_trip, create_expense, get_user_reviews, 
               create_review, get_trip_journal_entries, get_user_journal_entries,
               get_journal_entry_by_id, create_journal_entry, update_journal_entry,
               delete_journal_entry, get_trip_invitations, get_user_invitations,
               get_invitation_by_code, create_invitation, update_invitation,
               get_shared_trips, add_user_to_shared_trip, remove_user_from_shared_trip)

@app.route('/')
def index():
    featured_destinations = load_destinations()[:4]  # Get first 4 destinations for featured section
    return render_template('index.html', featured_destinations=featured_destinations)

@app.route('/destinations')
def destinations():
    search_query = request.args.get('search', '').lower()
    all_destinations = load_destinations()
    
    if search_query:
        filtered_destinations = [dest for dest in all_destinations 
                               if search_query in dest['name'].lower() or 
                                  search_query in dest['country'].lower() or
                                  any(search_query in tag.lower() for tag in dest.get('tags', []))]
    else:
        filtered_destinations = all_destinations
        
    return render_template('destinations.html', 
                           destinations=filtered_destinations, 
                           search_query=search_query)

@app.route('/destination/<destination_id>')
def destination_detail(destination_id):
    destination = get_destination_by_id(destination_id)
    if not destination:
        flash('Destination not found', 'danger')
        return redirect(url_for('destinations'))
    
    # Get weather information for the destination
    weather = get_weather_for_city(f"{destination['name']}, {destination['country']}")
    
    return render_template('destination_detail.html', 
                          destination=destination, 
                          weather=weather)

@app.route('/itineraries')
def itineraries():
    user_itineraries = get_itineraries()
    return render_template('itinerary.html', itineraries=user_itineraries)

@app.route('/itinerary/new', methods=['GET', 'POST'])
def create_itinerary():
    if request.method == 'POST':
        title = request.form.get('title')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        destination_id = request.form.get('destination_id')
        
        if not all([title, start_date, end_date, destination_id]):
            flash('All fields are required', 'danger')
            return redirect(url_for('create_itinerary'))
        
        destination = get_destination_by_id(destination_id)
        if not destination:
            flash('Invalid destination selected', 'danger')
            return redirect(url_for('create_itinerary'))
        
        # Create a new itinerary
        new_itinerary = {
            'id': str(uuid.uuid4()),
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'destination_id': destination_id,
            'destination_name': destination['name'],
            'days': []
        }
        
        # Calculate days between start and end dates to create day entries
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days_diff = (end - start).days + 1
            
            for i in range(days_diff):
                current_date = start.replace(day=start.day + i)
                new_itinerary['days'].append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'activities': []
                })
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('create_itinerary'))
        
        save_itinerary(new_itinerary)
        flash('Itinerary created successfully', 'success')
        return redirect(url_for('edit_itinerary', itinerary_id=new_itinerary['id']))
    
    # GET request - show form
    destinations = load_destinations()
    return render_template('itinerary_edit.html', 
                          itinerary=None, 
                          destinations=destinations, 
                          is_new=True)

@app.route('/itinerary/<itinerary_id>')
def view_itinerary(itinerary_id):
    itinerary = get_itinerary_by_id(itinerary_id)
    if not itinerary:
        flash('Itinerary not found', 'danger')
        return redirect(url_for('itineraries'))
    
    destination = get_destination_by_id(itinerary['destination_id'])
    # Get weather for the destination during itinerary period
    weather = get_weather_for_city(f"{destination['name']}, {destination['country']}")
    
    return render_template('itinerary.html', 
                          itinerary=itinerary, 
                          destination=destination,
                          weather=weather,
                          view_single=True)

@app.route('/itinerary/<itinerary_id>/edit', methods=['GET', 'POST'])
def edit_itinerary(itinerary_id):
    itinerary = get_itinerary_by_id(itinerary_id)
    if not itinerary:
        flash('Itinerary not found', 'danger')
        return redirect(url_for('itineraries'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        
        # Update basic information
        itinerary['title'] = title
        
        # Update activities for each day
        for day in itinerary['days']:
            day_date = day['date']
            day['activities'] = []
            
            # Get all activities for this day from form
            i = 0
            while True:
                activity_name = request.form.get(f"activity_{day_date}_{i}")
                activity_time = request.form.get(f"time_{day_date}_{i}")
                activity_notes = request.form.get(f"notes_{day_date}_{i}")
                
                if not activity_name:
                    break
                    
                day['activities'].append({
                    'name': activity_name,
                    'time': activity_time,
                    'notes': activity_notes
                })
                i += 1
        
        update_itinerary(itinerary)
        flash('Itinerary updated successfully', 'success')
        return redirect(url_for('view_itinerary', itinerary_id=itinerary_id))
    
    # GET request - show form with existing data
    destinations = load_destinations()
    return render_template('itinerary_edit.html', 
                          itinerary=itinerary, 
                          destinations=destinations,
                          is_new=False)

@app.route('/itinerary/<itinerary_id>/delete', methods=['POST'])
def delete_itinerary_route(itinerary_id):
    if delete_itinerary(itinerary_id):
        flash('Itinerary deleted successfully', 'success')
    else:
        flash('Failed to delete itinerary', 'danger')
    return redirect(url_for('itineraries'))

@app.route('/travel-tips')
def travel_tips():
    tips = load_travel_tips()
    return render_template('travel_tips.html', tips=tips)

# API endpoint for adding activities via AJAX
@app.route('/api/itinerary/<itinerary_id>/add-activity', methods=['POST'])
def add_activity(itinerary_id):
    itinerary = get_itinerary_by_id(itinerary_id)
    if not itinerary:
        return jsonify({'success': False, 'message': 'Itinerary not found'}), 404
    
    data = request.json
    day_index = data.get('day_index')
    activity = {
        'name': data.get('name', ''),
        'time': data.get('time', ''),
        'notes': data.get('notes', '')
    }
    
    if day_index is None or day_index < 0 or day_index >= len(itinerary['days']):
        return jsonify({'success': False, 'message': 'Invalid day index'}), 400
    
    itinerary['days'][day_index]['activities'].append(activity)
    update_itinerary(itinerary)
    
    return jsonify({
        'success': True, 
        'message': 'Activity added successfully',
        'activity': activity
    })

# User Authentication Routes
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        
        flash('Login successful', 'success')
        return redirect(next_page)
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        # Create the user in the database
        create_user(user)
        
        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user:
            # Here we would generate a reset token and send email
            # For now, just show a success message
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
            return redirect(url_for('login'))
        else:
            # Don't reveal if the email exists in the system
            flash('If an account exists with that email, a password reset link has been sent.', 'info')
            return redirect(url_for('login'))
    
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Here we would validate the token and get the user
    # For now, let's just show the form
    user = None
    
    if not user:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update user's password in the database
        user.password = form.password.data
        update_user(user)
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', title='Reset Password', form=form, token=token)

# User Profile & Dashboard Routes
@app.route('/profile')
@login_required
def profile():
    # Get user's trips
    user_trips = get_user_trips(current_user.id)
    
    # Calculate trip stats
    trips_count = len(user_trips)
    
    # Get user's reviews
    user_reviews = get_user_reviews(current_user.id)
    reviews_count = len(user_reviews)
    
    # Get countries visited (unique destinations)
    countries = set()
    upcoming_trips = []
    
    for trip in user_trips:
        # Get destination details
        destination = get_destination_by_id(trip.get('destination_id'))
        if destination and 'country' in destination:
            countries.add(destination['country'])
        
        # Calculate days until trip starts
        try:
            start_date = datetime.strptime(trip.get('start_date'), '%Y-%m-%d')
            days_until = (start_date - datetime.now()).days
            trip['countdown'] = days_until
            
            # Add to upcoming trips if in the future
            if days_until >= 0:
                upcoming_trips.append(trip)
        except (ValueError, TypeError):
            trip['countdown'] = 0
    
    countries_count = len(countries)
    
    # Sort upcoming trips by start date
    upcoming_trips = sorted(upcoming_trips, key=lambda x: x.get('start_date', ''))[:3]
    
    # Get recent activities (placeholder)
    activities = []
    
    return render_template('profile.html', 
                          trips_count=trips_count,
                          reviews_count=reviews_count,
                          countries_count=countries_count,
                          upcoming_trips=upcoming_trips,
                          activities=activities)

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's trips
    user_trips = get_user_trips(current_user.id)
    
    # Process trips for dashboard display
    upcoming_trips = []
    countries = set()
    total_budget = 0
    total_days = 0
    
    for trip in user_trips:
        # Get destination details
        destination = get_destination_by_id(trip.get('destination_id'))
        if destination:
            trip['destination_name'] = destination.get('name', 'Unknown')
            if 'country' in destination:
                countries.add(destination['country'])
        
        # Calculate days until trip starts
        try:
            start_date = datetime.strptime(trip.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(trip.get('end_date'), '%Y-%m-%d')
            days_until = (start_date - datetime.now()).days
            trip_duration = (end_date - start_date).days + 1
            
            trip['countdown'] = days_until
            total_days += trip_duration
            
            # Add to upcoming trips if in the future
            if days_until >= 0:
                upcoming_trips.append(trip)
        except (ValueError, TypeError):
            trip['countdown'] = 0
        
        # Add trip budget if available
        total_budget += float(trip.get('budget', 0) or 0)
    
    # Sort upcoming trips by start date
    upcoming_trips = sorted(upcoming_trips, key=lambda x: x.get('start_date', ''))
    
    # Dashboard stats
    stats = {
        'upcoming_trips': len(upcoming_trips),
        'countries_visited': len(countries),
        'total_budget': round(total_budget, 2),
        'total_days': total_days
    }
    
    # Get recent expenses
    recent_expenses = []
    for trip in user_trips[:3]:  # Get expenses for at most 3 trips
        expenses = get_trip_expenses(trip.get('id'))
        recent_expenses.extend(expenses)
    
    # Sort expenses by date (newest first) and limit to 5
    recent_expenses = sorted(recent_expenses, 
                            key=lambda x: datetime.strptime(x.get('date', '1970-01-01'), '%Y-%m-%d'), 
                            reverse=True)[:5]
    
    # Trip types chart data (placeholder)
    trip_types = [
        {'name': 'Family', 'count': 3},
        {'name': 'Solo', 'count': 2},
        {'name': 'Couple', 'count': 1},
        {'name': 'Business', 'count': 1},
        {'name': 'Friends', 'count': 1}
    ]
    
    # Budget data for chart (placeholder)
    budget_data = [
        {'category': 'Accommodation', 'amount': 1200},
        {'category': 'Transportation', 'amount': 800},
        {'category': 'Food', 'amount': 600},
        {'category': 'Activities', 'amount': 400},
        {'category': 'Shopping', 'amount': 300},
        {'category': 'Other', 'amount': 150}
    ]
    
    # Create expense form for modal
    expense_form = ExpenseForm()
    
    return render_template('dashboard.html',
                          stats=stats,
                          upcoming_trips=upcoming_trips,
                          recent_expenses=recent_expenses,
                          trip_types=trip_types,
                          budget_data=budget_data,
                          expense_form=expense_form,
                          journal_entries=[],
                          weather_forecast=[])

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        # Create expense object
        expense = Expense(
            trip_id=request.form.get('trip_id'),
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data,
            date=form.date.data,
            currency=form.currency.data
        )
        
        # Save to database
        create_expense(expense)
        
        flash('Expense added successfully', 'success')
        return redirect(url_for('dashboard'))
    
    flash('Error adding expense. Please check your inputs.', 'danger')
    return redirect(url_for('dashboard'))

# Travel Journal Routes
@app.route('/trips/<trip_id>/journal')
@login_required
def trip_journal(trip_id):
    # Get the trip
    trip = get_trip_by_id(trip_id)
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user owns the trip or it's shared with them
    if trip.get('user_id') != current_user.id and current_user.id not in trip.get('shared_with', []):
        flash('You do not have access to this trip journal', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get the journal entries for this trip
    journal_entries = get_trip_journal_entries(trip_id)
    
    # Get the destination details
    destination = get_destination_by_id(trip.get('destination_id'))
    
    return render_template('journal.html', 
                          trip=trip,
                          destination=destination,
                          journal_entries=journal_entries)

@app.route('/trips/<trip_id>/journal/new', methods=['GET', 'POST'])
@login_required
def create_journal_entry_route(trip_id):
    # Get the trip
    trip = get_trip_by_id(trip_id)
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user owns the trip or it's shared with them
    if trip.get('user_id') != current_user.id and current_user.id not in trip.get('shared_with', []):
        flash('You do not have access to this trip journal', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        date = request.form.get('date')
        location = request.form.get('location')
        mood = request.form.get('mood')
        
        if not title or not content or not date:
            flash('Title, content and date are required', 'danger')
            return redirect(url_for('create_journal_entry_route', trip_id=trip_id))
        
        # Process image uploads (if present)
        image_urls = []
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image and image.filename:
                    # For now, just store the filename (we'd need to implement actual file upload)
                    image_urls.append(image.filename)
        
        # Create journal entry
        journal_entry = JournalEntry(
            trip_id=trip_id,
            user_id=current_user.id,
            date=date,
            title=title,
            content=content,
            location=location,
            image_urls=image_urls,
            mood=mood
        )
        
        # Save to database
        success = create_journal_entry(journal_entry)
        if success:
            flash('Journal entry created successfully', 'success')
            return redirect(url_for('trip_journal', trip_id=trip_id))
        else:
            flash('Failed to create journal entry', 'danger')
    
    # For GET request, show the form
    return render_template('journal_entry_form.html', 
                          trip=trip,
                          entry=None,
                          is_new=True)

@app.route('/journal/entry/<entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal_entry(entry_id):
    # Get the journal entry
    entry = get_journal_entry_by_id(entry_id)
    if not entry:
        flash('Journal entry not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user owns the entry
    if entry.get('user_id') != current_user.id:
        flash('You do not have permission to edit this journal entry', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get the trip
    trip = get_trip_by_id(entry.get('trip_id'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        date = request.form.get('date')
        location = request.form.get('location')
        mood = request.form.get('mood')
        
        if not title or not content or not date:
            flash('Title, content and date are required', 'danger')
            return redirect(url_for('edit_journal_entry', entry_id=entry_id))
        
        # Process image uploads (if present)
        image_urls = entry.get('image_urls', [])
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image and image.filename:
                    # For now, just store the filename (we'd need to implement actual file upload)
                    image_urls.append(image.filename)
        
        # Update journal entry
        journal_entry = JournalEntry(
            id=entry_id,
            trip_id=entry.get('trip_id'),
            user_id=current_user.id,
            date=date,
            title=title,
            content=content,
            location=location,
            image_urls=image_urls,
            mood=mood
        )
        
        # Save to database
        success = update_journal_entry(journal_entry)
        if success:
            flash('Journal entry updated successfully', 'success')
            return redirect(url_for('trip_journal', trip_id=entry.get('trip_id')))
        else:
            flash('Failed to update journal entry', 'danger')
    
    # For GET request, show the form with existing data
    return render_template('journal_entry_form.html', 
                          trip=trip,
                          entry=entry,
                          is_new=False)

@app.route('/journal/entry/<entry_id>/delete', methods=['POST'])
@login_required
def delete_journal_entry_route(entry_id):
    # Get the journal entry
    entry = get_journal_entry_by_id(entry_id)
    if not entry:
        flash('Journal entry not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user owns the entry
    if entry.get('user_id') != current_user.id:
        flash('You do not have permission to delete this journal entry', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete the entry
    trip_id = entry.get('trip_id')
    success = delete_journal_entry(entry_id)
    
    if success:
        flash('Journal entry deleted successfully', 'success')
    else:
        flash('Failed to delete journal entry', 'danger')
    
    return redirect(url_for('trip_journal', trip_id=trip_id))

@app.route('/trips/<trip_id>/journal/download')
@login_required
def download_journal(trip_id):
    # Get the trip
    trip = get_trip_by_id(trip_id)
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user owns the trip or it's shared with them
    if trip.get('user_id') != current_user.id and current_user.id not in trip.get('shared_with', []):
        flash('You do not have access to this trip journal', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get the journal entries for this trip
    journal_entries = get_trip_journal_entries(trip_id)
    
    # Get the destination details
    destination = get_destination_by_id(trip.get('destination_id'))
    
    # Generate PDF (placeholder - would require a PDF library)
    # For now, just show a formatted HTML page that could be printed
    return render_template('journal_download.html',
                          trip=trip,
                          destination=destination,
                          journal_entries=journal_entries)

# Trip Sharing and Group Planning Routes
@app.route('/trips/<trip_id>/share', methods=['GET', 'POST'])
@login_required
def share_trip(trip_id):
    # Get the trip
    trip = get_trip_by_id(trip_id)
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user owns the trip
    if trip.get('user_id') != current_user.id:
        flash('You do not have permission to share this trip', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        share_budget = request.form.get('share_budget') == 'on'
        
        if not email:
            flash('Email is required', 'danger')
            return redirect(url_for('share_trip', trip_id=trip_id))
        
        # Check if a user with this email exists
        invited_user = get_user_by_email(email)
        
        # Create invitation
        invitation = TripInvitation(
            trip_id=trip_id,
            invited_by_id=current_user.id,
            email=email,
            user_id=invited_user.id if invited_user else None
        )
        
        # Save to database
        success = create_invitation(invitation)
        
        # Update trip sharing settings
        trip_obj = Trip(
            id=trip_id,
            sharing_enabled=True,
            budget_shared=share_budget
        )
        update_trip(trip_obj)
        
        if success:
            # Here we would send an email with the invitation link
            flash(f'Invitation sent to {email}', 'success')
        else:
            flash('Failed to send invitation', 'danger')
        
        return redirect(url_for('share_trip', trip_id=trip_id))
    
    # For GET request
    # Get existing invitations for this trip
    invitations = get_trip_invitations(trip_id)
    
    # Get users who already have access
    shared_with_users = []
    for user_id in trip.get('shared_with', []):
        user = get_user_by_id(user_id)
        if user:
            shared_with_users.append(user)
    
    return render_template('share_trip.html',
                          trip=trip,
                          invitations=invitations,
                          shared_with_users=shared_with_users)

@app.route('/invitation/<invitation_id>/cancel', methods=['POST'])
@login_required
def cancel_invitation(invitation_id):
    # Get the invitation
    invitation = get_invitation_by_code(invitation_id)
    if not invitation:
        flash('Invitation not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user is the trip owner
    trip = get_trip_by_id(invitation.get('trip_id'))
    if not trip or trip.get('user_id') != current_user.id:
        flash('You do not have permission to cancel this invitation', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete the invitation
    mongo.db.invitations.delete_one({"_id": invitation_id})
    
    flash('Invitation has been cancelled', 'success')
    return redirect(url_for('share_trip', trip_id=invitation.get('trip_id')))

@app.route('/trips/<trip_id>/remove_user/<user_id>', methods=['POST'])
@login_required
def remove_user_from_shared_trip_route(trip_id, user_id):
    # Get the trip
    trip = get_trip_by_id(trip_id)
    if not trip:
        flash('Trip not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if user is the trip owner
    if trip.get('user_id') != current_user.id:
        flash('You do not have permission to remove users from this trip', 'danger')
        return redirect(url_for('dashboard'))
    
    # Remove user from shared_with list
    if remove_user_from_shared_trip(trip_id, user_id):
        flash('User has been removed from the trip', 'success')
    else:
        flash('Failed to remove user from the trip', 'danger')
    
    return redirect(url_for('share_trip', trip_id=trip_id))

@app.route('/invitations')
@login_required
def user_invitations():
    # Get invitations for the current user by email
    invitations = get_user_invitations(current_user.email)
    
    # Process invitations to show trip details
    for invitation in invitations:
        trip = get_trip_by_id(invitation.get('trip_id'))
        if trip:
            invitation['trip'] = trip
            
            # Get inviter details
            inviter = get_user_by_id(invitation.get('invited_by_id'))
            if inviter:
                invitation['inviter_name'] = inviter.username
    
    return render_template('invitations.html', invitations=invitations)

@app.route('/invitation/<code>/accept', methods=['POST'])
@login_required
def accept_invitation(code):
    # Get the invitation
    invitation = get_invitation_by_code(code)
    if not invitation:
        flash('Invitation not found or has expired', 'danger')
        return redirect(url_for('user_invitations'))
    
    # Check if the invitation is for the current user's email
    if invitation.get('email') != current_user.email:
        flash('This invitation is not for your account', 'danger')
        return redirect(url_for('user_invitations'))
    
    # Update the invitation status to accepted
    invitation_obj = TripInvitation(
        id=invitation.get('id'),
        status=TripInvitation.STATUS_ACCEPTED,
        user_id=current_user.id
    )
    update_invitation(invitation_obj)
    
    # Add user to the shared trip
    trip_id = invitation.get('trip_id')
    add_user_to_shared_trip(trip_id, current_user.id)
    
    flash('You have successfully joined the trip', 'success')
    return redirect(url_for('view_itinerary', itinerary_id=trip_id))

@app.route('/invitation/<code>/decline', methods=['POST'])
@login_required
def decline_invitation(code):
    # Get the invitation
    invitation = get_invitation_by_code(code)
    if not invitation:
        flash('Invitation not found or has expired', 'danger')
        return redirect(url_for('user_invitations'))
    
    # Check if the invitation is for the current user's email
    if invitation.get('email') != current_user.email:
        flash('This invitation is not for your account', 'danger')
        return redirect(url_for('user_invitations'))
    
    # Update the invitation status to declined
    invitation_obj = TripInvitation(
        id=invitation.get('id'),
        status=TripInvitation.STATUS_DECLINED
    )
    update_invitation(invitation_obj)
    
    flash('You have declined the trip invitation', 'info')
    return redirect(url_for('user_invitations'))

@app.route('/trips/shared')
@login_required
def shared_trips():
    # Get trips shared with the current user
    trips = get_shared_trips(current_user.id)
    
    # Process trips to include destination details
    for trip in trips:
        destination = get_destination_by_id(trip.get('destination_id'))
        if destination:
            trip['destination'] = destination
    
    return render_template('shared_trips.html', trips=trips)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
