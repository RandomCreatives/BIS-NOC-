# utils/supabase_client.py
import os
import streamlit as st
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime, date

class SupabaseManager:
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client with credentials"""
        try:
            # Get credentials from environment variables or Streamlit secrets
            url = os.getenv("SUPABASE_URL") or st.secrets.get("supabase.url")
            key = os.getenv("SUPABASE_ANON_KEY") or st.secrets.get("supabase.anon_key")
            
            if not url or not key:
                st.error("❌ Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY in your environment or Streamlit secrets.")
                return
            
            # Create client with simple parameters
            self.client = create_client(url, key)
            st.success("✅ Connected to Supabase successfully!")
            
        except Exception as e:
            st.error(f"❌ Failed to connect to Supabase: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase client is connected"""
        return self.client is not None
    
    # STUDENTS OPERATIONS
    def get_students(self, class_name: Optional[str] = None) -> pd.DataFrame:
        """Get all students or students from a specific class"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            if class_name:
                response = self.client.table('students').select('*').eq('class', class_name).execute()
            else:
                response = self.client.table('students').select('*').execute()
            
            return pd.DataFrame(response.data)
        except Exception as e:
            st.error(f"Error fetching students: {e}")
            return pd.DataFrame()
    
    def add_student(self, student_data: Dict[str, Any]) -> bool:
        """Add a new student"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('students').insert(student_data).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error adding student: {e}")
            return False
    
    def update_student(self, student_id: int, updates: Dict[str, Any]) -> bool:
        """Update student information"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('students').update(updates).eq('id', student_id).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error updating student: {e}")
            return False
    
    def delete_student(self, student_id: int) -> bool:
        """Delete a student"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('students').delete().eq('id', student_id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting student: {e}")
            return False
    
    # ATTENDANCE OPERATIONS
    def get_attendance_records(self, class_name: Optional[str] = None, 
                             start_date: Optional[date] = None, 
                             end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get attendance records with optional filters"""
        if not self.is_connected():
            return []
        
        try:
            query = self.client.table('attendance_records').select('*')
            
            if class_name:
                query = query.eq('class', class_name)
            if start_date:
                query = query.gte('date', start_date.isoformat())
            if end_date:
                query = query.lte('date', end_date.isoformat())
            
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching attendance records: {e}")
            return []
    
    def save_attendance_records(self, records: List[Dict[str, Any]]) -> bool:
        """Save attendance records (upsert)"""
        if not self.is_connected():
            return False
        
        try:
            # First, delete existing records for the same date and class
            if records:
                first_record = records[0]
                target_date = first_record.get('date')
                target_class = first_record.get('class')
                
                if target_date and target_class:
                    self.client.table('attendance_records').delete().eq('class', target_class).eq('date', target_date).execute()
            
            # Insert new records
            response = self.client.table('attendance_records').insert(records).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error saving attendance records: {e}")
            return False
    
    def get_attendance_summary(self, class_name: str, selected_date: date) -> Dict[str, Any]:
        """Get attendance summary for a class and date"""
        if not self.is_connected():
            return {}
        
        try:
            response = self.client.table('attendance_records').select('status').eq('class', class_name).eq('date', selected_date.isoformat()).execute()
            
            if not response.data:
                return {}
            
            status_counts = {}
            for record in response.data:
                status = record['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            total_students = len(response.data)
            present_count = status_counts.get('P', 0) + status_counts.get('L', 0)
            attendance_rate = (present_count / total_students) * 100 if total_students > 0 else 0
            
            return {
                'total_students': total_students,
                'present_count': present_count,
                'attendance_rate': round(attendance_rate, 1),
                'status_counts': status_counts
            }
        except Exception as e:
            st.error(f"Error getting attendance summary: {e}")
            return {}
    
    # TEACHERS OPERATIONS
    def get_teachers(self, teacher_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all teachers or teachers of a specific type"""
        if not self.is_connected():
            return []
        
        try:
            query = self.client.table('teachers').select('*')
            if teacher_type:
                query = query.eq('type', teacher_type)
            
            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Error fetching teachers: {e}")
            return []
    
    def add_teacher(self, teacher_data: Dict[str, Any]) -> Optional[int]:
        """Add a new teacher"""
        if not self.is_connected():
            return None
        
        try:
            response = self.client.table('teachers').insert(teacher_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            st.error(f"Error adding teacher: {e}")
            return None
    
    def update_teacher(self, teacher_id: int, updates: Dict[str, Any]) -> bool:
        """Update teacher information"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('teachers').update(updates).eq('id', teacher_id).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error updating teacher: {e}")
            return False
    
    def delete_teacher(self, teacher_id: int) -> bool:
        """Delete a teacher"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('teachers').delete().eq('id', teacher_id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting teacher: {e}")
            return False
    
    # DAILY NOTES OPERATIONS
    def save_daily_note(self, class_name: str, note_date: date, text: str) -> bool:
        """Save daily note for a class"""
        if not self.is_connected():
            return False
        
        try:
            note_data = {
                'class': class_name,
                'date': note_date.isoformat(),
                'text': text,
                'last_updated': datetime.now().isoformat()
            }
            
            response = self.client.table('daily_notes').upsert(note_data, on_conflict='class,date').execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error saving daily note: {e}")
            return False
    
    def get_daily_note(self, class_name: str, note_date: date) -> str:
        """Get daily note for a class and date"""
        if not self.is_connected():
            return ""
        
        try:
            response = self.client.table('daily_notes').select('text').eq('class', class_name).eq('date', note_date.isoformat()).execute()
            return response.data[0]['text'] if response.data else ""
        except Exception as e:
            st.error(f"Error getting daily note: {e}")
            return ""
    
    # TIMETABLE OPERATIONS
    def get_class_timetable(self, class_name: str) -> Dict[str, List[str]]:
        """Get timetable for a class"""
        if not self.is_connected():
            return {}
        
        try:
            response = self.client.table('class_timetables').select('day,periods').eq('class_name', class_name).execute()
            
            timetable = {}
            for record in response.data:
                timetable[record['day']] = record['periods']
            
            return timetable
        except Exception as e:
            st.error(f"Error getting timetable: {e}")
            return {}
    
    def save_class_timetable(self, class_name: str, timetable_data: Dict[str, List[str]]) -> bool:
        """Save timetable for a class"""
        if not self.is_connected():
            return False
        
        try:
            # Delete existing timetable for this class
            self.client.table('class_timetables').delete().eq('class_name', class_name).execute()
            
            # Insert new timetable
            records = []
            for day, periods in timetable_data.items():
                records.append({
                    'class_name': class_name,
                    'day': day,
                    'periods': periods
                })
            
            response = self.client.table('class_timetables').insert(records).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error saving timetable: {e}")
            return False
    
    # DUTIES OPERATIONS
    def get_duties_for_date(self, duty_date: date) -> List[Dict[str, Any]]:
        """Get duties for a specific date"""
        if not self.is_connected():
            return []
        
        try:
            response = self.client.table('duties').select('*').eq('date', duty_date.isoformat()).execute()
            return response.data
        except Exception as e:
            st.error(f"Error getting duties: {e}")
            return []
    
    def assign_duty(self, duty_data: Dict[str, Any]) -> bool:
        """Assign a duty"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('duties').insert(duty_data).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error assigning duty: {e}")
            return False
    
    # NOTIFICATIONS OPERATIONS
    def send_class_notification(self, class_name: str, message: str, message_type: str = "info") -> bool:
        """Send notification to a class"""
        if not self.is_connected():
            return False
        
        try:
            notification_data = {
                'class_name': class_name,
                'message': message,
                'message_type': message_type,
                'is_read': False
            }
            
            response = self.client.table('class_notifications').insert(notification_data).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error sending notification: {e}")
            return False
    
    def get_class_notifications(self, class_name: str) -> List[Dict[str, Any]]:
        """Get notifications for a class"""
        if not self.is_connected():
            return []
        
        try:
            response = self.client.table('class_notifications').select('*').eq('class_name', class_name).order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            st.error(f"Error getting notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        if not self.is_connected():
            return False
        
        try:
            response = self.client.table('class_notifications').update({'is_read': True}).eq('id', notification_id).execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Error marking notification as read: {e}")
            return False

# Global instance
supabase_manager = SupabaseManager()
