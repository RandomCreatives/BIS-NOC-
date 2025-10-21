# app.py - FIXED VERSION
import streamlit as st
import pandas as pd
import datetime
import calendar
import base64
from utils.data_models import (
    initialize_session_state, 
    save_attendance, 
    get_class_attendance_summary,
    get_class_color, 
    send_class_notification, 
    get_class_notifications,
    mark_notification_read, 
    get_attendance_report, 
    get_all_classes_report,
    get_class_students,
    add_student_to_class,
    update_student,
    remove_student,
    save_daily_note,
    get_daily_note,
    get_note_last_updated,
    get_class_timetable,
    save_class_timetable,
    get_student_attendance_history,
    get_class_attendance_trends,
    search_students,
    get_live_timetable_status,
    export_to_custom_format
)

# Initialize session state FIRST
initialize_session_state()

# Page configuration
st.set_page_config(
    page_title="BIS NOC Campus - Attendance System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

def apply_custom_css():
    """Apply custom CSS with blue and lemon color palette"""
    st.markdown("""
    <style>
    .class-button {
        border: 2px solid;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .class-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .notification-unread {
        background-color: #fff3cd;
        border-left: 4px solid #ffd700;
        padding: 10px;
        margin: 5px 0px;
        border-radius: 5px;
    }
    .notification-read {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
        padding: 10px;
        margin: 5px 0px;
        border-radius: 5px;
        opacity: 0.7;
    }
    .sticky-note {
        background-color: #fff9c4;
        border-left: 4px solid #ffd700;
        padding: 15px;
        margin: 10px 0px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .absence-reason {
        background-color: #ffebee;
        border-left: 4px solid #e57373;
        padding: 8px;
        margin: 5px 0px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    .current-period {
        background-color: #e3f2fd !important;
        border-left: 5px solid #1976d2 !important;
        padding: 12px;
        margin: 8px 0;
        border-radius: 5px;
    }
    .next-period {
        background-color: #fff9c4 !important;
        border-left: 5px solid #ffd600 !important;
        padding: 12px;
        margin: 8px 0;
        border-radius: 5px;
    }
    .normal-period {
        border-left: 3px solid #dee2e6;
        padding: 10px;
        margin: 5px 0;
    }
    /* Blue and Lemon color scheme */
    .stButton > button {
        background-color: #D3DAD9;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #9DB2BF;
        color: white;
    }
    .stButton > button:focus {
        background-color: #080A1BA;
        color: white;
    }
    /* Secondary buttons with lemon color */
    .stButton > button[kind="secondary"] {
        background-color: #80A1BA;
        color: #333;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #799EFF;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

def show_custom_header():
    """Display custom header with logo and school name"""
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        try:
            st.image("logo.png", width=280)
        except:
            st.markdown("""
            <div style="text-align: center; padding: 10px;">
                <div style="font-size: 24px;">🏫</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="margin-bottom: 0; color: #1976d2;">BIS NOC Campus</h1>
            <p style="margin-top: 0; color: #666; font-size: 1.1em;">School Attendance System</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        st.markdown(f"""
        <div style="text-align: right; color: #666; font-size: 0.9em;">
            {current_time}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

def create_download_link(df, filename, text):
    """Generate a download link for DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def get_custom_download_link(df, filename, text):
    """Generate download link with BIS NOC custom formatting"""
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d/%m/%Y')
    
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def show_quick_actions(selected_class):
    """Quick actions sidebar for teachers"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        if st.button("📋 Take Roll Call", use_container_width=True):
            st.session_state.mark_attendance_expanded = True
            st.rerun()
        
        if st.button("📝 Add Daily Note", use_container_width=True):
            st.rerun()
        
        if st.button("👥 Add New Student", use_container_width=True):
            st.rerun()
        
        # Today's summary
        st.markdown("---")
        st.subheader("📊 Today's Snapshot")
        
        today = datetime.date.today()
        summary = get_class_attendance_summary(selected_class, today)
        
        if summary:
            st.metric("Present", summary['present_count'])
            st.metric("Absent", summary['total_students'] - summary['present_count'])
            st.metric("Rate", f"{summary['attendance_rate']}%")
        else:
            st.info("Attendance not marked today")

def main():
    apply_custom_css()
    
    # Show custom header
    show_custom_header()
    
    # Initialize session state for navigation
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None
    
    # SIDEBAR - Color-coded class selection and admin
    with st.sidebar:
        # HOME BUTTON
        if st.button("🏠 **Home**", use_container_width=True, type="primary"):
            st.session_state.selected_class = None
            st.rerun()
        
        st.markdown("---")
        
        # Admin section
        if st.button("👨‍💼 **Admin Dashboard**", use_container_width=True, type="secondary"):
            st.session_state.selected_class = "Admin"
            st.rerun()
        
        st.markdown("---")
        st.subheader("🎨 Classes")
        
        # Color-coded class buttons
        for class_name in st.session_state.classes:
            color = get_class_color(class_name)
            is_selected = st.session_state.selected_class == class_name
            
            button_text = f"🎒 {class_name}"
            if st.button(button_text, use_container_width=True, 
                        type="primary" if is_selected else "secondary"):
                st.session_state.selected_class = class_name
                st.rerun()
    
    # Quick actions for class view
    if st.session_state.selected_class and st.session_state.selected_class != "Admin":
        show_quick_actions(st.session_state.selected_class)
    
    # MAIN CONTENT AREA
    if st.session_state.selected_class == "Admin":
        show_admin_dashboard()
    elif st.session_state.selected_class:
        show_class_view()
    else:
        show_welcome_screen()

def show_welcome_screen():
    """Show when no class is selected"""
    st.title("🏫 Welcome to BIS NOC Campus")
    st.subheader("School Attendance Management System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **📚 For Teachers:**
        - Select your class from the sidebar
        - Mark daily attendance
        - Manage students (add/remove/edit)
        - View class timetable
        - Add daily notes and reminders
        - Check notifications
        """)
    
    with col2:
        st.success("""
        **👨‍💼 For Administrators:**
        - Click **Admin Dashboard** in sidebar
        - View school-wide reports
        - Send messages to classes
        - Edit timetables
        - Download reports
        """)
    
    # Quick stats
    st.markdown("---")
    st.subheader("📊 School Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Classes", len(st.session_state.classes))
    with col2:
        st.metric("Total Students", len(st.session_state.students_df))
    with col3:
        today = datetime.date.today()
        marked_today = sum(1 for class_name in st.session_state.classes 
                          if get_class_attendance_summary(class_name, today))
        st.metric("Marked Today", f"{marked_today}/{len(st.session_state.classes)}")
    with col4:
        st.metric("Current Time", datetime.datetime.now().strftime("%H:%M"))

def show_class_view():
    """Show class-specific view with enhanced tabs"""
    selected_class = st.session_state.selected_class
    class_color = get_class_color(selected_class)
    
    # TOPBAR NAVIGATION with class color
    st.markdown(f"<h1 style='color: {class_color}'>🎒 {selected_class}</h1>", unsafe_allow_html=True)
    
    # Create enhanced topbar tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Attendance", 
        "👥 Manage Students",
        "📅 Timetable", 
        "📝 Daily Notes",
        "📥 Export Data", 
        "🔔 Notifications"
    ])
    
    with tab1:
        show_class_attendance(selected_class)
    
    with tab2:
        show_enhanced_student_management(selected_class)
    
    with tab3:
        show_timetable_table(selected_class)
    
    with tab4:
        show_daily_notes(selected_class)
    
    with tab5:
        show_enhanced_download_section(selected_class)
    
    with tab6:
        show_class_notifications(selected_class)

def show_class_attendance(selected_class):
    """Enhanced Attendance tab with absence reasons"""
    st.subheader(f"🎯 Attendance - {selected_class}")
    
    # Date selection
    selected_date = st.date_input(
        "Select Date:",
        datetime.date.today(),
        key=f"date_{selected_class}"
    )
    
    # Get students for this class
    class_students = get_class_students(selected_class)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", len(class_students))
    with col2:
        summary = get_class_attendance_summary(selected_class, selected_date)
        if summary:
            st.metric("Present Today", f"{summary['present_count']}/{summary['total_students']}")
        else:
            st.metric("Present Today", "Not Marked")
    with col3:
        if summary:
            st.metric("Attendance Rate", f"{summary['attendance_rate']}%")
        else:
            st.metric("Attendance Rate", "0%")
    with col4:
        if st.button("📝 Mark Attendance", use_container_width=True):
            st.session_state.mark_attendance_expanded = True
    
    # Check if already marked
    existing_records = [
        r for r in st.session_state.attendance_records 
        if r['class'] == selected_class and r['date'] == selected_date
    ]
    
    if existing_records:
        st.success(f"✅ Attendance already marked for {selected_date}")
        
        # Show summary of existing records
        status_counts = {}
        absence_with_reasons = []
        for record in existing_records:
            status = record['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            if status in ['A', 'AP'] and record.get('notes'):
                absence_with_reasons.append(record)
        
        st.write("**Current Status:**")
        cols = st.columns(4)
        status_info = {
            "P": {"emoji": "✅", "label": "Present", "color": "green"},
            "L": {"emoji": "🟡", "label": "Late", "color": "orange"},
            "A": {"emoji": "🔴", "label": "Absent", "color": "red"},
            "AP": {"emoji": "🔵", "label": "Absent (Permission)", "color": "blue"}
        }
        
        for i, (status, count) in enumerate(status_counts.items()):
            with cols[i]:
                info = status_info.get(status, {"emoji": "⚪", "label": status, "color": "gray"})
                st.metric(f"{info['emoji']} {info['label']}", count)
        
        # Show absence reasons if any
        if absence_with_reasons:
            st.subheader("📋 Absence Reasons")
            for record in absence_with_reasons:
                with st.container():
                    st.markdown(f"""
                    <div class="absence-reason">
                        <strong>{record['name']}</strong> ({record['status']}): {record.get('notes', 'No reason provided')}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Enhanced attendance marking form with reason field
    with st.expander("📝 Mark/Edit Attendance", expanded=st.session_state.get('mark_attendance_expanded', False)):
        if 'mark_attendance_expanded' in st.session_state:
            del st.session_state.mark_attendance_expanded
            
        with st.form(f"attendance_form_{selected_class}"):
            attendance_data = []
            
            st.write(f"**Marking attendance for {selected_class} - {selected_date}**")
            st.info("💡 For absent students, please provide a reason in the notes field")
            
            for _, student in class_students.iterrows():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                with col1:
                    st.write(f"**{student['roll_number']}**")
                
                with col2:
                    st.write(f"{student['name']}")
                
                with col3:
                    # Pre-select existing status if available
                    existing_status = None
                    existing_notes = ""
                    for record in existing_records:
                        if record['student_id'] == student['id']:
                            existing_status = record['status']
                            existing_notes = record.get('notes', '')
                            break
                    
                    status = st.radio(
                        f"Status_{student['id']}",
                        ["P", "L", "A", "AP"],
                        index=["P", "L", "A", "AP"].index(existing_status) if existing_status else 0,
                        horizontal=True,
                        key=f"status_{student['id']}_{selected_date}",
                        label_visibility="collapsed"
                    )
                
                with col4:
                    # Show notes field (especially important for absences)
                    notes_placeholder = "Optional notes..."
                    if status in ['A', 'AP']:
                        notes_placeholder = "Reason for absence required"
                    
                    notes = st.text_input(
                        "Notes",
                        value=existing_notes,
                        placeholder=notes_placeholder,
                        key=f"notes_{student['id']}_{selected_date}",
                        label_visibility="collapsed"
                    )
                
                attendance_data.append({
                    "student_id": student["id"],
                    "name": student["name"],
                    "class": selected_class,
                    "date": selected_date,
                    "status": status,
                    "notes": notes,
                    "roll_number": student["roll_number"]
                })
                
                st.markdown("---")
            
            # Form actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submit_button = st.form_submit_button("💾 Save Attendance", use_container_width=True)
            
            with col2:
                mark_all_present = st.form_submit_button("✅ Mark All Present", use_container_width=True)
            
            with col3:
                clear_form = st.form_submit_button("🔄 Reset Form", use_container_width=True, type="secondary")
            
            if submit_button or mark_all_present:
                # Validate absence reasons
                missing_reasons = []
                for record in attendance_data:
                    if record['status'] in ['A', 'AP'] and not record['notes'].strip():
                        missing_reasons.append(record['name'])
                
                if missing_reasons and not mark_all_present:
                    st.error(f"❌ Please provide reasons for absent students: {', '.join(missing_reasons)}")
                else:
                    if mark_all_present:
                        # Auto-mark all as present and clear notes
                        for student_data in attendance_data:
                            student_data['status'] = 'P'
                            student_data['notes'] = ''
                    
                    save_attendance(attendance_data)
                    st.success(f"✅ Attendance saved for {selected_class}!")
                    st.rerun()
            
            if clear_form:
                st.rerun()

def show_enhanced_student_management(selected_class):
    """Enhanced student management with search and analytics"""
    st.subheader(f"👥 Student Management - {selected_class}")
    
    # Search functionality
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 Search Students", placeholder="Name or roll number...", key=f"search_{selected_class}")
    
    class_students = get_class_students(selected_class)
    
    if search_query:
        class_students = search_students(search_query, selected_class)
        if class_students.empty:
            st.info("No students found matching your search.")
            class_students = get_class_students(selected_class)
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", len(class_students))
    with col2:
        male_count = len(class_students[class_students['gender'] == 'M'])
        st.metric("Male Students", male_count)
    with col3:
        female_count = len(class_students[class_students['gender'] == 'F'])
        st.metric("Female Students", female_count)
    
    # Display current students
    st.subheader("📋 Current Students")
    
    if not class_students.empty:
        # Show editable table
        edited_df = st.data_editor(
            class_students[['id', 'roll_number', 'name', 'gender']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "roll_number": st.column_config.TextColumn("Roll No", disabled=True),
                "name": st.column_config.TextColumn("Student Name"),
                "gender": st.column_config.SelectboxColumn("Gender", options=["M", "F"])
            },
            key=f"student_editor_{selected_class}"
        )
        
        # Save changes button
        if st.button("💾 Save Student Changes", type="primary", key=f"save_changes_{selected_class}"):
            for index, row in edited_df.iterrows():
                original_row = class_students.iloc[index]
                if (row['name'] != original_row['name'] or 
                    row['gender'] != original_row['gender']):
                    update_student(row['id'], {
                        'name': row['name'],
                        'gender': row['gender']
                    })
            st.success("✅ Student information updated!")
            st.rerun()
        
        # Student analytics section
        st.subheader("📈 Student Analytics")
        
        if not class_students.empty:
            selected_student_id = st.selectbox(
                "View Attendance History:",
                options=class_students['id'].tolist(),
                format_func=lambda x: f"{class_students[class_students['id'] == x]['name'].iloc[0]}",
                key=f"student_analytics_{selected_class}"
            )
            
            if selected_student_id:
                attendance_history = get_student_attendance_history(selected_student_id)
                if not attendance_history.empty:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_days = len(attendance_history)
                        present_days = len(attendance_history[attendance_history['status'] == 'P'])
                        attendance_rate = (present_days / total_days) * 100 if total_days > 0 else 0
                        st.metric("30-Day Attendance", f"{attendance_rate:.1f}%")
                    
                    with col2:
                        late_days = len(attendance_history[attendance_history['status'] == 'L'])
                        st.metric("Late Days", late_days)
                    
                    with col3:
                        absent_days = len(attendance_history[attendance_history['status'].isin(['A', 'AP'])])
                        st.metric("Absent Days", absent_days)
                    
                    # Show recent attendance
                    st.write("**Recent Attendance:**")
                    recent_attendance = attendance_history.head(10)[['date', 'status', 'notes']]
                    st.dataframe(recent_attendance, use_container_width=True)
                else:
                    st.info("No attendance records found for this student in the last 30 days.")
        
        # Individual student actions
        st.subheader("🛠️ Student Actions")
        selected_student_id = st.selectbox(
            "Select Student for Actions:",
            options=class_students['id'].tolist(),
            format_func=lambda x: f"{class_students[class_students['id'] == x]['name'].iloc[0]} (ID: {x})",
            key=f"student_actions_{selected_class}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit Selected Student", use_container_width=True, key=f"edit_{selected_class}"):
                st.session_state.editing_student = selected_student_id
                st.rerun()
        
        with col2:
            if st.button("🗑️ Remove Selected Student", use_container_width=True, type="secondary", key=f"remove_{selected_class}"):
                student_name = class_students[class_students['id'] == selected_student_id]['name'].iloc[0]
                if st.checkbox(f"Confirm removal of {student_name}"):
                    if remove_student(selected_student_id):
                        st.success(f"✅ Removed {student_name} from class")
                        st.rerun()
                    else:
                        st.error("❌ Failed to remove student")
    else:
        st.info("No students in this class yet. Add your first student below!")
    
    # Add new student form
    st.subheader("➕ Add New Student")
    
    with st.form(f"add_student_{selected_class}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_student_name = st.text_input("Student Full Name", placeholder="e.g., John Smith", key=f"new_name_{selected_class}")
        
        with col2:
            new_student_gender = st.selectbox("Gender", ["M", "F"], key=f"new_gender_{selected_class}")
        
        if st.form_submit_button("👤 Add Student to Class", type="primary"):
            if new_student_name.strip():
                if add_student_to_class(selected_class, {
                    'name': new_student_name,
                    'gender': new_student_gender
                }):
                    st.success(f"✅ Added {new_student_name} to {selected_class}")
                    st.rerun()
                else:
                    st.error("❌ Failed to add student")
            else:
                st.error("❌ Please enter a student name")

def show_timetable_table(selected_class):
    """Timetable as a table with live status"""
    st.subheader(f"📅 BIS NOC Timetable - {selected_class}")
    
    # Live status section
    live_status = get_live_timetable_status(selected_class)
    
    st.subheader("🎯 Live Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Day", live_status['day'])
    
    with col2:
        current_time = datetime.datetime.now().strftime("%H:%M")
        st.metric("Current Time", current_time)
    
    with col3:
        if live_status['current']:
            st.metric("Current Period", live_status['current']['name'])
        else:
            st.metric("Current Period", "Break/None")
    
    with col4:
        if live_status['next']:
            st.metric("Next Period", live_status['next']['name'])
        else:
            st.metric("Next Period", "No more today")
    
    # Display current/next period highlights
    if live_status['current']:
        st.success(f"**🟢 CURRENTLY RUNNING:** {live_status['current']['name']} ({live_status['current']['time']}) - Ends at {live_status['current']['ends_at']}")
    
    if live_status['next']:
        st.info(f"**🟡 COMING UP NEXT:** {live_status['next']['name']} ({live_status['next']['time']}) - Starts at {live_status['next']['starts_at']}")
    
    # Timetable as a table with times vertical and days horizontal
    st.subheader("📋 Weekly Schedule Table")

    # Use the helper to get default timetable structure
    class_timetable = get_class_timetable(selected_class)

    # Define times (index) consistent with BIS NOC periods
    times = [
        "08:10-08:30",
        "08:30-09:20",
        "09:20-10:10",
        "10:10-10:40",
        "10:40-11:30",
        "11:30-12:20",
        "12:20-13:10",
        "13:10-14:00",
        "14:00-14:10",
        "14:10-15:00"
    ]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Build a dict where each day maps to a list of activities matching times
    table = {"Time": times}
    for day in days:
        activities = class_timetable.get(day, [])
        # Ensure activities list matches times length
        if len(activities) < len(times):
            activities = activities + [""] * (len(times) - len(activities))
        table[day] = activities[:len(times)]

    timetable_df = pd.DataFrame(table)
    timetable_df.set_index('Time', inplace=True)

    # Display the timetable with times as rows and days as columns
    st.dataframe(timetable_df, use_container_width=True)
    
    # Legend
    st.markdown("---")
    st.write("**Legend:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Current Period**")
    with col2:
        st.markdown("🟡 **Next Period**")
    with col3:
        st.markdown("📚 **All Classes Follow Same Schedule**")

def show_daily_notes(selected_class):
    """Daily sticky notes for teachers"""
    st.subheader(f"📝 Daily Notes - {selected_class}")
    
    # Date selection
    selected_date = st.date_input(
        "Select Date for Notes:",
        datetime.date.today(),
        key=f"notes_date_{selected_class}"
    )
    
    # Get existing note
    existing_note = get_daily_note(selected_class, selected_date)
    last_updated = get_note_last_updated(selected_class, selected_date)
    
    st.write(f"**Notes for {selected_date.strftime('%A, %B %d, %Y')}**")
    if last_updated:
        st.caption(f"Last updated: {last_updated}")
    
    # Sticky note editor
    note_text = st.text_area(
        "Your Daily Notes:",
        value=existing_note,
        placeholder="Write your notes for today...\n• Reminders\n• Important events\n• Things to follow up\n• Student observations",
        height=200,
        key=f"note_editor_{selected_class}_{selected_date}",
        label_visibility="collapsed"
    )
    
    # Note actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Note", use_container_width=True, type="primary"):
            save_daily_note(selected_class, selected_date, note_text)
            st.success("✅ Note saved!")
            st.rerun()
    
    with col2:
        if st.button("📋 Clear Note", use_container_width=True):
            save_daily_note(selected_class, selected_date, "")
            st.success("✅ Note cleared!")
            st.rerun()
    
    with col3:
        if st.button("📄 New Note Template", use_container_width=True):
            template = f"Notes for {selected_date.strftime('%Y-%m-%d')}\n\n• \n• \n• "
            st.session_state[f"note_editor_{selected_class}_{selected_date}"] = template
            st.rerun()
    
    # Display current note in sticky note style
    if note_text.strip():
        st.subheader("📌 Your Note Preview:")
        st.markdown(f"""
        <div class="sticky-note">
            {note_text.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
    
    # Recent notes preview
    st.subheader("📅 Recent Notes")
    recent_dates = []
    for i in range(7):
        date = datetime.date.today() - datetime.timedelta(days=i)
        note = get_daily_note(selected_class, date)
        if note.strip():
            recent_dates.append((date, note))
    
    if recent_dates:
        for date, note in recent_dates[:3]:
            with st.expander(f"📝 {date.strftime('%Y-%m-%d')}"):
                st.write(note)
                if st.button("📋 Copy to Today", key=f"copy_{date}"):
                    save_daily_note(selected_class, selected_date, note)
                    st.success("Note copied to today!")
                    st.rerun()
    else:
        st.info("No recent notes. Start by writing your first note above!")

def show_enhanced_download_section(selected_class):
    """Enhanced download section with BIS NOC custom format"""
    st.subheader("📥 Export Data - BIS NOC Format")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.datetime.now().date() - datetime.timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.datetime.now().date())
    
    # Format selection
    export_format = st.radio(
        "Export Format:",
        ["📋 BIS NOC Custom Format", "📊 Standard Format", "📈 Analytics Report"],
        horizontal=True
    )
    
    # Download buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download Attendance", use_container_width=True, type="primary"):
            if export_format == "📋 BIS NOC Custom Format":
                df = export_to_custom_format(selected_class, start_date, end_date)
                filename = f"BIS_NOC_{selected_class}_Attendance_{start_date}_to_{end_date}.csv"
                if not df.empty:
                    download_link = get_custom_download_link(df, filename, "📥 Download BIS NOC Format")
                    st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("No data available for the selected period.")
            elif export_format == "📊 Standard Format":
                df = get_attendance_report(selected_class, start_date, end_date)
                filename = f"{selected_class}_attendance_{start_date}_to_{end_date}.csv"
                if not df.empty:
                    download_link = create_download_link(df, filename, "📥 Download Standard Format")
                    st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("No data available for the selected period.")
            else:
                df = get_class_attendance_trends(selected_class, (end_date - start_date).days)
                filename = f"{selected_class}_analytics_{start_date}_to_{end_date}.csv"
                if not df.empty:
                    download_link = create_download_link(df, filename, "📥 Download Analytics")
                    st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.warning("No analytics data available.")
    
    with col2:
        if st.button("🕒 Download Timetable", use_container_width=True):
            timetable_data = {
                "Period": [
                    "Morning Activity, Registration", "Lesson 1", "Lesson 2", "Recess - Snack Time",
                    "Lesson 3", "Lesson 4", "Lunch Time", "Lesson 5", "Mini Break", "Lesson 6"
                ],
                "Time": [
                    "08:10-08:30", "08:30-09:20", "09:20-10:10", "10:10-10:40",
                    "10:40-11:30", "11:30-12:20", "12:20-13:10", "13:10-14:00", "14:00-14:10", "14:10-15:00"
                ]
            }
            timetable_df = pd.DataFrame(timetable_data)
            timetable_link = create_download_link(timetable_df, f"BIS_NOC_Timetable.csv", "📥 Download Timetable")
            st.markdown(timetable_link, unsafe_allow_html=True)
    
    with col3:
        if st.button("👥 Download Student List", use_container_width=True):
            students = get_class_students(selected_class)
            if not students.empty:
                students_link = create_download_link(students[['roll_number', 'name', 'gender']], 
                                                   f"BIS_NOC_{selected_class}_Students.csv", 
                                                   "📥 Download Student List")
                st.markdown(students_link, unsafe_allow_html=True)
            else:
                st.warning("No students in this class.")

def show_class_notifications(selected_class):
    """Notifications tab for specific class"""
    st.subheader(f"🔔 Notifications - {selected_class}")
    
    # Get notifications for this class
    notifications = get_class_notifications(selected_class)
    
    if notifications:
        st.write("**Recent Messages**")
        
        for i, notification in enumerate(notifications):
            css_class = "notification-unread" if not notification['read'] else "notification-read"
            message_html = f"""
            <div class="{css_class}">
                <strong>{notification['message']}</strong><br>
                <small>📅 {notification['timestamp']}</small>
            </div>
            """
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(message_html, unsafe_allow_html=True)
            with col2:
                if not notification['read']:
                    if st.button("✓ Read", key=f"read_{i}"):
                        mark_notification_read(selected_class, i)
                        st.rerun()
    else:
        st.info("No notifications for this class.")
    
    # Mark all as read
    if notifications and any(not n['read'] for n in notifications):
        if st.button("📭 Mark All as Read"):
            for i in range(len(notifications)):
                mark_notification_read(selected_class, i)
            st.rerun()

def show_admin_dashboard():
    """Admin Dashboard - FIXED VERSION"""
    st.title("👨‍💼 Admin Dashboard - BIS NOC Campus")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "📢 Send Messages", 
        "🕒 School Timetable", 
        "📋 Reports"
    ])
    
    with tab1:
        show_admin_overview()
    
    with tab2:
        show_admin_messages()
    
    with tab3:
        show_admin_timetable()
    
    with tab4:
        show_admin_reports()

def show_admin_overview():
    """Admin overview tab - FIXED delta_color error"""
    st.subheader("📊 School Overview - BIS NOC Campus")
    
    # School-wide statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Classes", len(st.session_state.classes))
    with col2:
        st.metric("Total Students", len(st.session_state.students_df))
    with col3:
        today = datetime.date.today()
        marked_today = sum(1 for class_name in st.session_state.classes 
                          if get_class_attendance_summary(class_name, today))
        st.metric("Marked Today", f"{marked_today}/{len(st.session_state.classes)}")
    with col4:
        total_attendance = len(st.session_state.attendance_records)
        st.metric("Total Records", total_attendance)
    
    # Class-wise attendance for today - FIXED delta_color
    st.subheader("🎯 Today's Attendance Summary")
    
    cols = st.columns(4)
    for i, class_name in enumerate(st.session_state.classes):
        with cols[i % 4]:
            summary = get_class_attendance_summary(class_name, datetime.date.today())
            
            if summary:
                # FIXED: Use proper delta_color values
                attendance_rate = summary['attendance_rate']
                if attendance_rate >= 90:
                    delta_color = "normal"
                elif attendance_rate >= 75:
                    delta_color = "off"
                else:
                    delta_color = "inverse"
                
                st.metric(
                    class_name,
                    f"{attendance_rate}%",
                    f"{summary['present_count']}/{summary['total_students']}",
                    delta_color=delta_color
                )
            else:
                class_students = len(st.session_state.students_df[
                    st.session_state.students_df['class'] == class_name
                ])
                st.metric(class_name, "Not Marked", f"{class_students} students")

def show_admin_messages():
    """Admin message sending interface"""
    st.subheader("📢 Send Messages to Classes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        message_type = st.selectbox(
            "Message Type:",
            ["📢 General Announcement", "⚠️ Important Alert", "📝 Reminder", "🎉 Good News"]
        )
    
    with col2:
        target_classes = st.multiselect(
            "Send to Classes:",
            st.session_state.classes,
            default=st.session_state.classes
        )
    
    message = st.text_area(
        "Message Content:",
        placeholder="Type your message here...",
        height=100
    )
    
    if st.button("📤 Send Message", type="primary"):
        if not message.strip():
            st.error("Please enter a message")
        elif not target_classes:
            st.error("Please select at least one class")
        else:
            for class_name in target_classes:
                send_class_notification(class_name, message, message_type)
            st.success(f"✅ Message sent to {len(target_classes)} classes!")

def show_admin_timetable():
    """Admin timetable editor: select class, edit times x days grid, save or publish to all classes"""
    st.subheader("🕒 BIS NOC - Timetable Editor (Admin)")

    # Select class to edit
    selected_class = st.selectbox("Select Class to Edit:", st.session_state.classes, key="admin_timetable_class")

    # Get current timetable for the class
    current_tt = get_class_timetable(selected_class)

    # Times index
    times = [
        "08:10-08:30",
        "08:30-09:20",
        "09:20-10:10",
        "10:10-10:40",
        "10:40-11:30",
        "11:30-12:20",
        "12:20-13:10",
        "13:10-14:00",
        "14:00-14:10",
        "14:10-15:00"
    ]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Build editable dataframe
    table = {"Time": times}
    for day in days:
        activities = current_tt.get(day, [""] * len(times))
        if len(activities) < len(times):
            activities = activities + [""] * (len(times) - len(activities))
        table[day] = activities[:len(times)]

    tt_df = pd.DataFrame(table).set_index('Time')

    st.write("Edit the timetable cells below (times on the left, days across the top):")
    edited = st.data_editor(
        tt_df,
        use_container_width=True,
        num_rows="fixed",
        key=f"admin_timetable_editor_{selected_class}"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save Timetable for Class", type="primary"):
            # Convert edited frame back to dict-of-lists
            new_tt = {day: edited[day].tolist() for day in days}
            save_class_timetable(selected_class, new_tt)
            st.success(f"✅ Timetable saved for {selected_class}")
            st.rerun()
    with col2:
        if st.button("📣 Publish to All Classes", type="secondary"):
            # Publish this timetable to all classes
            for cls in st.session_state.classes:
                save_class_timetable(cls, {day: edited[day].tolist() for day in days})
            st.success("✅ Timetable published to all classes")
            st.rerun()

def show_admin_reports():
    """Admin reporting interface"""
    st.subheader("📋 Generate Reports")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.datetime.now().date() - datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.datetime.now().date())
    
    report_type = st.selectbox(
        "Report Type:",
        ["All Classes Summary", "Individual Class Reports", "Attendance Trends"]
    )
    
    if st.button("📊 Generate Report", type="primary"):
        if report_type == "All Classes Summary":
            df = get_all_classes_report(start_date, end_date)
            if not df.empty:
                st.success(f"Report generated for {len(df)} records")
                st.dataframe(df, use_container_width=True)
                
                # Download link
                filename = f"BIS_NOC_All_Classes_Report_{start_date}_to_{end_date}.csv"
                download_link = get_custom_download_link(df, filename, "📥 Download Full Report")
                st.markdown(download_link, unsafe_allow_html=True)
            else:
                st.warning("No data available for the selected period.")

if __name__ == "__main__":
    main()