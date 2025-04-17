import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from data import (load_destinations, get_destination_by_id, 
                 load_travel_tips, get_itineraries, save_itinerary, 
                 get_itinerary_by_id, delete_itinerary, update_itinerary)
from weather import get_weather_for_city

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
