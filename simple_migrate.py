# simple_migrate.py - Simple migration script without Streamlit
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
from supabase import create_client, Client

def migrate_data():
    """Migrate data from CSV/JSON files to Supabase"""
    print("🚀 Starting migration to Supabase...")
    
    # Supabase credentials
    url = "https://xcziqogdqkeglwflwett.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhjemlxb2dkcWtlZ2x3Zmx3ZXR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjg0OTYsImV4cCI6MjA3NjY0NDQ5Nn0.zhBzEssRxerrXZME9VsalKTolbd4V6XiYUEUpSHe334"
    
    try:
        # Create Supabase client with simple parameters
        client = create_client(url, key)
        print("✅ Connected to Supabase successfully!")
        
        # Migrate students
        print("🔄 Migrating students...")
        students_file = Path("data/students.csv")
        if students_file.exists():
            students_df = pd.read_csv(students_file)
            students_data = students_df.to_dict('records')
            
            for student in students_data:
                try:
                    client.table('students').insert(student).execute()
                    print(f"✅ Migrated student: {student['name']}")
                except Exception as e:
                    print(f"❌ Failed to migrate student {student['name']}: {e}")
        else:
            print("❌ No students.csv found")
        
        # Migrate teachers
        print("🔄 Migrating teachers...")
        teachers_file = Path("data/teachers.csv")
        if teachers_file.exists():
            teachers_df = pd.read_csv(teachers_file)
            teachers_data = teachers_df.to_dict('records')
            
            for teacher in teachers_data:
                try:
                    # Convert subjects and classes to lists
                    if 'subjects' in teacher and pd.notna(teacher['subjects']):
                        teacher['subjects'] = [s.strip() for s in str(teacher['subjects']).split(',')]
                    else:
                        teacher['subjects'] = []
                        
                    if 'classes' in teacher and pd.notna(teacher['classes']):
                        teacher['classes'] = [c.strip() for c in str(teacher['classes']).split(',')]
                    else:
                        teacher['classes'] = []
                    
                    client.table('teachers').insert(teacher).execute()
                    print(f"✅ Migrated teacher: {teacher['name']}")
                except Exception as e:
                    print(f"❌ Failed to migrate teacher {teacher['name']}: {e}")
        else:
            print("❌ No teachers.csv found")
        
        # Migrate attendance records
        print("🔄 Migrating attendance records...")
        attendance_file = Path("data/attendance_records.csv")
        if attendance_file.exists():
            attendance_df = pd.read_csv(attendance_file)
            attendance_data = attendance_df.to_dict('records')
            
            # Group by date and class for batch processing
            grouped_data = {}
            for record in attendance_data:
                key = f"{record['class']}_{record['date']}"
                if key not in grouped_data:
                    grouped_data[key] = []
                grouped_data[key].append(record)
            
            for key, records in grouped_data.items():
                try:
                    client.table('attendance_records').insert(records).execute()
                    print(f"✅ Migrated {len(records)} attendance records for {key}")
                except Exception as e:
                    print(f"❌ Failed to migrate attendance records for {key}: {e}")
        else:
            print("❌ No attendance_records.csv found")
        
        # Migrate timetables
        print("🔄 Migrating timetables...")
        timetables_file = Path("data/class_timetables.json")
        if timetables_file.exists():
            with open(timetables_file, 'r') as f:
                timetables_data = json.load(f)
            
            for class_name, timetable in timetables_data.items():
                try:
                    # Convert to the format expected by Supabase
                    records = []
                    for day, periods in timetable.items():
                        records.append({
                            'class_name': class_name,
                            'day': day,
                            'periods': periods
                        })
                    
                    client.table('class_timetables').insert(records).execute()
                    print(f"✅ Migrated timetable for {class_name}")
                except Exception as e:
                    print(f"❌ Failed to migrate timetable for {class_name}: {e}")
        else:
            print("❌ No class_timetables.json found")
        
        # Migrate duties
        print("🔄 Migrating duties...")
        duties_file = Path("data/duties.csv")
        if duties_file.exists():
            duties_df = pd.read_csv(duties_file)
            duties_data = duties_df.to_dict('records')
            
            for duty in duties_data:
                try:
                    client.table('duties').insert(duty).execute()
                    print(f"✅ Migrated duty: {duty['role']} on {duty['date']}")
                except Exception as e:
                    print(f"❌ Failed to migrate duty: {e}")
        else:
            print("❌ No duties.csv found")
        
        print("🎉 Migration completed!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_data()
