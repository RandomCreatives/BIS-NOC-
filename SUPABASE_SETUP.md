# BIS NOC Campus - Supabase Integration Setup

This guide will help you integrate your BIS NOC Attendance System with Supabase for cloud-based data storage.

## Prerequisites

- Python 3.8 or higher
- Supabase account (free tier available)
- Your existing BIS NOC system

## Step 1: Set Up Supabase Project

1. **Create Supabase Account**
   - Go to [supabase.com](https://supabase.com)
   - Sign up for a free account
   - Create a new project

2. **Get Your Credentials**
   - In your Supabase dashboard, go to Settings → API
   - Copy your Project URL and anon/public API key
   - Keep these credentials safe

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Credentials

### Option A: Using Streamlit Secrets (Recommended)

1. Create `.streamlit/secrets.toml` file:
```toml
[supabase]
url = "your_supabase_project_url_here"
anon_key = "your_supabase_anon_key_here"
```

### Option B: Using Environment Variables

1. Create `.env` file:
```env
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## Step 4: Set Up Database Schema

1. **Run the SQL Schema**
   - In your Supabase dashboard, go to SQL Editor
   - Copy and paste the contents of `database_schema.sql`
   - Click "Run" to create all tables and relationships

2. **Verify Tables Created**
   - Go to Table Editor in Supabase
   - You should see: students, teachers, attendance_records, daily_notes, class_timetables, duties, marksheets, class_notifications

## Step 5: Migrate Existing Data

1. **Run Migration Script**
   ```bash
   python migrate_to_supabase.py
   ```

2. **Verify Migration**
   - Check your Supabase dashboard to ensure data was migrated
   - Test the new app to ensure everything works

## Step 6: Test the Supabase Version

1. **Run the Supabase Version**
   ```bash
   streamlit run app_supabase.py
   ```

2. **Test Key Features**
   - Mark attendance for a class
   - Add/edit students
   - Send notifications
   - Generate reports

## Step 7: Switch to Production

Once everything is working:

1. **Update your main app.py** (optional)
   - Replace the import statement to use `data_models_supabase` instead of `data_models`
   - Or rename `app_supabase.py` to `app.py`

2. **Backup your data**
   - Your data is now safely stored in Supabase
   - You can export from Supabase dashboard if needed

## Benefits of Supabase Integration

✅ **Cloud Storage**: Data is stored in the cloud, accessible from anywhere
✅ **Real-time Updates**: Multiple users can work simultaneously
✅ **Automatic Backups**: Supabase handles backups automatically
✅ **Scalability**: Can handle more data and users
✅ **Security**: Built-in authentication and row-level security
✅ **API Access**: Can build mobile apps or other integrations

## Troubleshooting

### Connection Issues
- Verify your Supabase URL and API key are correct
- Check that your Supabase project is active
- Ensure your internet connection is stable

### Data Migration Issues
- Check that all CSV files exist in the `data/` folder
- Verify the database schema was created correctly
- Check the migration script output for errors

### Performance Issues
- Supabase free tier has limits (500MB database, 2GB bandwidth)
- Consider upgrading to Pro plan for production use

## Next Steps

1. **Set up Row Level Security (RLS)** for multi-user access
2. **Configure Authentication** for different user roles
3. **Set up automated backups**
4. **Monitor usage** in Supabase dashboard

## Support

- Supabase Documentation: https://supabase.com/docs
- Streamlit Documentation: https://docs.streamlit.io
- BIS NOC System Issues: Check the original system documentation

---

**Note**: This integration maintains all existing functionality while adding cloud storage capabilities. Your original CSV/JSON files remain as backups.
