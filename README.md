# Campus Event Management System

## Goals & Scope
A minimal, production-readable slice for event reporting on a multi-tenant Campus Event Platform used by ~50 colleges, each with ~500 students and ~20 events per semester.

Scope for this prototype:
- Track event creation, student registration, attendance (check-in), and feedback (1–5 rating).
- Provide reporting APIs/queries:
  - Event popularity (registrations)
  - Attendance percentage
  - Average feedback score
  - Student participation (# events attended)
  - Top N most active students
  - Flexible filters (by college, event type)

## Overview
A complete web application built on Flask for overseeing campus events at various colleges. The system offers role-specific access for administrators, staff members, and students to organize, manage, and engage in diverse campus activities such as hackathons, workshops, tech talks, festivals, and seminars. The platform includes features for event registration, check-in monitoring, reporting functionality, and a sleek dark-themed user interface designed with Bootstrap.

## Tech Stack
- Backend: Flask(Python)
- DataBase: MySQL Workbench

## Data to Track
- **Event** creation & metadata (type, time window, capacity, status)
- **Student Registration** per event
- **Attendance** (day-of check-in)
- **Feedback** (rating 1–5, optional comment)

## Features
- Create and list events
- Register students for events
- Mark Attendance
- Submit Feedback
- Reports:
  - Event popularity
  - Attendance percentage
  - Student participation
  - Top 3 most active students

## Setup Instructions
1. Clone Repository
2. Setup database in MySQL Workbench
3. Create virtual environment
4. Install dependencies
5. Run Flask Server
   - python main.py
   - Flask will start at: http://127.0.0.1:5000/





