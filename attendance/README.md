# Smart School Attendance System

A comprehensive Streamlit application designed for school attendance management.

## Features

### 🎯 Mark Attendance
- Class-wise attendance system
- Bulk actions (Mark all Present/Absent)
- Three attendance statuses: Present, Absent, Late
- Date-wise attendance recording

### 📊 Data Views
- View daily attendance records
- Student-wise detailed reports
- Monthly reports and analytics
- Student performance tracker

### 📈 Analytical Tools
- Monthly comparison (without charts)
- Student progress monitoring
- Annual attendance average calculation

### 🏆 Awards System
- Year-end awards for best attendance
- Three categories: Platinum, Gold, Silver
- Automatic eligibility determination

## Installation

1. Install required packages:

pip install streamlit pandas


2. Run the application:

streamlit run attendance_system.py


## Data Storage

- `attendance_students.json`: Student details
- `attendance_records.json`: Attendance records

## Usage

1. **First Use**: App will automatically create empty data files
2. **Add Students**: Add data directly to JSON files
3. **Mark Attendance**: Record daily attendance through interface
4. **View Reports**: Analyze through different tabs

## File Structure


// attendance_students.json
{
    "Class 1": ["Student1", "Student2"],
    "Class 2": ["Student3", "Student4"]
}

// attendance_records.json
{
    "2024-01-15": {
        "Class 1": {
            "Student1": "Present",
            "Student2": "Absent"
        }
    }
}


## Key Features

- ✅ User-friendly interface
- ✅ Secure data storage
- ✅ Comprehensive reporting
- ✅ Automatic analytics
- ✅ Awards system
- ✅ Responsive design

## Technical Details

- **Framework**: Streamlit
- **Data Format**: JSON
- **Data Analysis**: Pandas
- **Date Handling**: datetime module

This system provides a complete solution for attendance management in schools.

school) sarosh@Saroshs-Air school % uv run streamlit run farida.py

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.0.41:8501

  For better performance, install the Watchdog module:

  $ xcode-select --install
  $ pip install watchdog