-- BIS NOC Campus Attendance System - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    class VARCHAR(100) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    roll_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(class, roll_number)
);

-- Teachers table
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- Main, Subject, Assistant, Special
    subjects TEXT[], -- Array of subjects
    classes TEXT[], -- Array of classes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attendance records table
CREATE TABLE attendance_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    class VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    status CHAR(2) NOT NULL CHECK (status IN ('P', 'L', 'A', 'AP')),
    notes TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, date)
);

-- Daily notes table
CREATE TABLE daily_notes (
    id SERIAL PRIMARY KEY,
    class VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    text TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(class, date)
);

-- Class timetables table
CREATE TABLE class_timetables (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    day VARCHAR(20) NOT NULL CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')),
    periods JSONB NOT NULL, -- Array of period activities
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(class_name, day)
);

-- Duties table
CREATE TABLE duties (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    role VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Marksheets table
CREATE TABLE marksheets (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES teachers(id) ON DELETE CASCADE,
    class_name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL, -- quiz1, midterm, final, etc.
    score DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(teacher_id, class_name, subject, student_id, assessment_type)
);

-- Class notifications table
CREATE TABLE class_notifications (
    id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_attendance_student_date ON attendance_records(student_id, date);
CREATE INDEX idx_attendance_class_date ON attendance_records(class, date);
CREATE INDEX idx_students_class ON students(class);
CREATE INDEX idx_teachers_type ON teachers(type);
CREATE INDEX idx_duties_date ON duties(date);
CREATE INDEX idx_marksheets_teacher_class ON marksheets(teacher_id, class_name);
CREATE INDEX idx_notifications_class ON class_notifications(class_name);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_students_updated_at BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teachers_updated_at BEFORE UPDATE ON teachers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_class_timetables_updated_at BEFORE UPDATE ON class_timetables
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_marksheets_updated_at BEFORE UPDATE ON marksheets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default BIS NOC classes
INSERT INTO students (name, class, gender, roll_number) VALUES
-- This will be populated by the migration script
('Sample Student', 'Year 3 - Blue', 'M', 'BLU-01');

-- Insert sample teacher
INSERT INTO teachers (name, type, subjects, classes) VALUES
('Ms. Sample Teacher', 'Main', ARRAY['General'], ARRAY['Year 3 - Blue']);

-- Insert default timetable for all classes
INSERT INTO class_timetables (class_name, day, periods) VALUES
('Year 3 - Blue', 'Monday', '["Morning Activity, Registration (08:10-08:30)", "Lesson 1 (08:30-09:20)", "Lesson 2 (09:20-10:10)", "Recess - Snack Time (10:10-10:40)", "Lesson 3 (10:40-11:30)", "Lesson 4 (11:30-12:20)", "Lunch Time (12:20-13:10)", "Lesson 5 (13:10-14:00)", "Mini Break (14:00-14:10)", "Lesson 6 (14:10-15:00)"]'),
('Year 3 - Blue', 'Tuesday', '["Morning Activity, Registration (08:10-08:30)", "Lesson 1 (08:30-09:20)", "Lesson 2 (09:20-10:10)", "Recess - Snack Time (10:10-10:40)", "Lesson 3 (10:40-11:30)", "Lesson 4 (11:30-12:20)", "Lunch Time (12:20-13:10)", "Lesson 5 (13:10-14:00)", "Mini Break (14:00-14:10)", "Lesson 6 (14:10-15:00)"]'),
('Year 3 - Blue', 'Wednesday', '["Morning Activity, Registration (08:10-08:30)", "Lesson 1 (08:30-09:20)", "Lesson 2 (09:20-10:10)", "Recess - Snack Time (10:10-10:40)", "Lesson 3 (10:40-11:30)", "Lesson 4 (11:30-12:20)", "Lunch Time (12:20-13:10)", "Lesson 5 (13:10-14:00)", "Mini Break (14:00-14:10)", "Lesson 6 (14:10-15:00)"]'),
('Year 3 - Blue', 'Thursday', '["Morning Activity, Registration (08:10-08:30)", "Lesson 1 (08:30-09:20)", "Lesson 2 (09:20-10:10)", "Recess - Snack Time (10:10-10:40)", "Lesson 3 (10:40-11:30)", "Lesson 4 (11:30-12:20)", "Lunch Time (12:20-13:10)", "Lesson 5 (13:10-14:00)", "Mini Break (14:00-14:10)", "Lesson 6 (14:10-15:00)"]'),
('Year 3 - Blue', 'Friday', '["Morning Activity, Registration (08:10-08:30)", "Lesson 1 (08:30-09:20)", "Lesson 2 (09:20-10:10)", "Recess - Snack Time (10:10-10:40)", "Lesson 3 (10:40-11:30)", "Lesson 4 (11:30-12:20)", "Lunch Time (12:20-13:10)", "Lesson 5 (13:10-14:00)", "Mini Break (14:00-14:10)", "Lesson 6 (14:10-15:00)"]');
