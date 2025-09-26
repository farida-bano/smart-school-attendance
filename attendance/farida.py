import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from collections import defaultdict

# ✅ CRITICAL: set_page_config MUST be the first Streamlit command
st.set_page_config(page_title="Smart School Attendance System", page_icon="🏫", layout="wide")

class SmartAttendanceSystem:
    def __init__(self):
        self.students_file = "attendance_students.json"
        self.attendance_file = "attendance_records.json"
        self.load_data()
    
    def load_data(self):
        # Load students data
        try:
            with open(self.students_file, 'r') as f:
                self.students = json.load(f)
        except FileNotFoundError:
            self.students = {}
            st.warning("Students file not found. Starting with empty students database.")
        
        # Load attendance data
        try:
            with open(self.attendance_file, 'r') as f:
                self.attendance_data = json.load(f)
        except FileNotFoundError:
            self.attendance_data = {}
            st.warning("Attendance file not found. Starting with empty attendance records.")
    
    def save_attendance(self):
        """Save attendance data to JSON file"""
        try:
            with open(self.attendance_file, 'w') as f:
                json.dump(self.attendance_data, f, indent=4)
        except Exception as e:
            st.error(f"Error saving attendance data: {e}")

    def mark_attendance_ui(self):
        """Improved UI for marking attendance"""
        st.header("🎯 Mark Attendance")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            class_selected = st.selectbox("Select Class", list(self.students.keys()))
            attendance_date = st.date_input("Select Date", datetime.today())
            bulk_action = st.selectbox("Bulk Action", ["Select All", "Mark All Present", "Mark All Absent", "No Bulk Action"])
        
        if class_selected:
            with col2:
                st.subheader(f"📊 Quick Attendance for {class_selected}")
                
                default_status = "Present" if bulk_action == "Mark All Present" else "Absent" if bulk_action == "Mark All Absent" else "Present"
                
                attendance_status = {}
                cols = st.columns(4)
                
                for i, student in enumerate(self.students[class_selected]):
                    with cols[i % 4]:
                        status = st.radio(
                            f"**{student}**",
                            ["Present", "Absent", "Late"],
                            index=0 if bulk_action in ["Select All", "Mark All Present"] else 1 if bulk_action == "Mark All Absent" else 0,
                            key=f"att_{class_selected}_{student}_{attendance_date}"
                        )
                        attendance_status[student] = status
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("💾 Save Attendance", use_container_width=True):
                    self.save_daily_attendance(class_selected, str(attendance_date), attendance_status)
                    st.success(f"✅ Attendance saved for {class_selected} on {attendance_date}!")
                    
                    present_count = list(attendance_status.values()).count("Present")
                    absent_count = list(attendance_status.values()).count("Absent")
                    late_count = list(attendance_status.values()).count("Late")
                    
                    st.info(f"**Summary:** Present: {present_count} | Absent: {absent_count} | Late: {late_count}")

    def year_end_awards_ui(self):
        """Awards for best attendance performers"""
        st.header("🏆 Year-End Attendance Awards")
        st.subheader("Top Performers with Perfect Attendance")
        
        if not self.attendance_data:
            st.info("No attendance records found for awards calculation.")
            return
        
        current_year = datetime.now().year
        award_categories = {
            "Platinum Award (100% Attendance)": 100,
            "Gold Award (95%+ Attendance)": 95,
            "Silver Award (90%+ Attendance)": 90
        }
        
        for award_name, threshold in award_categories.items():
            st.markdown(f"### {award_name}")
            
            award_winners = []
            for class_name, students in self.students.items():
                for student in students:
                    total_days = 0
                    present_days = 0
                    
                    for date, classes in self.attendance_data.items():
                        try:
                            record_date = datetime.strptime(date, "%Y-%m-%d")
                            if record_date.year == current_year and class_name in classes:
                                if student in classes[class_name]:
                                    total_days += 1
                                    if classes[class_name][student] == "Present":
                                        present_days += 1
                        except ValueError:
                            continue
                    
                    if total_days >= 50:
                        attendance_rate = (present_days / total_days) * 100
                        if attendance_rate >= threshold:
                            award_winners.append({
                                'Class': class_name,
                                'Student': student,
                                'Attendance Rate': f"{attendance_rate:.1f}%",
                                'Days Present': present_days,
                                'Total Days': total_days
                            })
            
            if award_winners:
                df = pd.DataFrame(award_winners)
                st.dataframe(df.sort_values('Attendance Rate', ascending=False))
            else:
                st.info(f"No students qualified for {award_name}")

    def monthly_comparison_ui(self):
        """Monthly comparison without charts"""
        st.header("📈 Monthly Attendance Analytics")
        
        if not self.attendance_data:
            st.info("No attendance records found for analytics.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            year = st.selectbox("Select Year", range(2023, 2031), key="chart_year")
            class_selected = st.selectbox("Select Class", list(self.students.keys()), key="chart_class")
        
        # Prepare monthly data
        monthly_data = []
        for month in range(1, 13):
            monthly_records = {}
            for date, classes in self.attendance_data.items():
                try:
                    record_date = datetime.strptime(date, "%Y-%m-%d")
                    if record_date.year == year and record_date.month == month:
                        if class_selected in classes:
                            monthly_records = classes[class_selected]
                except ValueError:
                    continue
            
            if monthly_records:
                present_count = list(monthly_records.values()).count("Present")
                absent_count = list(monthly_records.values()).count("Absent")
                late_count = list(monthly_records.values()).count("Late")
                total_count = len(monthly_records)
                
                monthly_data.append({
                    'Month': month,
                    'Present': present_count,
                    'Absent': absent_count,
                    'Late': late_count,
                    'Total': total_count,
                    'Attendance Rate': (present_count / total_count * 100) if total_count > 0 else 0
                })
        
        if monthly_data:
            df = pd.DataFrame(monthly_data)
            
            # Table format mein display karein (charts ke bina)
            st.subheader(f"Monthly Attendance Data - {class_selected} {year}")
            st.dataframe(df)
            
            # Best and worst months
            best_month = df.loc[df['Attendance Rate'].idxmax()]
            worst_month = df.loc[df['Attendance Rate'].idxmin()]
            
            st.subheader("📊 Monthly Performance Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Best Month", f"Month {int(best_month['Month'])}", 
                         f"{best_month['Attendance Rate']:.1f}%")
            with col2:
                st.metric("Worst Month", f"Month {int(worst_month['Month'])}", 
                         f"{worst_month['Attendance Rate']:.1f}%")
        else:
            st.info(f"No data found for {class_selected} in {year}")

    def student_progress_ui(self):
        """Student progress without charts"""
        st.header("📊 Student Progress Tracker")
        
        if not self.students:
            st.info("No students data found.")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            class_selected = st.selectbox("Select Class", list(self.students.keys()), key="progress_class")
        with col2:
            student_selected = st.selectbox("Select Student", self.students[class_selected], key="progress_student")
        
        if student_selected:
            monthly_progress = []
            current_year = datetime.now().year
            
            for month in range(1, 13):
                monthly_present = 0
                monthly_total = 0
                
                for date, classes in self.attendance_data.items():
                    try:
                        record_date = datetime.strptime(date, "%Y-%m-%d")
                        if (record_date.year == current_year and 
                            record_date.month == month and 
                            class_selected in classes and 
                            student_selected in classes[class_selected]):
                            
                            monthly_total += 1
                            if classes[class_selected][student_selected] == "Present":
                                monthly_present += 1
                    except ValueError:
                        continue
                
                if monthly_total > 0:
                    monthly_progress.append({
                        'Month': month,
                        'Attendance Rate': (monthly_present / monthly_total) * 100,
                        'Days Present': monthly_present,
                        'Days Recorded': monthly_total
                    })
            
            if monthly_progress:
                df = pd.DataFrame(monthly_progress)
                
                # Table format mein display
                st.subheader(f"{student_selected} - Monthly Attendance Progress")
                st.dataframe(df)
                
                # Current status
                current_month = datetime.now().month
                current_month_data = df[df['Month'] == current_month]
                
                if not current_month_data.empty:
                    current_rate = current_month_data['Attendance Rate'].values[0]
                    st.metric("Current Month Attendance", f"{current_rate:.1f}%")
                
                # Overall performance
                total_present = df['Days Present'].sum()
                total_days = df['Days Recorded'].sum()
                overall_rate = (total_present / total_days) * 100 if total_days > 0 else 0
                
                st.metric("Overall Annual Attendance", f"{overall_rate:.1f}%")
            else:
                st.info(f"No attendance records found for {student_selected}")

    def save_daily_attendance(self, class_name, date, status_dict):
        """Daily attendance save karein"""
        if date not in self.attendance_data:
            self.attendance_data[date] = {}
        
        self.attendance_data[date][class_name] = status_dict
        self.save_attendance()

    def view_daily_attendance_ui(self):
        """View daily attendance records"""
        st.header("View Daily Attendance")
        
        if not self.attendance_data:
            st.info("No attendance records found.")
            return
        
        dates = list(self.attendance_data.keys())
        selected_date = st.selectbox("Select Date", dates)
        
        if selected_date:
            st.subheader(f"Attendance for {selected_date}")
            
            for class_name, students in self.attendance_data[selected_date].items():
                st.write(f"**Class: {class_name}**")
                attendance_df = pd.DataFrame(list(students.items()), 
                                           columns=['Student', 'Status'])
                st.dataframe(attendance_df)

    def student_report_ui(self):
        """Generate student-wise report"""
        st.header("Student Report")
        
        if not self.students:
            st.info("No students data found.")
            return
        
        class_selected = st.selectbox("Select Class", list(self.students.keys()), key="report_class")
        
        if class_selected:
            student_selected = st.selectbox("Select Student", self.students[class_selected])
            
            if student_selected:
                student_records = []
                
                for date, classes in self.attendance_data.items():
                    if class_selected in classes and student_selected in classes[class_selected]:
                        status = classes[class_selected][student_selected]
                        student_records.append({
                            'Date': date,
                            'Status': status
                        })
                
                if student_records:
                    df = pd.DataFrame(student_records)
                    st.subheader(f"Attendance Report for {student_selected}")
                    st.dataframe(df)
                    
                    present_count = len(df[df['Status'] == 'Present'])
                    absent_count = len(df[df['Status'] == 'Absent'])
                    late_count = len(df[df['Status'] == 'Late'])
                    total_count = len(df)
                    
                    st.write(f"**Summary:**")
                    st.write(f"Present: {present_count} ({present_count/total_count*100:.1f}%)")
                    st.write(f"Absent: {absent_count} ({absent_count/total_count*100:.1f}%)")
                    st.write(f"Late: {late_count} ({late_count/total_count*100:.1f}%)")
                else:
                    st.info(f"No attendance records found for {student_selected}")

    def monthly_report_ui(self):
        """Generate monthly attendance report"""
        st.header("Monthly Report")
        
        if not self.attendance_data:
            st.info("No attendance records found.")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Select Year", range(2023, 2031))
        with col2:
            month = st.selectbox("Select Month", range(1, 13))
        
        monthly_records = {}
        
        for date, classes in self.attendance_data.items():
            try:
                record_date = datetime.strptime(date, "%Y-%m-%d")
                if record_date.year == year and record_date.month == month:
                    monthly_records[date] = classes
            except ValueError:
                continue
        
        if monthly_records:
            st.subheader(f"Monthly Report for {month}/{year}")
            
            class_summary = {}
            
            for date, classes in monthly_records.items():
                for class_name, students in classes.items():
                    if class_name not in class_summary:
                        class_summary[class_name] = {'Present': 0, 'Absent': 0, 'Late': 0, 'Total': 0}
                    
                    for student, status in students.items():
                        class_summary[class_name][status] += 1
                        class_summary[class_name]['Total'] += 1
            
            for class_name, summary in class_summary.items():
                st.write(f"**{class_name}:**")
                st.write(f"Present: {summary['Present']} | Absent: {summary['Absent']} | Late: {summary['Late']} | Total: {summary['Total']}")
        else:
            st.info(f"No records found for {month}/{year}")

    def run_streamlit_app(self):
        st.title("🏫 Smart School Attendance Management System")
        
        menu = st.sidebar.selectbox("Navigation", 
                                   ["🎯 Mark Attendance", "📊 View Daily Attendance", 
                                    "👤 Student Report", "📈 Monthly Report",
                                    "📊 Student Progress", "📈 Monthly Analytics",
                                    "🏆 Year-End Awards"])
        
        if menu == "🎯 Mark Attendance":
            self.mark_attendance_ui()
        elif menu == "📊 View Daily Attendance":
            self.view_daily_attendance_ui()
        elif menu == "👤 Student Report":
            self.student_report_ui()
        elif menu == "📈 Monthly Report":
            self.monthly_report_ui()
        elif menu == "📊 Student Progress":
            self.student_progress_ui()
        elif menu == "📈 Monthly Analytics":
            self.monthly_comparison_ui()
        elif menu == "🏆 Year-End Awards":
            self.year_end_awards_ui()

# Run the app
if __name__ == "__main__":
    system = SmartAttendanceSystem()
    system.run_streamlit_app()