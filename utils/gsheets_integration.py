# utils/gsheets_integration.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import datetime, date
import time

class GoogleSheetsManager:
    def __init__(self):
        self.credentials_file = "credentials.json"  # You'll need to download this from Google Cloud
        self.sheet_name = "BIS NOC Attendance"  # Name of your Google Sheet
        self.client = None
        self.sheet = None
        
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Authenticate with service account
            creds = Credentials.from_service_account_file(self.credentials_file, scopes=scope)
            self.client = gspread.authorize(creds)
            
            # Try to open the sheet, create if it doesn't exist
            try:
                self.sheet = self.client.open(self.sheet_name)
                st.success("✅ Connected to Google Sheets successfully!")
            except gspread.SpreadsheetNotFound:
                st.warning("📄 Creating new Google Sheet...")
                self.sheet = self.client.create(self.sheet_name)
                # Share with yourself (replace with your email)
                self.sheet.share('your-email@gmail.com', perm_type='user', role='writer')
                st.success(f"✅ Created new Google Sheet: {self.sheet_name}")
                
            return True
        except Exception as e:
            st.error(f"❌ Google Sheets authentication failed: {e}")
            return False
    
    def get_attendance_worksheet(self, class_name, date_str=None):
        """Get or create worksheet for specific class and date"""
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m")
        
        worksheet_name = f"{class_name} - {date_str}"
        
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            return worksheet
        except gspread.WorksheetNotFound:
            # Create new worksheet with headers
            worksheet = self.sheet.add_worksheet(title=worksheet_name, rows=1000, cols=20)
            
            # Set up headers for BIS NOC format
            headers = [
                "Date", "Student Name", "Roll Number", "Class", 
                "Status", "Remarks", "Period", "Subject", 
                "Teacher", "Timestamp", "School", "Academic Year"
            ]
            worksheet.append_row(headers)
            
            # Format headers
            worksheet.format('A1:L1', {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.8},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
            })
            
            st.info(f"📋 Created new worksheet: {worksheet_name}")
            return worksheet
    
    def push_attendance_to_sheet(self, class_name, attendance_data, selected_date=None):
        """Push attendance data to Google Sheets"""
        if not self.authenticate():
            return False
        
        try:
            if selected_date is None:
                selected_date = datetime.now().date()
            
            date_str = selected_date.strftime("%Y-%m")
            worksheet = self.get_attendance_worksheet(class_name, date_str)
            
            # Convert attendance data to Google Sheets format
            rows_to_add = []
            for record in attendance_data:
                row = [
                    selected_date.strftime("%d/%m/%Y"),  # Date in DD/MM/YYYY format
                    record['name'],                      # Student Name
                    record['roll_number'],               # Roll Number
                    class_name,                          # Class
                    record['status'],                    # Status (P/L/A/AP)
                    record.get('notes', ''),             # Remarks/Notes
                    "All Day",                          # Period
                    "General Attendance",               # Subject
                    "Class Teacher",                    # Teacher
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                    "BIS NOC Campus",                   # School
                    "2024-2025"                         # Academic Year
                ]
                rows_to_add.append(row)
            
            # Append all rows at once
            if rows_to_add:
                worksheet.append_rows(rows_to_add)
                st.success(f"✅ Attendance data pushed to Google Sheets for {class_name}")
                return True
            
        except Exception as e:
            st.error(f"❌ Error pushing to Google Sheets: {e}")
            return False
    
    def pull_attendance_from_sheet(self, class_name, selected_date=None):
        """Pull attendance data from Google Sheets"""
        if not self.authenticate():
            return []
        
        try:
            if selected_date is None:
                selected_date = datetime.now().date()
            
            date_str = selected_date.strftime("%Y-%m")
            worksheet = self.get_attendance_worksheet(class_name, date_str)
            
            # Get all records
            records = worksheet.get_all_records()
            
            # Filter for the specific date
            target_date = selected_date.strftime("%d/%m/%Y")
            filtered_records = [r for r in records if r.get('Date') == target_date]
            
            # Convert to app format
            attendance_data = []
            for record in filtered_records:
                attendance_data.append({
                    'name': record.get('Student Name', ''),
                    'roll_number': record.get('Roll Number', ''),
                    'status': record.get('Status', ''),
                    'notes': record.get('Remarks', ''),
                    'class': record.get('Class', class_name),
                    'date': selected_date
                })
            
            st.info(f"📥 Loaded {len(attendance_data)} records from Google Sheets")
            return attendance_data
            
        except Exception as e:
            st.error(f"❌ Error pulling from Google Sheets: {e}")
            return []
    
    def sync_attendance(self, class_name, attendance_data, selected_date):
        """Sync attendance data between app and Google Sheets"""
        # Push current data to Google Sheets
        success = self.push_attendance_to_sheet(class_name, attendance_data, selected_date)
        return success
    
    def get_sheet_url(self):
        """Get the URL of the Google Sheet"""
        if self.sheet:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet.id}"
        return None

# Global instance
gsheets_manager = GoogleSheetsManager()

def setup_google_sheets_integration():
    """Setup Google Sheets integration in the app"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("☁️ Google Sheets")
    
    if st.sidebar.button("🔗 Connect to Google Sheets", use_container_width=True):
        if gsheets_manager.authenticate():
            st.sidebar.success("✅ Connected!")
            url = gsheets_manager.get_sheet_url()
            if url:
                st.sidebar.markdown(f"[📊 Open Google Sheet]({url})")
        else:
            st.sidebar.error("❌ Connection failed")
    
    return gsheets_manager

def export_to_google_sheets_format(class_name, start_date, end_date, attendance_data):
    """Convert attendance data to Google Sheets format"""
    google_sheets_data = []
    
    current_date = start_date
    while current_date <= end_date:
        # Filter records for this date
        date_records = [r for r in attendance_data if r['date'] == current_date]
        
        for record in date_records:
            google_record = {
                'Date': current_date.strftime("%d/%m/%Y"),
                'Student Name': record['name'],
                'Roll Number': record['roll_number'],
                'Class': class_name,
                'Status': record['status'],
                'Remarks': record.get('notes', ''),
                'Period': 'All Day',
                'Subject': 'General Attendance',
                'Teacher': 'Class Teacher',
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'School': 'BIS NOC Campus',
                'Academic Year': '2024-2025'
            }
            google_sheets_data.append(google_record)
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(google_sheets_data)