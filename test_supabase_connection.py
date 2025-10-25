# test_supabase_connection.py
import streamlit as st
from utils.supabase_client import supabase_manager

def test_connection():
    """Test Supabase connection"""
    st.title("🔗 Supabase Connection Test")
    
    if supabase_manager.is_connected():
        st.success("✅ Successfully connected to Supabase!")
        
        # Test basic operations
        st.subheader("Testing Basic Operations")
        
        # Test getting students
        students = supabase_manager.get_students()
        st.write(f"📊 Found {len(students)} students in database")
        
        # Test getting teachers
        teachers = supabase_manager.get_teachers()
        st.write(f"👩‍🏫 Found {len(teachers)} teachers in database")
        
        # Test getting attendance records
        attendance = supabase_manager.get_attendance_records()
        st.write(f"📋 Found {len(attendance)} attendance records in database")
        
        st.success("🎉 All tests passed! Your Supabase integration is working correctly.")
        
    else:
        st.error("❌ Failed to connect to Supabase. Please check your credentials in .streamlit/secrets.toml")
        st.info("Make sure you have:")
        st.write("1. ✅ Created `.streamlit/secrets.toml` file")
        st.write("2. ✅ Added your Supabase URL and API key")
        st.write("3. ✅ Created the database schema in Supabase dashboard")

if __name__ == "__main__":
    test_connection()
