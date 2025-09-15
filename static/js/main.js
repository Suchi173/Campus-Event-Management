// Main JavaScript for Campus Event Management Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.querySelector('.btn-close')) {
                alert.querySelector('.btn-close').click();
            }
        }, 5000);
    });

    // Form validation improvements
    const forms = document.querySelectorAll('form[data-validate="true"]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Real-time search functionality
    const searchInputs = document.querySelectorAll('input[data-search="true"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', debounce(function(e) {
            performSearch(e.target.value, e.target.dataset.searchTarget);
        }, 300));
    });

    // Event registration confirmation
    const registrationForms = document.querySelectorAll('form[action*="register_event"]');
    registrationForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const eventTitle = form.closest('.card').querySelector('.card-title').textContent;
            if (!confirm(`Are you sure you want to register for "${eventTitle}"?`)) {
                e.preventDefault();
            }
        });
    });

    // Auto-refresh for ongoing events (every 30 seconds)
    if (window.location.pathname.includes('/dashboard') || window.location.pathname.includes('/events')) {
        setInterval(function() {
            updateEventStatuses();
        }, 30000);
    }

    // Dynamic form field visibility
    setupDynamicFormFields();

    // Enhanced date/time input handling
    setupDateTimeInputs();

    // Progress bar animations
    animateProgressBars();

    // Loading states for buttons
    setupLoadingStates();
});

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function performSearch(query, target) {
    // Implementation for real-time search
    console.log('Searching for:', query, 'in target:', target);
    // This would typically make an AJAX request to filter results
}

function updateEventStatuses() {
    // Check for events that might have status changes
    const eventCards = document.querySelectorAll('.card[data-event-id]');
    eventCards.forEach(function(card) {
        const eventId = card.dataset.eventId;
        const startTime = card.dataset.startTime;
        const endTime = card.dataset.endTime;
        
        if (startTime && endTime) {
            const now = new Date();
            const start = new Date(startTime);
            const end = new Date(endTime);
            
            const statusElement = card.querySelector('.event-status');
            if (statusElement) {
                if (now >= start && now <= end) {
                    statusElement.innerHTML = '<span class="badge bg-info">Ongoing</span>';
                } else if (now > end) {
                    statusElement.innerHTML = '<span class="badge bg-secondary">Completed</span>';
                }
            }
        }
    });
}

function setupDynamicFormFields() {
    // Role-based field visibility in registration form
    const roleSelect = document.getElementById('role');
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const studentFields = document.getElementById('student-fields');
            const staffFields = document.getElementById('staff-fields');
            
            if (this.value === 'student') {
                if (studentFields) studentFields.style.display = 'block';
                if (staffFields) staffFields.style.display = 'none';
                
                // Make student fields required
                const requiredFields = studentFields.querySelectorAll('input[data-required-for="student"]');
                requiredFields.forEach(field => field.required = true);
            } else {
                if (studentFields) studentFields.style.display = 'none';
                if (staffFields) staffFields.style.display = 'block';
                
                // Remove required from student fields
                const studentInputs = studentFields.querySelectorAll('input');
                studentInputs.forEach(field => field.required = false);
            }
        });
        
        // Trigger on page load
        roleSelect.dispatchEvent(new Event('change'));
    }
}

function setupDateTimeInputs() {
    // Set minimum dates for datetime inputs
    const now = new Date();
    const localISOTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
                        .toISOString().slice(0, 16);
    
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateTimeInputs.forEach(function(input) {
        if (input.dataset.allowPast !== 'true') {
            input.min = localISOTime;
        }
    });

    // Event start/end time validation
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    const registrationDeadlineInput = document.getElementById('registration_deadline');

    if (startTimeInput && endTimeInput) {
        startTimeInput.addEventListener('change', function() {
            endTimeInput.min = this.value;
            if (registrationDeadlineInput) {
                registrationDeadlineInput.max = this.value;
            }
            
            // Clear end time if it's before start time
            if (endTimeInput.value && endTimeInput.value < this.value) {
                endTimeInput.value = '';
            }
        });

        endTimeInput.addEventListener('change', function() {
            if (this.value < startTimeInput.value) {
                alert('End time cannot be before start time');
                this.value = '';
            }
        });
    }
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    // Intersection Observer for progress bar animation
    if ('IntersectionObserver' in window) {
        const progressObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.style.width;
                    
                    // Animate from 0 to target width
                    progressBar.style.width = '0%';
                    progressBar.style.transition = 'width 1s ease-in-out';
                    
                    setTimeout(function() {
                        progressBar.style.width = targetWidth;
                    }, 100);
                    
                    progressObserver.unobserve(progressBar);
                }
            });
        });

        progressBars.forEach(function(bar) {
            progressObserver.observe(bar);
        });
    }
}

function setupLoadingStates() {
    // Add loading states to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.dataset.noLoading) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                submitButton.disabled = true;
                
                // Re-enable after 5 seconds as fallback
                setTimeout(function() {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 5000);
            }
        });
    });
}

// Event management functions
function confirmDeleteEvent(eventId, eventTitle) {
    if (confirm(`Are you sure you want to delete the event "${eventTitle}"? This action cannot be undone.`)) {
        // Submit delete form or make AJAX request
        const deleteForm = document.getElementById(`delete-event-${eventId}`);
        if (deleteForm) {
            deleteForm.submit();
        }
    }
}

function toggleEventStatus(eventId, currentStatus) {
    const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
    const action = newStatus === 'active' ? 'activate' : 'deactivate';
    
    if (confirm(`Are you sure you want to ${action} this event?`)) {
        // Make AJAX request to update status
        fetch(`/admin/events/${eventId}/toggle`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error updating event status');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error updating event status');
        });
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Export functions for global use
window.CampusEvents = {
    confirmDeleteEvent,
    toggleEventStatus,
    showNotification,
    debounce
};

// Service Worker registration for offline capability (if needed)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment if you want to add offline support
        // navigator.serviceWorker.register('/static/js/sw.js');
    });
}

// Analytics tracking (placeholder)
function trackEvent(eventName, eventData = {}) {
    // Placeholder for analytics tracking
    console.log('Analytics Event:', eventName, eventData);
    
    // If you're using Google Analytics, you could do:
    // gtag('event', eventName, eventData);
    
    // Or for other analytics platforms:
    // analytics.track(eventName, eventData);
}

// Track page views
trackEvent('page_view', {
    page: window.location.pathname,
    title: document.title
});

// Track button clicks for analytics
document.addEventListener('click', function(e) {
    if (e.target.matches('button, .btn, a.btn')) {
        const action = e.target.textContent.trim() || e.target.title || 'Button Click';
        trackEvent('button_click', {
            action: action,
            page: window.location.pathname
        });
    }
});
