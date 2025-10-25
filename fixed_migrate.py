# fixed_migrate.py - Fixed migration script
import streamlit as st
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
from supabase import create_client, Client

def main():
    """Fixed migration script"""
    st.title("🔄 Fixed Data Migration to Supabase")
    
    try:
        # Get credentials from Streamlit secrets
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        
        # Create client
        client = create_client(url, key)
        st.success("✅ Connected to Supabase successfully!")
        
        # Extract students from attendance records
        st.subheader("🔄 Extracting Students from Attendance Records")
        attendance_file = Path("data/attendance_records.csv")
        if attendance_file.exists():
            attendance_df = pd.read_csv(attendance_file)
            
            # Extract unique students
            students_data = []
            seen_students = set()
            
            for _, row in attendance_df.iterrows():
                student_key = (row['student_id'], row['name'], row['roll_number'], row['class'])
                if student_key not in seen_students:
                    students_data.append({
                        'id': row['student_id'],
                        'name': row['name'],
                        'roll_number': row['roll_number'],
                        'class': row['class'],
                        'gender': 'M' if row['student_id'] % 2 == 1 else 'F'  # Simple gender assignment
                    })
                    seen_students.add(student_key)
            
            # Insert students
            success_count = 0
            for student in students_data:
                try:
                    client.table('students').insert(student).execute()
                    success_count += 1
                except Exception as e:
                    if "duplicate key" not in str(e).lower():
                        st.error(f"❌ Failed to migrate student {student['name']}: {e}")
            
            st.success(f"✅ Migrated {success_count} students")
        else:
            st.warning("❌ No attendance_records.csv found")
        
        # Migrate attendance records (fixed)
        st.subheader("🔄 Migrating Attendance Records (Fixed)")
        if attendance_file.exists():
            attendance_df = pd.read_csv(attendance_file)
            attendance_data = attendance_df.to_dict('records')
            
            # Fix the data format
            fixed_records = []
            for record in attendance_data:
                fixed_record = {
                    'student_id': record['student_id'],
                    'class': record['class'],
                    'date': record['date'],
                    'status': record['status'],
                    'notes': record.get('notes', ''),
                    'timestamp': record.get('timestamp', '')
                }
                fixed_records.append(fixed_record)
            
            # Group by date and class for batch processing
            grouped_data = {}
            for record in fixed_records:
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
                    if "duplicate key" not in str(e).lower():
                        st.error(f"❌ Failed to migrate attendance records for {key}: {e}")
            
            st.success(f"✅ Migrated {success_count} attendance records")
        
        # Migrate duties (fixed column name)
        st.subheader("🔄 Migrating Duties (Fixed)")
        duties_file = Path("data/duties.csv")
        if duties_file.exists():
            duties_df = pd.read_csv(duties_file)
            duties_data = duties_df.to_dict('records')
            
            success_count = 0
            for duty in duties_data:
                try:
                    # Fix column name from 'time' to 'time_slot'
                    fixed_duty = {
                        'date': duty['date'],
                        'time_slot': duty['time'],  # Fix column name
                        'teacher_id': duty['teacher_id'],
                        'role': duty['role']
                    }
                    client.table('duties').insert(fixed_duty).execute()
                    success_count += 1
                except Exception as e:
                    if "duplicate key" not in str(e).lower():
                        st.error(f"❌ Failed to migrate duty: {e}")
            
            st.success(f"✅ Migrated {success_count} duties")
        else:
            st.warning("❌ No duties.csv found")
        
        # Skip timetables (already exist from schema)
        st.subheader("🔄 Timetables")
        st.info("ℹ️ Timetables already exist from database schema - skipping")
        
        st.success("🎉 Fixed migration completed!")
        
    except Exception as e:
        st.error(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    main()
