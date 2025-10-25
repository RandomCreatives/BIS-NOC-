# test_simple_connection.py
import streamlit as st
from supabase import create_client, Client

def test_connection():
    """Simple connection test"""
    st.title("🔗 Supabase Connection Test")
    
    try:
        # Get credentials from Streamlit secrets
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["anon_key"]
        
        st.write(f"**Supabase URL:** {url}")
        st.write(f"**API Key:** {key[:20]}...")
        
        # Create client with simple parameters
        client = create_client(url, key)
        
        # Test basic connection
        st.info("Testing connection...")
        
        # Try to access the database
        response = client.table('students').select('*').limit(1).execute()
        
        st.success("✅ Successfully connected to Supabase!")
        st.write(f"📊 Found {len(response.data)} students in database")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        
        # Check if it's a table not found error
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            st.warning("💡 Database tables not found. You need to run the database schema first!")
            st.info("**Next steps:**")
            st.write("1. Go to your Supabase dashboard")
            st.write("2. Navigate to SQL Editor")
            st.write("3. Copy and paste the contents of `database_schema.sql`")
            st.write("4. Click 'Run' to create all tables")
        
        return False

if __name__ == "__main__":
    test_connection()
