-- Create Database
CREATE DATABASE campus_events;
USE campus_events;

-- College Table
CREATE TABLE college (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User Table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    college_id INT NOT NULL,
    student_id VARCHAR(50),
    department VARCHAR(50),
    year_of_study INT,
    phone VARCHAR(15),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (college_id) REFERENCES college(id) ON DELETE CASCADE
);

-- Event Table
CREATE TABLE event (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,
    venue VARCHAR(200),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    max_participants INT,
    registration_deadline DATETIME,
    college_id INT NOT NULL,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    requires_approval BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (college_id) REFERENCES college(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES user(id) ON DELETE CASCADE
);

-- Registration Table
CREATE TABLE registration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE KEY unique_user_event_registration (user_id, event_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE
);

-- Check-in Table
CREATE TABLE check_in (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE KEY unique_user_event_checkin (user_id, event_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE
);

-- Feedback table
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_event FOREIGN KEY (event_id) REFERENCES event(id) ON DELETE CASCADE,
    CONSTRAINT unique_user_event_feedback UNIQUE (user_id, event_id)
);


-- Create Indexes for Performance
CREATE INDEX idx_user_college ON user(college_id);
CREATE INDEX idx_user_role ON user(role);
CREATE INDEX idx_event_college ON event(college_id);
CREATE INDEX idx_event_type ON event(event_type);
CREATE INDEX idx_event_start_time ON event(start_time);
CREATE INDEX idx_registration_user ON registration(user_id);
CREATE INDEX idx_registration_event ON registration(event_id);
CREATE INDEX idx_registration_status ON registration(status);
CREATE INDEX idx_checkin_user ON check_in(user_id);
CREATE INDEX idx_checkin_event ON check_in(event_id);

-- Insert Sample Data
INSERT INTO college (name, code, address) VALUES 
('Demo University', 'DEMO', '123 Campus Street, Education City'),
('Tech Institute', 'TECH', '456 Innovation Ave, Tech City'),
('State College', 'STATE', '789 Academic Blvd, College Town');

INSERT INTO user (username, email, password_hash, full_name, role, college_id, student_id, department, year_of_study, phone) VALUES 
('admin', 'admin@demo.edu', 'scrypt:32768:8:1$...', 'System Administrator', 'admin', 1, NULL, NULL, NULL, '+1234567890'),
('john_doe', 'john@demo.edu', 'scrypt:32768:8:1$...', 'John Doe', 'student', 1, 'CS2024001', 'Computer Science', 3, '+1234567891'),
('jane_smith', 'jane@demo.edu', 'scrypt:32768:8:1$...', 'Jane Smith', 'student', 1, 'EE2024002', 'Electrical Engineering', 2, '+1234567892'),
('prof_wilson', 'wilson@demo.edu', 'scrypt:32768:8:1$...', 'Dr. Wilson', 'staff', 1, NULL, 'Computer Science', NULL, '+1234567893');