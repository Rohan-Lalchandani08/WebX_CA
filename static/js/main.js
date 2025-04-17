document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle adding activities to itinerary
    const addActivityButtons = document.querySelectorAll('.add-activity-btn');
    addActivityButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dayId = this.getAttribute('data-day');
            const dayIndex = this.getAttribute('data-day-index');
            const activitiesContainer = document.querySelector(`#activities-${dayId}`);
            
            // Create new activity input row
            const activityCount = activitiesContainer.querySelectorAll('.activity-row').length;
            const newRow = document.createElement('div');
            newRow.className = 'activity-row row mb-3';
            newRow.innerHTML = `
                <div class="col-md-4">
                    <input type="text" name="activity_${dayId}_${activityCount}" class="form-control" placeholder="Activity">
                </div>
                <div class="col-md-3">
                    <input type="text" name="time_${dayId}_${activityCount}" class="form-control" placeholder="Time">
                </div>
                <div class="col-md-5">
                    <input type="text" name="notes_${dayId}_${activityCount}" class="form-control" placeholder="Notes">
                </div>
            `;
            
            activitiesContainer.appendChild(newRow);
        });
    });

    // Handle delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-itinerary-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this itinerary? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Handle search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }

    // Handle date validation in itinerary form
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    
    if (startDateInput && endDateInput) {
        // Set minimum date as today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.setAttribute('min', today);
        
        // Update end date minimum based on start date
        startDateInput.addEventListener('change', function() {
            endDateInput.setAttribute('min', this.value);
            
            // If end date is before start date, reset it
            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = this.value;
            }
        });
    }
});
