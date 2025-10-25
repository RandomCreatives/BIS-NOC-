# test_connection_streamlit.py
import streamlit as st
import os
from supabase import create_client, Client

def test_supabase_connection():
    """Test Supabase connection using Streamlit secrets"""
    st.title("🔗 Supabase Connection Test")
    
    try:
        # Get credentials from Streamlit secrets
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        
        st.write(f"**Supabase URL:** {url}")
        st.write(f"**API Key:** {key[:20]}...")
        
        # Create client
        client = create_client(url, key)
        
        # Test connection by trying to access a table
        try:
            response = client.table('students').select('count').execute()
            st.success("✅ Successfully connected to Supabase!")
            st.write("📊 Database is accessible")
            
            # Test if tables exist
            st.subheader("🔍 Checking Database Tables")
            
            tables_to_check = ['students', 'teachers', 'attendance_records', 'daily_notes', 'class_timetables', 'duties', 'marksheets', 'class_notifications']
            
            for table in tables_to_check:
                try:
                    response = client.table(table).select('*').limit(1).execute()
                    st.write(f"✅ {table} table exists")
                except Exception as e:
                    st.write(f"❌ {table} table not found: {str(e)[:100]}...")
            
            st.success("🎉 Connection test completed!")
            return True
            
        except Exception as e:
            st.error(f"❌ Database access failed: {e}")
            st.info("💡 You may need to run the database schema first in your Supabase dashboard")
            return False
        
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        st.info("Make sure you have:")
        st.write("1. ✅ Created `.streamlit/secrets.toml` file")
        st.write("2. ✅ Added your Supabase URL and API key")
        st.write("3. ✅ Created the database schema in Supabase dashboard")
        return False

if __name__ == "__main__":
    test_supabase_connection()
