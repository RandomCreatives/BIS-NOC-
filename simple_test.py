# simple_test.py - Test Supabase connection without Streamlit
import os
from supabase import create_client, Client

def test_supabase_connection():
    """Test Supabase connection directly"""
    print("🔗 Testing Supabase Connection...")
    
    try:
        # Try to get credentials from environment or secrets
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials not found in environment variables")
            print("Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
            return False
        
        # Create client
        client = create_client(url, key)
        
        # Test connection by trying to access a table
        response = client.table('students').select('count').execute()
        print("✅ Successfully connected to Supabase!")
        print(f"📊 Database is accessible")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
