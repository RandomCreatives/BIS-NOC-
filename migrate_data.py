# migrate_data.py - Migration using the working approach
import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
from supabase import create_client, Client

def main():
    """Migration script using Streamlit context"""
    st.title("🔄 Data Migration to Supabase")
    
    try:
        # Get credentials from Streamlit secrets
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        
        # Create client
        client = create_client(url, key)
        st.success("✅ Connected to Supabase successfully!")
        
        # Migrate students
        st.subheader("🔄 Migrating Students")
        students_file = Path("data/students.csv")
        if students_file.exists():
            students_df = pd.read_csv(students_file)
            students_data = students_df.to_dict('records')
            
            success_count = 0
            for student in students_data:
                try:
                    client.table('students').insert(student).execute()
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ Failed to migrate student {student['name']}: {e}")
            
            st.success(f"✅ Migrated {success_count} students")
        else:
            st.warning("❌ No students.csv found")
        
        # Migrate teachers
        st.subheader("🔄 Migrating Teachers")
        teachers_file = Path("data/teachers.csv")
        if teachers_file.exists():
            teachers_df = pd.read_csv(teachers_file)
            teachers_data = teachers_df.to_dict('records')
            
            success_count = 0
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
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ Failed to migrate teacher {teacher['name']}: {e}")
            
            st.success(f"✅ Migrated {success_count} teachers")
        else:
            st.warning("❌ No teachers.csv found")
        
        # Migrate attendance records
        st.subheader("🔄 Migrating Attendance Records")
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
            
            success_count = 0
            for key, records in grouped_data.items():
                try:
                    client.table('attendance_records').insert(records).execute()
                    success_count += len(records)
                except Exception as e:
                    st.error(f"❌ Failed to migrate attendance records for {key}: {e}")
            
            st.success(f"✅ Migrated {success_count} attendance records")
        else:
            st.warning("❌ No attendance_records.csv found")
        
        # Migrate timetables
        st.subheader("🔄 Migrating Timetables")
        timetables_file = Path("data/class_timetables.json")
        if timetables_file.exists():
            with open(timetables_file, 'r') as f:
                timetables_data = json.load(f)
            
            success_count = 0
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
                    success_count += len(records)
                except Exception as e:
                    st.error(f"❌ Failed to migrate timetable for {class_name}: {e}")
            
            st.success(f"✅ Migrated {success_count} timetable records")
        else:
            st.warning("❌ No class_timetables.json found")
        
        # Migrate duties
        st.subheader("🔄 Migrating Duties")
        duties_file = Path("data/duties.csv")
        if duties_file.exists():
            duties_df = pd.read_csv(duties_file)
            duties_data = duties_df.to_dict('records')
            
            success_count = 0
            for duty in duties_data:
                try:
                    client.table('duties').insert(duty).execute()
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ Failed to migrate duty: {e}")
            
            st.success(f"✅ Migrated {success_count} duties")
        else:
            st.warning("❌ No duties.csv found")
        
        st.success("🎉 Migration completed!")
        
    except Exception as e:
        st.error(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    main()
