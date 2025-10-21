# utils/excel_reports.py
import streamlit as st
import pandas as pd
import datetime
import calendar

def display_excel_like_table(monthly_data, class_name, month_year):
    """Display attendance data in Excel-like format"""
    
    # Create DataFrame matching your template structure
    excel_df = create_excel_format_dataframe(monthly_data, month_year)
    
    if excel_df.empty:
        st.info("No data available to display.")
        return
    
    # Display as interactive data grid
    st.dataframe(
        excel_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Quick stats
    st.subheader("📈 Monthly Summary")
    
    if not excel_df.empty:
        # Calculate totals from the data
        p_total = excel_df['P'].sum() if 'P' in excel_df.columns else 0
        a_total = excel_df['A'].sum() if 'A' in excel_df.columns else 0
        l_total = excel_df['L'].sum() if 'L' in excel_df.columns else 0
        ap_total = excel_df['AP'].sum() if 'AP' in excel_df.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Present (P)", int(p_total))
        with col2:
            st.metric("Absent (A)", int(a_total))
        with col3:
            st.metric("Late (L)", int(l_total))
        with col4:
            st.metric("Absent with Permission (AP)", int(ap_total))

def create_excel_format_dataframe(monthly_data, month_year):
    """Convert monthly data to Excel template format"""
    if not monthly_data:
        return pd.DataFrame()
    
    # Parse month and year
    try:
        month_str, year_str = month_year.split(' ')
        month_num = datetime.datetime.strptime(month_str, "%B").month
        year = int(year_str)
    except ValueError:
        st.error("Invalid month format")
        return pd.DataFrame()
    
    # Get number of days in month
    num_days = calendar.monthrange(year, month_num)[1]
    
    # Create columns structure matching your template
    columns = ['Student Name']
    
    # Add day columns (1-31) with day-of-week headers
    for day in range(1, num_days + 1):
        date_obj = datetime.date(year, month_num, day)
        day_name = date_obj.strftime('%a')[:2]  # Mo, Tu, We, etc.
        columns.append(f"{day}\n{day_name}")
    
    # Add totals columns
    columns.extend(['P', 'A', 'L', 'AP'])
    
    # Create DataFrame with these columns
    df = pd.DataFrame(columns=columns)
    
    # Fill with student data
    for student_data in monthly_data:
        student_row = [student_data['name']]
        
        # Initialize counters
        p_count, a_count, l_count, ap_count = 0, 0, 0, 0
        
        # Add daily attendance
        for day in range(1, num_days + 1):
            date_str = datetime.date(year, month_num, day).strftime('%Y-%m-%d')
            status = student_data['attendance'].get(date_str, '')
            student_row.append(status)
            
            # Count statuses
            if status == 'P':
                p_count += 1
            elif status == 'A':
                a_count += 1
            elif status == 'L':
                l_count += 1
            elif status == 'AP':
                ap_count += 1
        
        # Add totals
        student_row.extend([p_count, a_count, l_count, ap_count])
        
        df.loc[len(df)] = student_row
    
    return df