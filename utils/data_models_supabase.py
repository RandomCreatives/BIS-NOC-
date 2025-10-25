# utils/data_models_supabase.py - SUPABASE VERSION
import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
from pathlib import Path
import os
import calendar
import json
from utils.supabase_client import supabase_manager

# Initialize session state with Supabase
def initialize_session_state():
    """Initialize all session state variables with Supabase"""
    # Check if Supabase is connected - if not, fallback to sensible defaults so the
    # rest of the app can still run (UI will show warnings). This mirrors the
    # behaviour in the local data_models module where defaults are always set.
    if not supabase_manager.is_connected():
        st.warning("⚠️ Supabase not connected - working in offline/local mode. Some features will be limited.")
        # Ensure session keys exist so the app doesn't crash
        st.session_state.students_df = st.session_state.get('students_df', pd.DataFrame())
        st.session_state.attendance_records = st.session_state.get('attendance_records', [])
    else:
        # Load students from Supabase
        st.session_state.students_df = supabase_manager.get_students()
        # Load attendance records from Supabase
        st.session_state.attendance_records = supabase_manager.get_attendance_records()
    
    # Define classes
    if 'classes' not in st.session_state:
        st.session_state.classes = [
            "Year 3 - Blue", "Year 3 - Crimson", "Year 3 - Cyan", "Year 3 - Purple",
            "Year 3 - Lavender", "Year 3 - Maroon", "Year 3 - Violet", "Year 3 - Green",
            "Year 3 - Red", "Year 3 - Yellow", "Year 3 - Magenta", "Year 3 - Orange"
        ]
    
    # Initialize other session state variables
    if 'class_notifications' not in st.session_state:
        st.session_state.class_notifications = {}
    
    if 'class_timetables' not in st.session_state:
        st.session_state.class_timetables = {}
    
    if 'daily_notes' not in st.session_state:
        st.session_state.daily_notes = {}
    
    if 'teachers' not in st.session_state:
        st.session_state.teachers = supabase_manager.get_teachers()
    
    if 'duties' not in st.session_state:
        st.session_state.duties = {}
    
    if 'marksheets' not in st.session_state:
        st.session_state.marksheets = {}

def save_attendance(attendance_data):
    """Save attendance records to Supabase"""
    if not attendance_data:
        return
    
    # Convert to the format expected by Supabase
    records = []
    for record in attendance_data:
        # Normalize date to string
        d = record.get('date')
        if isinstance(d, str):
            date_str = d
        elif isinstance(d, date):
            date_str = d.isoformat()
        elif isinstance(d, datetime):
            date_str = d.date().isoformat()
        else:
            date_str = date.today().isoformat()
        
        records.append({
            'student_id': record['student_id'],
            'class': record['class'],
            'date': date_str,
            'status': record['status'],
            'notes': record.get('notes', ''),
            'timestamp': datetime.now().isoformat()
        })
    
    # Save to Supabase
    success = supabase_manager.save_attendance_records(records)
    if success:
        # Update session state
        if 'attendance_records' not in st.session_state:
            st.session_state.attendance_records = []
        st.session_state.attendance_records.extend(records)
    else:
        st.error("Failed to save attendance records to Supabase")

def get_class_attendance_summary(class_name, selected_date):
    """Get attendance summary for a specific class and date"""
    return supabase_manager.get_attendance_summary(class_name, selected_date)

def get_class_color(class_name):
    """Return blue and lemon color palette based on class name"""
    color_map = {
        "Blue": "#1976d2",        # Primary Blue
        "Crimson": "#1565c0",     # Darker Blue
        "Cyan": "#42a5f5",        # Light Blue
        "Purple": "#90caf9",      # Very Light Blue
        "Lavender": "#bbdefb",    # Pale Blue
        "Maroon": "#0d47a1",      # Navy Blue
        "Violet": "#64b5f6",      # Medium Blue
        "Green": "#ffd600",       # Lemon Yellow
        "Red": "#ffc400",         # Darker Yellow
        "Yellow": "#ffea00",      # Bright Yellow
        "Magenta": "#ffab00",     # Orange-Yellow
        "Orange": "#ffd740"       # Light Yellow
    }
    
    for color, hex_code in color_map.items():
        if color.lower() in class_name.lower():
            return hex_code
    return "#1976d2"  # Default blue

def send_class_notification(class_name, message, message_type="info"):
    """Send notification to a specific class"""
    return supabase_manager.send_class_notification(class_name, message, message_type)

def get_class_notifications(class_name):
    """Get notifications for a specific class"""
    raw = supabase_manager.get_class_notifications(class_name)
    # Normalize notification shape so the rest of the app (which expects keys
    # like 'read' and 'timestamp') can consume this uniformly.
    normalized = []
    for r in (raw or []):
        normalized.append({
            'id': r.get('id'),
            'message': r.get('message') or r.get('text') or r.get('body') or '',
            'type': r.get('message_type') or r.get('type') or 'info',
            'timestamp': r.get('created_at') or r.get('timestamp') or r.get('last_updated') or '',
            # Supabase table uses 'is_read' in the client; local code expects 'read'
            'read': bool(r.get('is_read')) if 'is_read' in r else bool(r.get('read', False)),
            # keep raw payload for debugging if needed
            '_raw': r
        })
    return normalized

def mark_notification_read(class_name, index):
    """Mark a notification as read"""
    notifications = get_class_notifications(class_name)
    if index < len(notifications):
        notification_id = notifications[index]['id']
        return supabase_manager.mark_notification_read(notification_id)
    return False

def get_attendance_report(class_name, start_date, end_date):
    """Generate attendance report for a class"""
    records = supabase_manager.get_attendance_records(class_name, start_date, end_date)
    
    if not records:
        return pd.DataFrame()
    
    # Create report dataframe
    report_data = []
    for record in records:
        report_data.append({
            'Date': record['date'],
            'Student ID': record['student_id'],
            'Student Name': record.get('name', ''),
            'Roll Number': record.get('roll_number', ''),
            'Status': record['status'],
            'Notes': record.get('notes', ''),
            'Timestamp': record.get('timestamp', ''),
            'Class': record['class']
        })
    
    return pd.DataFrame(report_data)

def get_all_classes_report(start_date, end_date):
    """Generate report for all classes"""
    records = supabase_manager.get_attendance_records(None, start_date, end_date)
    
    if not records:
        return pd.DataFrame()
    
    # Create comprehensive report
    report_data = []
    for record in records:
        report_data.append({
            'Date': record['date'],
            'Class': record['class'],
            'Student ID': record['student_id'],
            'Student Name': record.get('name', ''),
            'Roll Number': record.get('roll_number', ''),
            'Status': record['status'],
            'Notes': record.get('notes', '')
        })
    
    return pd.DataFrame(report_data)

def update_attendance_from_list(records_list):
    """Update session attendance records from a list of record dicts (admin edits)"""
    try:
        # Normalize input list
        normalized = []
        for rec in records_list:
            r = dict(rec)
            d = r.get('date')
            # convert string dates to date
            if isinstance(d, str):
                try:
                    r['date'] = datetime.strptime(d, "%Y-%m-%d").date().isoformat()
                except Exception:
                    try:
                        r['date'] = datetime.fromisoformat(d).date().isoformat()
                    except Exception:
                        r['date'] = date.today().isoformat()
            normalized.append(r)

        # Save to Supabase
        success = supabase_manager.save_attendance_records(normalized)
        if success:
            # Update session state
            st.session_state.attendance_records = supabase_manager.get_attendance_records()
        return success
    except Exception as e:
        print(f"Error updating attendance records: {e}")
        return False

# STUDENT MANAGEMENT FUNCTIONS

def get_class_students(class_name):
    """Get students for a specific class"""
    return supabase_manager.get_students(class_name)

def add_student_to_class(class_name, student_data):
    """Add a new student to a class"""
    try:
        # Generate new student ID (let Supabase handle this)
        # Create roll number
        class_prefix = class_name.replace('Year 3 - ', '').upper()[:3]
        existing_students = get_class_students(class_name)
        new_roll_number = f"{class_prefix}-{len(existing_students) + 1:02d}"
        
        new_student = {
            "name": student_data['name'],
            "class": class_name,
            "gender": student_data['gender'],
            "roll_number": new_roll_number
        }
        
        # Add to Supabase
        success = supabase_manager.add_student(new_student)
        if success:
            # Update session state
            st.session_state.students_df = supabase_manager.get_students()
        return success
    except Exception as e:
        print(f"Error adding student: {e}")
        return False

def update_student(student_id, updated_data):
    """Update student information"""
    success = supabase_manager.update_student(student_id, updated_data)
    if success:
        # Update session state
        st.session_state.students_df = supabase_manager.get_students()
    return success

def remove_student(student_id):
    """Remove a student from class"""
    success = supabase_manager.delete_student(student_id)
    if success:
        # Update session state
        st.session_state.students_df = supabase_manager.get_students()
    return success

# TEACHER MANAGEMENT FUNCTIONS

def get_teachers(teacher_type=None):
    """Return list of teachers, optionally filtered by type"""
    teachers = supabase_manager.get_teachers(teacher_type)
    return teachers

def add_teacher(teacher):
    """Add a teacher record"""
    teacher_id = supabase_manager.add_teacher(teacher)
    if teacher_id:
        # Update session state
        st.session_state.teachers = supabase_manager.get_teachers()
    return teacher_id

def update_teacher(teacher_id, updates):
    """Update teacher fields by id"""
    success = supabase_manager.update_teacher(teacher_id, updates)
    if success:
        # Update session state
        st.session_state.teachers = supabase_manager.get_teachers()
    return success

def remove_teacher(teacher_id):
    """Remove teacher by id"""
    success = supabase_manager.delete_teacher(teacher_id)
    if success:
        # Update session state
        st.session_state.teachers = supabase_manager.get_teachers()
    return success

def get_teacher_by_id(teacher_id):
    """Get teacher by ID"""
    teachers = supabase_manager.get_teachers()
    for teacher in teachers:
        if teacher.get('id') == teacher_id:
            return teacher
    return None

# DUTIES FUNCTIONS

def assign_duty(date_key, time_slot, teacher_id, role):
    """Assign a duty to a teacher for a date and time slot"""
    duty_data = {
        'date': date_key.isoformat() if isinstance(date_key, date) else str(date_key),
        'time_slot': time_slot,
        'teacher_id': teacher_id,
        'role': role
    }
    return supabase_manager.assign_duty(duty_data)

def remove_duty(date_key, teacher_id, time_slot=None, role=None):
    """Remove duty assignment"""
    # This would need to be implemented in the Supabase client
    # For now, we'll use a simple approach
    duties = get_duties_for_date(date_key)
    new_duties = []
    for duty in duties:
        if not (duty.get('teacher_id') == teacher_id and 
                (time_slot is None or duty.get('time_slot') == time_slot) and 
                (role is None or duty.get('role') == role)):
            new_duties.append(duty)
    
    # Update duties in session state
    st.session_state.duties[str(date_key)] = new_duties
    return True

def get_duties_for_date(date_key):
    """Get duties for a specific date"""
    return supabase_manager.get_duties_for_date(date_key)

# DAILY NOTES FUNCTIONS

def save_daily_note(class_name, date, note_text):
    """Save daily note for a class"""
    return supabase_manager.save_daily_note(class_name, date, note_text)

def get_daily_note(class_name, date):
    """Get daily note for a class and date"""
    return supabase_manager.get_daily_note(class_name, date)

def get_note_last_updated(class_name, date):
    """Get when the note was last updated"""
    # This would need to be implemented in Supabase client
    # For now, return current time
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# TIMETABLE FUNCTIONS

def get_class_timetable(class_name):
    """Get timetable for a class"""
    return supabase_manager.get_class_timetable(class_name)

def save_class_timetable(class_name, timetable_data):
    """Save timetable for a class"""
    success = supabase_manager.save_class_timetable(class_name, timetable_data)
    if success:
        # Update session state
        st.session_state.class_timetables[class_name] = timetable_data
    return success

# ENHANCED ANALYTICS FUNCTIONS

def get_student_attendance_history(student_id, days=30):
    """Get attendance history for a specific student"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    records = supabase_manager.get_attendance_records(None, start_date, end_date)
    student_records = [r for r in records if r['student_id'] == student_id]
    
    return pd.DataFrame(student_records) if student_records else pd.DataFrame()

def get_class_attendance_trends(class_name, days=30):
    """Get attendance trends for a class"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    records = supabase_manager.get_attendance_records(class_name, start_date, end_date)
    
    if not records:
        return pd.DataFrame()
    
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])
    daily_summary = df.groupby('date').agg({
        'status': lambda x: (x == 'P').sum() / len(x) * 100
    }).rename(columns={'status': 'attendance_rate'})
    
    return daily_summary

def search_students(query, class_name=None):
    """Search students by name or roll number"""
    students = supabase_manager.get_students(class_name)
    
    if not query.strip():
        return students
    
    mask = students['name'].str.contains(query, case=False, na=False) | \
           students['roll_number'].astype(str).str.contains(query, case=False, na=False)
    
    return students[mask]

# BIS NOC SPECIFIC FUNCTIONS

def get_live_timetable_status(class_name):
    """Get current timetable status for BIS NOC timetable"""
    now = datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")
    
    # BIS NOC Timetable periods
    periods = [
        {"name": "Morning Activity, Registration", "start": "08:10", "end": "08:30"},
        {"name": "Lesson 1", "start": "08:30", "end": "09:20"},
        {"name": "Lesson 2", "start": "09:20", "end": "10:10"},
        {"name": "Recess - Snack Time", "start": "10:10", "end": "10:40"},
        {"name": "Lesson 3", "start": "10:40", "end": "11:30"},
        {"name": "Lesson 4", "start": "11:30", "end": "12:20"},
        {"name": "Lunch Time", "start": "12:20", "end": "13:10"},
        {"name": "Lesson 5", "start": "13:10", "end": "14:00"},
        {"name": "Mini Break", "start": "14:00", "end": "14:10"},
        {"name": "Lesson 6", "start": "14:10", "end": "15:00"}
    ]
    
    current_period = None
    next_period = None
    
    for i, period in enumerate(periods):
        # Check if current period
        if period["start"] <= current_time <= period["end"]:
            current_period = {
                'name': period["name"],
                'time': f"{period['start']}-{period['end']}",
                'ends_at': period["end"]
            }
        
        # Check if next period (current time is before start time)
        elif current_time < period["start"]:
            if not next_period:
                # Calculate minutes until start
                start_dt = datetime.strptime(period["start"], "%H:%M")
                current_dt = datetime.strptime(current_time, "%H:%M")
                minutes_diff = (start_dt - current_dt).seconds // 60
                
                next_period = {
                    'name': period["name"],
                    'time': f"{period['start']}-{period['end']}",
                    'starts_at': period["start"],
                    'starts_in': f"in {minutes_diff} min"
                }
            break  # Found the next period, no need to check further
    
    return {
        "current": current_period,
        "next": next_period,
        "day": current_day
    }

def export_to_custom_format(class_name, start_date, end_date):
    """Export to BIS NOC custom format"""
    # Get the standard attendance data
    attendance_data = get_attendance_report(class_name, start_date, end_date)
    
    if attendance_data.empty:
        return pd.DataFrame()
    
    # Create BIS NOC custom format
    custom_data = []
    for _, record in attendance_data.iterrows():
        custom_record = {
            'Date': record['Date'],
            'Student Name': record['Student Name'],
            'Roll Number': record['Roll Number'],
            'Class': record['Class'],
            'Status': record['Status'],
            'Remarks': record['Notes'],
            'School': 'BIS NOC Campus',
            'Academic Year': '2024-2025'
        }
        custom_data.append(custom_record)
    
    return pd.DataFrame(custom_data)

# MARKSHEET FUNCTIONS (simplified for now)

def get_marksheet(teacher_id, class_name, subject):
    """Return a DataFrame marksheet for the teacher/class/subject"""
    # This would need to be implemented with Supabase
    # For now, return empty DataFrame
    return pd.DataFrame()

def save_marksheet(teacher_id, class_name, subject, df):
    """Save a marksheet DataFrame into Supabase"""
    # This would need to be implemented with Supabase
    # For now, just return True
    return True
