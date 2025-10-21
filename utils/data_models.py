# utils/data_models.py - COMPLETE UPDATED VERSION
import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
from pathlib import Path
import os
import calendar
import json

# Data file path for persistence
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ATTENDANCE_FILE = DATA_DIR / "attendance_records.csv"
STUDENTS_FILE = DATA_DIR / "students.csv"
NOTES_FILE = DATA_DIR / "daily_notes.csv"
TIMETABLES_FILE = DATA_DIR / "class_timetables.json"

def initialize_session_state():
    """Initialize all session state variables"""
    # Try to load students from disk first
    persisted_students = load_students_from_disk()
    if persisted_students is not None:
        st.session_state.students_df = persisted_students
    else:
        st.session_state.students_df = load_sample_students()
    
    if 'attendance_records' not in st.session_state:
        st.session_state.attendance_records = load_attendance_from_disk()
    
    if 'classes' not in st.session_state:
        st.session_state.classes = [
            "Year 3 - Blue", "Year 3 - Crimson", "Year 3 - Cyan", "Year 3 - Purple",
            "Year 3 - Lavender", "Year 3 - Maroon", "Year 3 - Violet", "Year 3 - Green",
            "Year 3 - Red", "Year 3 - Yellow", "Year 3 - Magenta", "Year 3 - Orange"
        ]
    
    if 'class_notifications' not in st.session_state:
        st.session_state.class_notifications = {}
    
    if 'class_timetables' not in st.session_state:
        # Try to load timetables from disk
        loaded = load_class_timetables_from_disk()
        st.session_state.class_timetables = loaded if loaded is not None else {}

    if 'daily_notes' not in st.session_state:
        st.session_state.daily_notes = load_daily_notes_from_disk()

    # Ensure data directory exists for persistence
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

def load_sample_students():
    """Create sample student data for all classes"""
    students = []
    student_names = [
        "James Smith", "Maria Garcia", "David Johnson", "Sarah Williams",
        "Michael Brown", "Emily Davis", "Daniel Miller", "Jessica Wilson",
        "Christopher Moore", "Amanda Taylor", "Matthew Anderson", "Ashley Thomas",
        "Joshua Jackson", "Stephanie White", "Andrew Harris", "Nicole Martin",
        "Joseph Thompson", "Elizabeth Martinez", "Kevin Robinson", "Megan Clark"
    ]
    
    classes = [
        "Year 3 - Blue", "Year 3 - Crimson", "Year 3 - Cyan", "Year 3 - Purple",
        "Year 3 - Lavender", "Year 3 - Maroon", "Year 3 - Violet", "Year 3 - Green",
        "Year 3 - Red", "Year 3 - Yellow", "Year 3 - Magenta", "Year 3 - Orange"
    ]
    
    student_id = 1
    for class_name in classes:
        for i, name in enumerate(student_names):
            students.append({
                "id": student_id,
                "name": name,
                "class": class_name,
                "gender": "M" if i % 2 == 0 else "F",
                "roll_number": f"{class_name[-3:]}-{i+1:02d}"
            })
            student_id += 1
    
    return pd.DataFrame(students)

def save_attendance(attendance_data):
    """Save attendance records to session state"""
    if 'attendance_records' not in st.session_state:
        st.session_state.attendance_records = []
    
    # Remove existing records for the same date and class
    if attendance_data:
        first_record = attendance_data[0]
        target_date = first_record['date']
        target_class = first_record['class']
        
        # Convert target_date to date object if it's string
        if isinstance(target_date, str):
            try:
                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except Exception:
                target_date = date.today()
        
        # Filter out existing records for this date and class
        st.session_state.attendance_records = [
            r for r in st.session_state.attendance_records 
            if not (r['class'] == target_class and r['date'] == target_date)
        ]
    
    # Add timestamp and normalize dates
    normalized = []
    for record in attendance_data:
        # Normalize date to datetime.date
        rec = dict(record)
        d = rec.get('date')
        if isinstance(d, str):
            try:
                rec['date'] = datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                try:
                    rec['date'] = datetime.fromisoformat(d).date()
                except Exception:
                    rec['date'] = date.today()
        elif isinstance(d, datetime):
            rec['date'] = d.date()
        elif d is None:
            rec['date'] = date.today()

        rec['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        normalized.append(rec)

    st.session_state.attendance_records.extend(normalized)

    # Persist to disk
    try:
        save_attendance_to_disk(st.session_state.attendance_records)
    except Exception as e:
        print(f"Could not save attendance: {e}")

def save_attendance_to_disk(records):
    """Save attendance records to CSV file for simple persistence"""
    if not records:
        return
    # Ensure data dir
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    # Convert date/datetime to ISO strings for CSV
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)
    df.to_csv(ATTENDANCE_FILE, index=False)

def load_attendance_from_disk():
    """Load attendance records from CSV if available; return list of dicts"""
    if not ATTENDANCE_FILE.exists():
        return []
    try:
        df = pd.read_csv(ATTENDANCE_FILE)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Could not load attendance: {e}")
        return []

def get_class_attendance_summary(class_name, selected_date):
    """Get attendance summary for a specific class and date"""
    if 'attendance_records' not in st.session_state:
        return {}
    
    records = st.session_state.attendance_records
    if not records:
        return {}
    
    # Filter records for the specific class and date
    class_records = [
        r for r in records 
        if r['class'] == class_name and r['date'] == selected_date
    ]
    
    if not class_records:
        return {}
    
    # Calculate summary
    status_counts = {}
    for record in class_records:
        status = record['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    total_students = len(class_records)
    present_count = status_counts.get('P', 0) + status_counts.get('L', 0)
    attendance_rate = (present_count / total_students) * 100 if total_students > 0 else 0
    
    return {
        'total_students': total_students,
        'present_count': present_count,
        'attendance_rate': round(attendance_rate, 1),
        'status_counts': status_counts
    }

def get_class_color(class_name):
    """Return blue and lemon color palette based on class name"""
    # Blue and Lemon color palette
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
    if 'class_notifications' not in st.session_state:
        st.session_state.class_notifications = {}
    
    if class_name not in st.session_state.class_notifications:
        st.session_state.class_notifications[class_name] = []
    
    notification = {
        "message": message,
        "type": message_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }
    
    st.session_state.class_notifications[class_name].append(notification)

def get_class_notifications(class_name):
    """Get notifications for a specific class"""
    if 'class_notifications' not in st.session_state:
        return []
    
    return st.session_state.class_notifications.get(class_name, [])

def mark_notification_read(class_name, index):
    """Mark a notification as read"""
    if ('class_notifications' in st.session_state and 
        class_name in st.session_state.class_notifications and
        index < len(st.session_state.class_notifications[class_name])):
        st.session_state.class_notifications[class_name][index]['read'] = True

def get_attendance_report(class_name, start_date, end_date):
    """Generate attendance report for a class"""
    if 'attendance_records' not in st.session_state:
        return pd.DataFrame()
    
    records = st.session_state.attendance_records
    class_records = [
        r for r in records 
        if r['class'] == class_name and start_date <= r['date'] <= end_date
    ]
    
    if not class_records:
        return pd.DataFrame()
    
    # Create report dataframe
    report_data = []
    for record in class_records:
        report_data.append({
            'Date': record['date'],
            'Student ID': record['student_id'],
            'Student Name': record['name'],
            'Roll Number': record['roll_number'],
            'Status': record['status'],
            'Notes': record.get('notes', ''),
            'Class': record['class']
        })
    
    return pd.DataFrame(report_data)

def get_all_classes_report(start_date, end_date):
    """Generate report for all classes"""
    if 'attendance_records' not in st.session_state:
        return pd.DataFrame()
    
    records = st.session_state.attendance_records
    filtered_records = [
        r for r in records 
        if start_date <= r['date'] <= end_date
    ]
    
    if not filtered_records:
        return pd.DataFrame()
    
    # Create comprehensive report
    report_data = []
    for record in filtered_records:
        report_data.append({
            'Date': record['date'],
            'Class': record['class'],
            'Student ID': record['student_id'],
            'Student Name': record['name'],
            'Roll Number': record['roll_number'],
            'Status': record['status'],
            'Notes': record.get('notes', '')
        })
    
    return pd.DataFrame(report_data)

# STUDENT MANAGEMENT FUNCTIONS

def get_class_students(class_name):
    """Get students for a specific class"""
    if 'students_df' not in st.session_state:
        return pd.DataFrame()
    
    return st.session_state.students_df[
        st.session_state.students_df['class'] == class_name
    ]

def add_student_to_class(class_name, student_data):
    """Add a new student to a class"""
    if 'students_df' not in st.session_state:
        return False
    
    try:
        # Generate new student ID
        max_id = st.session_state.students_df['id'].max() if not st.session_state.students_df.empty else 0
        new_id = max_id + 1
        
        # Create roll number consistent with initial dataset (last 3 chars of class name)
        class_suffix = class_name[-3:]
        existing_students = get_class_students(class_name)
        new_roll_number = f"{class_suffix}-{len(existing_students) + 1:02d}"
        
        new_student = {
            "id": new_id,
            "name": student_data['name'],
            "class": class_name,
            "gender": student_data['gender'],
            "roll_number": new_roll_number
        }
        
        # Add to dataframe
        new_df = pd.DataFrame([new_student])
        st.session_state.students_df = pd.concat([st.session_state.students_df, new_df], ignore_index=True)
        
        # Persist to disk
        save_students_to_disk()
        return True
    except Exception as e:
        print(f"Error adding student: {e}")
        return False

def update_student(student_id, updated_data):
    """Update student information"""
    if 'students_df' not in st.session_state:
        return False
    
    try:
        # Find and update student
        mask = st.session_state.students_df['id'] == student_id
        if mask.any():
            for key, value in updated_data.items():
                st.session_state.students_df.loc[mask, key] = value
            
            # Persist to disk
            save_students_to_disk()
            return True
        return False
    except Exception as e:
        print(f"Error updating student: {e}")
        return False

def remove_student(student_id):
    """Remove a student from class"""
    if 'students_df' not in st.session_state:
        return False
    
    try:
        # Remove student
        st.session_state.students_df = st.session_state.students_df[
            st.session_state.students_df['id'] != student_id
        ]
        
        # Persist to disk
        save_students_to_disk()
        return True
    except Exception as e:
        print(f"Error removing student: {e}")
        return False

def save_students_to_disk():
    """Save students data to CSV for persistence"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        st.session_state.students_df.to_csv(STUDENTS_FILE, index=False)
    except Exception as e:
        print(f"Could not save students: {e}")

def load_students_from_disk():
    """Load students from CSV if available"""
    try:
        if STUDENTS_FILE.exists():
            return pd.read_csv(STUDENTS_FILE)
    except Exception as e:
        print(f"Could not load students: {e}")
    return None

# DAILY NOTES FUNCTIONS

def save_daily_note(class_name, note_date, note_text):
    """Save daily note for a class"""
    if 'daily_notes' not in st.session_state:
        st.session_state.daily_notes = {}

    # Normalize date input to a datetime.date
    if isinstance(note_date, str):
        try:
            normalized_date = datetime.strptime(note_date, "%Y-%m-%d").date()
        except Exception:
            normalized_date = date.today()
    elif isinstance(note_date, datetime):
        normalized_date = note_date.date()
    elif isinstance(note_date, date):
        normalized_date = note_date
    else:
        normalized_date = date.today()

    key = f"{class_name}_{normalized_date.isoformat()}"
    st.session_state.daily_notes[key] = {
        "text": note_text,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "class": class_name,
        "date": normalized_date.isoformat()
    }

    # Persist to disk
    save_daily_notes_to_disk()

def get_daily_note(class_name, note_date):
    """Get daily note for a class and date"""
    if 'daily_notes' not in st.session_state:
        return ""

    # Normalize date
    if isinstance(note_date, str):
        try:
            normalized_date = datetime.strptime(note_date, "%Y-%m-%d").date()
        except Exception:
            normalized_date = date.today()
    elif isinstance(note_date, datetime):
        normalized_date = note_date.date()
    elif isinstance(note_date, date):
        normalized_date = note_date
    else:
        normalized_date = date.today()

    key = f"{class_name}_{normalized_date.isoformat()}"
    note_data = st.session_state.daily_notes.get(key, {})
    return note_data.get("text", "")

def get_note_last_updated(class_name, note_date):
    """Get when the note was last updated"""
    if 'daily_notes' not in st.session_state:
        return ""

    # Normalize date
    if isinstance(note_date, str):
        try:
            normalized_date = datetime.strptime(note_date, "%Y-%m-%d").date()
        except Exception:
            normalized_date = date.today()
    elif isinstance(note_date, datetime):
        normalized_date = note_date.date()
    elif isinstance(note_date, date):
        normalized_date = note_date
    else:
        normalized_date = date.today()

    key = f"{class_name}_{normalized_date.isoformat()}"
    note_data = st.session_state.daily_notes.get(key, {})
    return note_data.get("last_updated", "")

def save_daily_notes_to_disk():
    """Save daily notes to CSV for persistence"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if st.session_state.daily_notes:
            notes_df = pd.DataFrame.from_dict(st.session_state.daily_notes, orient='index')
            notes_df.to_csv(NOTES_FILE, index=False)
    except Exception as e:
        print(f"Could not save daily notes: {e}")

def load_daily_notes_from_disk():
    """Load daily notes from CSV if available"""
    try:
        if NOTES_FILE.exists():
            notes_df = pd.read_csv(NOTES_FILE)
            # Convert back to the expected dictionary format
            daily_notes = {}
            for _, row in notes_df.iterrows():
                key = f"{row['class']}_{row['date']}"
                daily_notes[key] = {
                    "text": row.get('text', ''),
                    "last_updated": row.get('last_updated', ''),
                    "class": row['class'],
                    "date": row['date']
                }
            return daily_notes
    except Exception as e:
        print(f"Could not load daily notes: {e}")
    return {}

# ENHANCED ANALYTICS FUNCTIONS

def get_student_attendance_history(student_id, days=30):
    """Get attendance history for a specific student"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    student_records = [
        r for r in st.session_state.attendance_records 
        if r['student_id'] == student_id and start_date <= r['date'] <= end_date
    ]
    
    return pd.DataFrame(student_records) if student_records else pd.DataFrame()

def get_class_attendance_trends(class_name, days=30):
    """Get attendance trends for a class"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    class_records = [
        r for r in st.session_state.attendance_records 
        if r['class'] == class_name and start_date <= r['date'] <= end_date
    ]
    
    if not class_records:
        return pd.DataFrame()
    
    df = pd.DataFrame(class_records)
    df['date'] = pd.to_datetime(df['date'])
    daily_summary = df.groupby('date').agg({
        'status': lambda x: (x == 'P').sum() / len(x) * 100
    }).rename(columns={'status': 'attendance_rate'})
    
    return daily_summary

def search_students(query, class_name=None):
    """Search students by name or roll number"""
    if 'students_df' not in st.session_state:
        return pd.DataFrame()
    
    students = st.session_state.students_df
    
    if class_name:
        students = students[students['class'] == class_name]
    
    if not query.strip():
        return students
    
    mask = students['name'].str.contains(query, case=False, na=False) | \
           students['roll_number'].astype(str).str.contains(query, case=False, na=False)
    
    return students[mask]

def get_student_performance_stats(student_id):
    """Get comprehensive performance stats for a student"""
    attendance_history = get_student_attendance_history(student_id, days=90)
    
    if attendance_history.empty:
        return {
            'total_days': 0,
            'present_rate': 0,
            'late_rate': 0,
            'absent_rate': 0,
            'trend': 'no_data'
        }
    
    total_days = len(attendance_history)
    present_days = len(attendance_history[attendance_history['status'] == 'P'])
    late_days = len(attendance_history[attendance_history['status'] == 'L'])
    absent_days = len(attendance_history[attendance_history['status'].isin(['A', 'AP'])])
    
    present_rate = (present_days / total_days) * 100
    late_rate = (late_days / total_days) * 100
    absent_rate = (absent_days / total_days) * 100
    
    # Calculate trend (simple: compare first half vs second half)
    if total_days >= 10:
        first_half = attendance_history.iloc[:total_days//2]
        second_half = attendance_history.iloc[total_days//2:]
        
        first_present = len(first_half[first_half['status'] == 'P']) / len(first_half) * 100
        second_present = len(second_half[second_half['status'] == 'P']) / len(second_half) * 100
        
        if second_present > first_present + 5:
            trend = 'improving'
        elif second_present < first_present - 5:
            trend = 'declining'
        else:
            trend = 'stable'
    else:
        trend = 'insufficient_data'
    
    return {
        'total_days': total_days,
        'present_rate': round(present_rate, 1),
        'late_rate': round(late_rate, 1),
        'absent_rate': round(absent_rate, 1),
        'trend': trend
    }

def get_class_summary_stats(class_name, days=30):
    """Get comprehensive summary stats for a class"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    class_records = [
        r for r in st.session_state.attendance_records 
        if r['class'] == class_name and start_date <= r['date'] <= end_date
    ]
    
    if not class_records:
        return {
            'total_records': 0,
            'average_attendance': 0,
            'best_day': None,
            'worst_day': None,
            'most_common_issue': 'none'
        }
    
    df = pd.DataFrame(class_records)
    
    # Daily attendance rates
    daily_rates = df.groupby('date').apply(
        lambda x: (x['status'] == 'P').sum() / len(x) * 100
    )
    
    # Most common non-present status
    status_counts = df[df['status'] != 'P']['status'].value_counts()
    most_common_issue = status_counts.index[0] if not status_counts.empty else 'none'
    
    return {
        'total_records': len(class_records),
        'average_attendance': round(daily_rates.mean(), 1),
        'best_day': {
            'date': daily_rates.idxmax(),
            'rate': round(daily_rates.max(), 1)
        } if not daily_rates.empty else None,
        'worst_day': {
            'date': daily_rates.idxmin(),
            'rate': round(daily_rates.min(), 1)
        } if not daily_rates.empty else None,
        'most_common_issue': most_common_issue
    }

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

# TIMETABLE FUNCTIONS

def get_class_timetable(class_name):
    """Get timetable for a class, prefer persisted per-class timetables."""
    # If timetables exist in session state use them
    if 'class_timetables' in st.session_state:
        tt = st.session_state.class_timetables.get(class_name)
        if tt:
            # If loaded from JSON it may already be a dict-of-lists
            if isinstance(tt, dict):
                return tt

    # If not in session, try loading from disk
    loaded = load_class_timetables_from_disk()
    if loaded and isinstance(loaded, dict) and class_name in loaded:
        # put it into session for faster access later
        st.session_state.class_timetables = st.session_state.get('class_timetables', {})
        st.session_state.class_timetables[class_name] = loaded[class_name]
        return loaded[class_name]

    # Fall back to default BIS NOC timetable
    default = {
        "Monday": [
            "Morning Activity, Registration (08:10-08:30)",
            "Lesson 1 (08:30-09:20)",
            "Lesson 2 (09:20-10:10)", 
            "Recess - Snack Time (10:10-10:40)",
            "Lesson 3 (10:40-11:30)",
            "Lesson 4 (11:30-12:20)",
            "Lunch Time (12:20-13:10)",
            "Lesson 5 (13:10-14:00)",
            "Mini Break (14:00-14:10)",
            "Lesson 6 (14:10-15:00)"
        ],
        "Tuesday": [
            "Morning Activity, Registration (08:10-08:30)",
            "Lesson 1 (08:30-09:20)",
            "Lesson 2 (09:20-10:10)", 
            "Recess - Snack Time (10:10-10:40)",
            "Lesson 3 (10:40-11:30)",
            "Lesson 4 (11:30-12:20)",
            "Lunch Time (12:20-13:10)",
            "Lesson 5 (13:10-14:00)",
            "Mini Break (14:00-14:10)",
            "Lesson 6 (14:10-15:00)"
        ],
        "Wednesday": [
            "Morning Activity, Registration (08:10-08:30)",
            "Lesson 1 (08:30-09:20)",
            "Lesson 2 (09:20-10:10)", 
            "Recess - Snack Time (10:10-10:40)",
            "Lesson 3 (10:40-11:30)",
            "Lesson 4 (11:30-12:20)",
            "Lunch Time (12:20-13:10)",
            "Lesson 5 (13:10-14:00)",
            "Mini Break (14:00-14:10)",
            "Lesson 6 (14:10-15:00)"
        ],
        "Thursday": [
            "Morning Activity, Registration (08:10-08:30)",
            "Lesson 1 (08:30-09:20)",
            "Lesson 2 (09:20-10:10)", 
            "Recess - Snack Time (10:10-10:40)",
            "Lesson 3 (10:40-11:30)",
            "Lesson 4 (11:30-12:20)",
            "Lunch Time (12:20-13:10)",
            "Lesson 5 (13:10-14:00)",
            "Mini Break (14:00-14:10)",
            "Lesson 6 (14:10-15:00)"
        ],
        "Friday": [
            "Morning Activity, Registration (08:10-08:30)",
            "Lesson 1 (08:30-09:20)",
            "Lesson 2 (09:20-10:10)", 
            "Recess - Snack Time (10:10-10:40)",
            "Lesson 3 (10:40-11:30)",
            "Lesson 4 (11:30-12:20)",
            "Lunch Time (12:20-13:10)",
            "Lesson 5 (13:10-14:00)",
            "Mini Break (14:00-14:10)",
            "Lesson 6 (14:10-15:00)"
        ]
    }
    return default

def save_class_timetable(class_name, timetable_data):
    """Save timetable for a class"""
    if 'class_timetables' not in st.session_state:
        st.session_state.class_timetables = {}
    st.session_state.class_timetables[class_name] = timetable_data

    # Persist timetables to disk
    try:
        save_class_timetables_to_disk()
    except Exception as e:
        print(f"Could not persist class timetables: {e}")

def get_default_timetable(class_name):
    """Return default timetable for a class"""
    return get_class_timetable(class_name)  # Use BIS NOC timetable


def save_class_timetables_to_disk():
    """Persist all class timetables to a JSON file"""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Convert any non-serializable types (dates etc) to strings if needed
        to_save = st.session_state.get('class_timetables', {})
        with open(TIMETABLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving timetables to disk: {e}")


def load_class_timetables_from_disk():
    """Load class timetables from JSON file if available"""
    try:
        if TIMETABLES_FILE.exists():
            with open(TIMETABLES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading timetables from disk: {e}")
    return None

# UTILITY FUNCTIONS

def get_recent_attendance_dates(class_name, limit=5):
    """Get recent dates when attendance was taken for a class"""
    if 'attendance_records' not in st.session_state:
        return []
    
    class_dates = set()
    for record in st.session_state.attendance_records:
        if record['class'] == class_name:
            class_dates.add(record['date'])
    
    # Sort dates descending and return limited number
    sorted_dates = sorted(class_dates, reverse=True)
    return sorted_dates[:limit]

def export_class_data(class_name, start_date, end_date):
    """Export comprehensive class data for reporting"""
    attendance_data = get_attendance_report(class_name, start_date, end_date)
    students_data = get_class_students(class_name)
    
    return {
        'attendance': attendance_data,
        'students': students_data,
        'summary': get_class_summary_stats(class_name, days=(end_date - start_date).days)
    }

def generate_monthly_report(month, year):
    """Generate comprehensive monthly report"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year+1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month+1, 1) - timedelta(days=1)
    
    # Generate report data
    monthly_data = get_all_classes_report(start_date, end_date)
    
    # Create monthly reports directory
    reports_dir = DATA_DIR / "monthly_reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Save the report
    report_filename = f"monthly_report_{year}_{month:02d}.csv"
    report_path = reports_dir / report_filename
    monthly_data.to_csv(report_path, index=False)
    
    return report_path

def get_available_monthly_reports():
    """Get list of available monthly reports"""
    reports_dir = DATA_DIR / "monthly_reports"
    if not reports_dir.exists():
        return []
    
    reports = []
    for file_path in reports_dir.glob("monthly_report_*.csv"):
        filename = file_path.name
        # Extract year and month from filename
        parts = filename.replace('monthly_report_', '').replace('.csv', '').split('_')
        if len(parts) == 2:
            year, month = int(parts[0]), int(parts[1])
            reports.append({
                'filename': filename,
                'year': year,
                'month': month,
                'file_path': file_path,
                'display_name': f"{date(year, month, 1).strftime('%B %Y')}"
            })
    
    return sorted(reports, key=lambda x: (x['year'], x['month']), reverse=True)

