# Data Analytics Dashboard

A beginner-friendly data visualization project for analyzing SAP implementation tracking data. Perfect for learning data analysis and dashboard development with Python.

## 🚀 Key Features

### **Core Analytics**
- **Project Timelines**: Interactive Gantt charts showing development phases
- **Effort Tracking**: Compare forecast vs actual ABAP/PI development hours
- **Status Monitoring**: Track project stages (Dev Completed, In Progress)
- **Team Analysis**: View workload distribution across functional owners and developers

### **Visualization Types**
- **Pie Charts**: WRICEF type distribution
- **Bar Charts**: Complexity levels and implementation counts
- **Scatter Plots**: Date comparisons with trend lines
- **Violin Plots**: Duration distribution analysis
- **Heatmaps**: Team collaboration patterns

### **Error Handling**
- Automatic missing data detection
- Graceful error messages
- Safe numeric conversions

## 📋 Technologies Used
- **Python 3.11**
- **Streamlit** (Dashboard framework)
- **Pandas** (Data processing)
- **Plotly** (Interactive visualizations)
- **Openpyxl** (Excel file handling)

## 📥 Installation

1. **Install Requirements**  
pip install streamlit pandas numpy plotly openpyxl

2. **Prepare Data**  
- Save your WRICEF tracker Excel file as `WRICEF-Tracker-dump.xlsx`
- Required columns:  
        Development ID, WRICEF Type, Complexity, Stage,
        FSD Planned Date, Dev Actual Date, ABAP Effort Forecast

3. **Run Dashboard**  
streamlit run wricef_analytics_pro.py


## 💻 Usage

1. **Main Dashboard**  
   - View key metrics at the top
   - Interactive charts update automatically
   - Hover over data points for details

2. **Section Navigation**  
   - Scroll through analysis sections:
     - FSD Process Timeline
     - FUT Status Tracking
     - Development Performance
     - Team Member Workloads

3. **Custom Filters**  
   - Use built-in selectors to focus on specific:
     - Development IDs
     - Complexity levels
     - Implementation types

## 🧠 Learning Outcomes

1. **Data Visualization Fundamentals**  
   - Create 6+ chart types from raw Excel data
   - Customize colors and layouts
   - Add interactive hover tooltips

2. **Real-World Data Skills**  
   - Clean messy project tracking data
   - Handle date/time conversions
   - Manage missing values

3. **Dashboard Development**  
   - Build multi-section Streamlit apps
   - Create responsive layouts
   - Add dynamic metrics

4. **Error Prevention**  
   - Validate input data
   - Handle calculation errors
   - Create user-friendly warnings

## 💡 Customization Ideas

1. Add new metrics:  
df['New Metric'] = df['ABAP Effort'] / df['Duration']

2. Implement dark/light theme toggle

3. Add filters for specific implementations

4. Create email alerts for overdue projects
