# app_supabase.py - SUPABASE VERSION
import streamlit as st
import pandas as pd
import datetime
import calendar
import base64
from utils.data_models_supabase import (
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
    # teachers/duties
    get_teachers,
    add_teacher,
    update_teacher,
    remove_teacher,
    get_teacher_by_id,
    update_attendance_from_list,
    remove_duty,
    get_marksheet,
    save_marksheet,
    assign_duty,
    get_duties_for_date,
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
    page_title="BIS NOC Campus - Attendance System (Supabase)",
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
            <p style="margin-top: 0; color: #666; font-size: 1.1em;">School Attendance System (Supabase)</p>
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
        # Direct link to Admin Teachers Portal
        if st.button("👩‍🏫 Teachers Portal (Admin)", use_container_width=True, type="secondary"):
            st.session_state.selected_class = "AdminTeachers"
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

    # Sidebar: small navigation only (Teachers are managed in Admin Teachers Portal)
    with st.sidebar:
        st.markdown("---")
        st.subheader("👩‍🏫 Teachers Portal")
        st.markdown("Click 'Teachers Portal (Admin)' above to manage teachers and view marksheets.")
    
    # MAIN CONTENT AREA
    # If a teacher was selected in the sidebar, show teacher portal
    if st.session_state.get('selected_teacher'):
        show_teacher_portal(st.session_state.get('selected_teacher'))
        return

    if st.session_state.selected_class == "Admin":
        show_admin_dashboard()
    elif st.session_state.selected_class == "AdminTeachers":
        show_admin_teachers_portal()
    elif st.session_state.selected_class == "AdminAttendanceReview":
        show_admin_attendance_review()
    elif st.session_state.selected_class:
        show_class_view()
    else:
        show_welcome_screen()

def show_welcome_screen():
    """Show when no class is selected"""
    st.title("🏫 Welcome to BIS NOC Campus")
    st.subheader("School Attendance Management System (Supabase)")
    
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

    # Show today's duties briefly for teachers to notice
    st.markdown("---")
    st.subheader("👩‍🏫 Today's Duties")
    today = datetime.date.today()
    duties = get_duties_for_date(today)
    if duties:
        for d in duties:
            teacher = get_teacher_by_id(d.get('teacher_id'))
            teacher_name = teacher['name'] if teacher else f"ID {d.get('teacher_id')}"
            st.markdown(f"- {d.get('time_slot')} — {teacher_name} ({d.get('role')})")
    else:
        st.info("No duties assigned for today")

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
        if r['class'] == selected_class and r['date'] == selected_date.isoformat()
    ]

    # Monthly summary (read-only for teachers, editable for admin)
    if st.button("📆 Monthly Summary"):
        # Show previous month summary modal-like section
        month_start = (selected_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
        df = get_attendance_report(selected_class, month_start, month_end)
        if df.empty:
            st.info("No attendance data for previous month")
        else:
            st.subheader(f"Attendance Summary: {month_start.strftime('%B %Y')}")
            st.dataframe(df, use_container_width=True)
            if st.session_state.get('selected_class') == 'Admin':
                st.warning("Admin can edit records here: select a row and use the edit tools below.")
    
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

# Continue with the rest of the functions...
# (The remaining functions would be similar to the original app.py but using Supabase data models)

if __name__ == "__main__":
    main()
