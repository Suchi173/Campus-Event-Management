from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc, or_
from datetime import datetime, timedelta
from app import app, db
from models import Feedback, User, College, Event, Registration, CheckIn

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin' or current_user.role == 'staff':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role in ['admin', 'staff']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        role = request.form.get('role', 'student')
        college_id = request.form['college_id']
        student_id = request.form.get('student_id')
        department = request.form.get('department')
        year_of_study = request.form.get('year_of_study')
        phone = request.form.get('phone')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html', colleges=College.query.all())
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html', colleges=College.query.all())
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role,
            college_id=college_id,
            student_id=student_id,
            department=department,
            year_of_study=int(year_of_study) if year_of_study else None,
            phone=phone
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    colleges = College.query.all()
    return render_template('register.html', colleges=colleges)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Get statistics for the current college
    total_events = Event.query.filter_by(college_id=current_user.college_id).count()
    total_students = User.query.filter_by(college_id=current_user.college_id, role='student').count()
    
    # Recent events
    recent_events = Event.query.filter_by(college_id=current_user.college_id)\
                              .order_by(desc(Event.created_at)).limit(5).all()
    
    # Upcoming events
    upcoming_events = Event.query.filter(
        Event.college_id == current_user.college_id,
        Event.start_time > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.start_time).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         total_events=total_events,
                         total_students=total_students,
                         recent_events=recent_events,
                         upcoming_events=upcoming_events)

@app.route('/admin/events')
@login_required
def manage_events():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied', 'error')
        return redirect(url_for('student_dashboard'))
    
    page = request.args.get('page', 1, type=int)
    events = Event.query.filter_by(college_id=current_user.college_id)\
                       .order_by(desc(Event.created_at))\
                       .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('admin/manage_events.html', events=events)

@app.route('/admin/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied', 'error')
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_type = request.form['event_type']
        venue = request.form['venue']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        max_participants = request.form.get('max_participants')
        registration_deadline = request.form.get('registration_deadline')
        
        if registration_deadline:
            registration_deadline = datetime.strptime(registration_deadline, '%Y-%m-%dT%H:%M')
        
        event = Event(
            title=title,
            description=description,
            event_type=event_type,
            venue=venue,
            start_time=start_time,
            end_time=end_time,
            max_participants=int(max_participants) if max_participants else None,
            registration_deadline=registration_deadline,
            college_id=current_user.college_id,
            created_by=current_user.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('manage_events'))
    
    return render_template('admin/create_event.html')

@app.route('/admin/reports')
@login_required
def reports():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Get filter parameters
    event_type = request.args.get('event_type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Base query for events in current college
    base_query = Event.query.filter_by(college_id=current_user.college_id)
    
    # Apply filters
    if event_type:
        base_query = base_query.filter_by(event_type=event_type)
    
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        base_query = base_query.filter(Event.start_time >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        base_query = base_query.filter(Event.start_time <= end_dt)
    
    events = base_query.all()
    
    # Top 3 Most Active Students
    top_students = db.session.query(
        User.id,
        User.full_name,
        User.student_id,
        func.count(Registration.id).label('registration_count'),
        func.count(CheckIn.id).label('checkin_count')
    ).join(Registration, Registration.user_id == User.id)\
     .outerjoin(CheckIn, CheckIn.user_id == User.id)\
     .filter(User.college_id == current_user.college_id)\
     .filter(User.role == 'student')\
     .group_by(User.id)\
     .order_by(desc('registration_count'), desc('checkin_count'))\
     .limit(3).all()
    
    # Event type statistics
    event_type_stats = db.session.query(
        Event.event_type,
        func.count(Event.id).label('event_count'),
        func.count(Registration.id).label('total_registrations')
    ).outerjoin(Registration, Registration.event_id == Event.id)\
     .filter(Event.college_id == current_user.college_id)\
     .group_by(Event.event_type).all()
    
    # Event types for filter dropdown
    event_types = db.session.query(Event.event_type).distinct()\
                           .filter_by(college_id=current_user.college_id).all()
    event_types = [et[0] for et in event_types]
    
    return render_template('admin/reports.html',
                         events=events,
                         top_students=top_students,
                         event_type_stats=event_type_stats,
                         event_types=event_types,
                         current_filters={
                             'event_type': event_type,
                             'start_date': start_date,
                             'end_date': end_date
                         })

# Student Routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role not in ['student']:
        flash('Access denied', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Upcoming events
    upcoming_events = Event.query.filter(
        Event.college_id == current_user.college_id,
        Event.start_time > datetime.utcnow(),
        Event.is_active == True
    ).order_by(Event.start_time).limit(5).all()
    
    # My recent registrations
    my_registrations = Registration.query.filter_by(user_id=current_user.id)\
                                        .order_by(desc(Registration.registered_at))\
                                        .limit(5).all()
    
    return render_template('student/dashboard.html',
                         upcoming_events=upcoming_events,
                         my_registrations=my_registrations)

@app.route('/student/events')
@login_required
def browse_events():
    if current_user.role not in ['student']:
        flash('Access denied', 'error')
        return redirect(url_for('admin_dashboard'))
    
    page = request.args.get('page', 1, type=int)
    event_type = request.args.get('event_type', '')
    
    # Base query for events in current college
    query = Event.query.filter(
        Event.college_id == current_user.college_id,
        Event.is_active == True
    )
    
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    events = query.order_by(Event.start_time).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get event types for filter
    event_types = db.session.query(Event.event_type).distinct()\
                           .filter_by(college_id=current_user.college_id).all()
    event_types = [et[0] for et in event_types]
    
    # Get user's registrations
    user_registrations = {r.event_id: r.status for r in 
                         Registration.query.filter_by(user_id=current_user.id).all()}
    
    return render_template('student/events.html',
                         events=events,
                         event_types=event_types,
                         current_filter=event_type,
                         user_registrations=user_registrations)

@app.route('/student/my_events')
@login_required
def my_events():
    if current_user.role not in ['student']:
        flash('Access denied', 'error')
        return redirect(url_for('admin_dashboard'))
    
    registrations = Registration.query.filter_by(user_id=current_user.id)\
                                    .order_by(desc(Registration.registered_at)).all()
    
    return render_template('student/my_events.html', registrations=registrations)

@app.route('/register_event/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    if current_user.role not in ['student']:
        flash('Access denied', 'error')
        return redirect(url_for('admin_dashboard'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if event belongs to user's college
    if event.college_id != current_user.college_id:
        flash('Access denied', 'error')
        return redirect(url_for('browse_events'))
    
    # Check if registration is open
    if not event.is_registration_open:
        flash('Registration is closed for this event', 'error')
        return redirect(url_for('browse_events'))
    
    # Check if already registered
    existing_registration = Registration.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this event', 'warning')
        return redirect(url_for('browse_events'))
    
    # Check capacity
    if event.max_participants:
        current_count = event.registration_count
        if current_count >= event.max_participants:
            flash('Event is full', 'error')
            return redirect(url_for('browse_events'))
    
    # Create registration
    registration = Registration(
        user_id=current_user.id,
        event_id=event_id,
        status='confirmed'
    )
    
    db.session.add(registration)
    db.session.commit()
    
    flash('Successfully registered for the event!', 'success')
    return redirect(url_for('browse_events'))

@app.route('/cancel_registration/<int:event_id>', methods=['POST'])
@login_required
def cancel_registration(event_id):
    registration = Registration.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first_or_404()
    
    registration.status = 'cancelled'
    db.session.commit()
    
    flash('Registration cancelled successfully', 'info')
    return redirect(url_for('my_events'))

@app.route('/checkin/<int:event_id>', methods=['POST'])
@login_required
def checkin_event(event_id):
    # Check if user is registered for the event
    registration = Registration.query.filter_by(
        user_id=current_user.id, 
        event_id=event_id, 
        status='confirmed'
    ).first()
    
    if not registration:
        flash('You must be registered for this event to check in', 'error')
        return redirect(url_for('my_events'))
    
    # Check if already checked in
    existing_checkin = CheckIn.query.filter_by(
        user_id=current_user.id, event_id=event_id
    ).first()
    
    if existing_checkin:
        flash('You have already checked in for this event', 'warning')
        return redirect(url_for('my_events'))
    
    # Create check-in
    checkin = CheckIn(
        user_id=current_user.id,
        event_id=event_id
    )
    
    db.session.add(checkin)
    db.session.commit()
    
    flash('Successfully checked in!', 'success')
    return redirect(url_for('my_events'))

@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()
    user_id = data.get('user_id')
    event_id = data.get('event_id')
    notes = data.get('notes')

    # Check if user and event exist
    user = User.query.get(user_id)
    event = Event.query.get(event_id)
    if not user or not event:
        return jsonify({"error": "User or Event not found"}), 404

    # Prevent duplicate check-in
    existing = CheckIn.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        return jsonify({"error": "User already checked in"}), 400

    checkin = CheckIn(user_id=user_id, event_id=event_id, notes=notes)
    db.session.add(checkin)
    db.session.commit()

    return jsonify({
        "message": "Check-in successful",
        "user": user.full_name,
        "event": event.title,
        "time": checkin.check_in_time.strftime("%Y-%m-%d %H:%M:%S")
    }), 201

# ------------------ Feedback Routes ------------------
@app.route('/event/<int:event_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(event_id):
    event = Event.query.get_or_404(event_id)

    if current_user.role != 'student':
        flash('Only students can submit feedback.', 'error')
        return redirect(url_for('my_events'))

    checkin = CheckIn.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not checkin:
        flash('You must check in before submitting feedback.', 'error')
        return redirect(url_for('my_events'))

    existing_feedback = Feedback.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing_feedback:
        flash('You already submitted feedback for this event.', 'warning')
        return redirect(url_for('my_events'))

    rating = int(request.form.get('rating'))
    comment = request.form.get('comment', '')

    feedback = Feedback(user_id=current_user.id, event_id=event_id, rating=rating, comment=comment)
    db.session.add(feedback)
    db.session.commit()
    
@app.route('/event/<int:event_id>/feedback', methods=['GET'])
def get_feedback(event_id):
    event = Event.query.get_or_404(event_id)
    
    feedbacks = Feedback.query.filter_by(event_id=event_id).all()
    result = []
    for f in feedbacks:
        result.append({
            "student_name": f.user.full_name,
            "student_id": f.user.student_id,
            "rating": f.rating,
            "comment": f.comment,
            "submitted_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return jsonify({
        "event": event.title,
        "feedbacks": result
    })

@app.route('/event/<int:event_id>/registrations', methods=['GET'])
def get_total_registrations(event_id):
    event = Event.query.get_or_404(event_id)
    
    total_registrations = Registration.query.filter_by(event_id=event_id).count()
    
    # Optional: get detailed list of students
    registrations = Registration.query.filter_by(event_id=event_id).all()
    students = []
    for r in registrations:
        students.append({
            "student_name": r.user.full_name,
            "student_id": r.user.student_id,
            "status": r.status,
            "registered_at": r.registered_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return jsonify({
        "event": event.title,
        "total_registrations": total_registrations,
        "students": students
    })

@app.route('/report/top_students', methods=['GET'])
def get_top_students():
    # Optional: filter by college_id via query param
    college_id = request.args.get('college_id', type=int)

    query = db.session.query(
        User.id,
        User.full_name,
        User.student_id,
        func.count(Registration.id).label('registration_count'),
        func.count(CheckIn.id).label('checkin_count')
    ).join(Registration, Registration.user_id == User.id)\
     .outerjoin(CheckIn, CheckIn.user_id == User.id)\
     .filter(User.role == 'student')

    if college_id:
        query = query.filter(User.college_id == college_id)
    
    top_students = query.group_by(User.id)\
                        .order_by(desc('registration_count'), desc('checkin_count'))\
                        .limit(5).all()  # Top 5 students
    
    result = []
    for s in top_students:
        result.append({
            "student_name": s.full_name,
            "student_id": s.student_id,
            "registration_count": s.registration_count,
            "checkin_count": s.checkin_count
        })
    
    return jsonify({"top_students": result})


@app.route('/report/registrations')
@login_required
def report_registrations():
    if current_user.role not in ['admin', 'staff']:
        return jsonify({"error": "Access denied"}), 403

    # Get all registrations for this college
    registrations = db.session.query(
        Registration.id,
        User.full_name,
        User.student_id,
        Event.title,
        Registration.status,
        Registration.registered_at
    ).join(User, User.id == Registration.user_id) \
     .join(Event, Event.id == Registration.event_id) \
     .filter(User.college_id == current_user.college_id) \
     .all()

    result = []
    for r in registrations:
        result.append({
            "registration_id": r.id,
            "student_name": r.full_name,
            "student_id": r.student_id,
            "event_title": r.title,
            "status": r.status,
            "registered_at": r.registered_at.strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(result)

# Attendance Report Route
@app.route('/report/attendance/<int:event_id>')
def report_attendance(event_id):
    checkins = CheckIn.query.filter_by(event_id=event_id).all()
    data = [
        {
            "user": c.user.full_name,
            "check_in_time": c.check_in_time.strftime("%Y-%m-%d %H:%M:%S"),
            "notes": c.notes
        }
        for c in checkins
    ]
    return jsonify(data)



@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.context_processor
def utility_processor():
    def format_datetime(dt):
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M')
        return ''
    
    def format_date(dt):
        if dt:
            return dt.strftime('%Y-%m-%d')
        return ''
    
    return dict(format_datetime=format_datetime, format_date=format_date)
