# migrate_to_supabase.py
"""
Migration script to move data from CSV/JSON files to Supabase
Run this script once to migrate your existing data
"""

import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
from utils.supabase_client import supabase_manager

def migrate_students():
    """Migrate students from CSV to Supabase"""
    print("🔄 Migrating students...")
    
    # Load existing students
    students_file = Path("data/students.csv")
    if not students_file.exists():
        print("❌ No students.csv found")
        return
    
    students_df = pd.read_csv(students_file)
    
    # Convert to list of dicts
    students_data = students_df.to_dict('records')
    
    # Insert into Supabase
    for student in students_data:
        success = supabase_manager.add_student(student)
        if success:
            print(f"✅ Migrated student: {student['name']}")
        else:
            print(f"❌ Failed to migrate student: {student['name']}")

def migrate_teachers():
    """Migrate teachers from CSV to Supabase"""
    print("🔄 Migrating teachers...")
    
    teachers_file = Path("data/teachers.csv")
    if not teachers_file.exists():
        print("❌ No teachers.csv found")
        return
    
    teachers_df = pd.read_csv(teachers_file)
    
    # Convert to list of dicts and handle list fields
    teachers_data = []
    for _, teacher in teachers_df.iterrows():
        teacher_dict = teacher.to_dict()
        
        # Convert subjects and classes from strings to lists
        if 'subjects' in teacher_dict and pd.notna(teacher_dict['subjects']):
            teacher_dict['subjects'] = [s.strip() for s in str(teacher_dict['subjects']).split(',')]
        else:
            teacher_dict['subjects'] = []
            
        if 'classes' in teacher_dict and pd.notna(teacher_dict['classes']):
            teacher_dict['classes'] = [c.strip() for c in str(teacher_dict['classes']).split(',')]
        else:
            teacher_dict['classes'] = []
        
        teachers_data.append(teacher_dict)
    
    # Insert into Supabase
    for teacher in teachers_data:
        success = supabase_manager.add_teacher(teacher)
        if success:
            print(f"✅ Migrated teacher: {teacher['name']}")
        else:
            print(f"❌ Failed to migrate teacher: {teacher['name']}")

def migrate_attendance():
    """Migrate attendance records from CSV to Supabase"""
    print("🔄 Migrating attendance records...")
    
    attendance_file = Path("data/attendance_records.csv")
    if not attendance_file.exists():
        print("❌ No attendance_records.csv found")
        return
    
    attendance_df = pd.read_csv(attendance_file)
    
    # Convert to list of dicts
    attendance_data = attendance_df.to_dict('records')
    
    # Group by date and class for batch processing
    grouped_data = {}
    for record in attendance_data:
        key = f"{record['class']}_{record['date']}"
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(record)
    
    # Insert batches into Supabase
    for key, records in grouped_data.items():
        success = supabase_manager.save_attendance_records(records)
        if success:
            print(f"✅ Migrated {len(records)} attendance records for {key}")
        else:
            print(f"❌ Failed to migrate attendance records for {key}")

def migrate_timetables():
    """Migrate timetables from JSON to Supabase"""
    print("🔄 Migrating timetables...")
    
    timetables_file = Path("data/class_timetables.json")
    if not timetables_file.exists():
        print("❌ No class_timetables.json found")
        return
    
    with open(timetables_file, 'r') as f:
        timetables_data = json.load(f)
    
    # Insert timetables into Supabase
    for class_name, timetable in timetables_data.items():
        success = supabase_manager.save_class_timetable(class_name, timetable)
        if success:
            print(f"✅ Migrated timetable for {class_name}")
        else:
            print(f"❌ Failed to migrate timetable for {class_name}")

def migrate_duties():
    """Migrate duties from CSV to Supabase"""
    print("🔄 Migrating duties...")
    
    duties_file = Path("data/duties.csv")
    if not duties_file.exists():
        print("❌ No duties.csv found")
        return
    
    duties_df = pd.read_csv(duties_file)
    
    # Convert to list of dicts
    duties_data = duties_df.to_dict('records')
    
    # Insert into Supabase
    for duty in duties_data:
        success = supabase_manager.assign_duty(duty)
        if success:
            print(f"✅ Migrated duty: {duty['role']} on {duty['date']}")
        else:
            print(f"❌ Failed to migrate duty: {duty['role']} on {duty['date']}")

def main():
    """Run the complete migration"""
    print("🚀 Starting migration to Supabase...")
    
    # Check if Supabase is connected
    if not supabase_manager.is_connected():
        print("❌ Cannot connect to Supabase. Please check your credentials.")
        return
    
    print("✅ Connected to Supabase successfully!")
    
    # Run migrations
    migrate_students()
    migrate_teachers()
    migrate_attendance()
    migrate_timetables()
    migrate_duties()
    
    print("🎉 Migration completed!")

if __name__ == "__main__":
    main()
