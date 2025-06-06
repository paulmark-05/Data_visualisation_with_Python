# wricef_analytics_complete_fixed.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="WRICEF Tracker Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    """Load and preprocess WRICEF data with comprehensive error handling"""
    try:
        df = pd.read_excel('WRICEF-Tracker-dump.xlsx', engine='openpyxl')

        # Date columns from your actual data
        date_columns = [
            'FSD Planned Del Date', 'FSD Recieved Date', 
            'FSD Planned Walkthrough Date', 'FSD Actual Walkthrough Date',
            'Planned FUT Date', 'Revised FUT Date', 'Actual FUT Date',
            'Dev Planned Delivery Date', 'Dev Revised Delivery Date', 'Dev Actual Delivery Date',
            'Dev Planned Start Date', 'Dev Revised Start Date', 'Dev Actual Start Date',
            'ABAP Planned Delivery Date', 'ABAP Revised Delivery Date', 'ABAP Actual Delivery Date'
        ]

        # Convert date columns properly
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Numeric columns
        numeric_columns = [
            'ABAP Effort Forecast (hrs)', 'ABAP Actual Effort (hrs)',
            'PI Effort Forecast (hrs)', 'PI Actual Effort (hrs)', 'FSI'
        ]

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Clean categorical data
        categorical_columns = [
            'Implementation', 'WRICEF Type', 'Complexity', 'Priority of Delivery',
            'Stage', 'Functional Owner', 'Dev Lead ', 'ABAP Developer ', 'FUT Status'
        ]

        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown').astype(str)

        # Calculate derived metrics with safe handling
        df['FSD Duration'] = (df['FSD Actual Walkthrough Date'] - df['FSD Planned Del Date']).dt.days
        df['DEV Duration'] = (df['Dev Actual Delivery Date'] - df['Dev Planned Delivery Date']).dt.days
        df['FUT Duration'] = (df['Actual FUT Date'] - df['Planned FUT Date']).dt.days
        df['ABAP Effort Variance'] = df['ABAP Actual Effort (hrs)'] - df['ABAP Effort Forecast (hrs)']

        # CRITICAL FIX: Create safe size columns for scatter plots (no negative values)
        df['FSD Duration Safe'] = df['FSD Duration'].fillna(0).abs() + 1
        df['DEV Duration Safe'] = df['DEV Duration'].fillna(0).abs() + 1
        df['FUT Duration Safe'] = df['FUT Duration'].fillna(0).abs() + 1
        df['ABAP Effort Safe'] = df['ABAP Effort Forecast (hrs)'].fillna(0) + 1

        return df

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def create_basic_charts(df):
    """Create the original working charts"""
    st.header("📊 Basic Analytics Overview")

    col1, col2 = st.columns(2)

    with col1:
        # WRICEF Type Distribution (Original Chart)
        st.subheader("WRICEF Type Distribution", 
                    help="Distribution of different WRICEF types in the portfolio")
        type_counts = df['WRICEF Type'].value_counts()
        fig1 = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.3,
            title="WRICEF Implementation Types"
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label',
                          hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Implementation Distribution (Original Chart)
        st.subheader("Implementation Distribution", 
                    help="Projects by implementation category")
        impl_counts = df['Implementation'].value_counts().head(10)
        fig2 = px.bar(
            x=impl_counts.index,
            y=impl_counts.values,
            color=impl_counts.values,
            color_continuous_scale='Blues',
            title="Top 10 Implementations by Project Count"
        )
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)

    # Complexity Distribution (Original Chart)
    st.subheader("Complexity Analysis", 
                help="Project complexity levels breakdown")
    complexity_counts = df['Complexity'].value_counts()
    fig3 = px.bar(
        x=complexity_counts.index,
        y=complexity_counts.values,
        color=complexity_counts.values,
        color_continuous_scale='RdYlBu_r',
        title="Project Complexity Distribution"
    )
    st.plotly_chart(fig3, use_container_width=True)

def create_timeline_analysis(df):
    """Create enhanced timeline analysis"""
    st.header("📅 Project Timeline Analysis")

    # Comprehensive Timeline (Enhanced Original Chart)
    st.subheader("Development ID Timeline", 
                help="Gantt chart showing project durations by Development ID")

    timeline_df = df.dropna(subset=['Dev Planned Delivery Date', 'Dev Actual Delivery Date']).head(30)
    if not timeline_df.empty:
        fig = px.timeline(
            timeline_df,
            x_start="Dev Planned Delivery Date",
            x_end="Dev Actual Delivery Date",
            y="Development ID",
            color="Implementation",
            hover_name="Project Name",
            title="Project Timeline: Development Planning to Completion",
            labels={'Dev Planned Delivery Date': 'Start Date', 'Dev Actual Delivery Date': 'End Date'}
        )
        fig.update_yaxes(autorange="reversed", categoryorder="total ascending")
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No timeline data available")

def create_fsd_analysis(df):
    """Create FSD process analysis - FIXED VERSION"""
    st.header("📋 FSD Process Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # FSD Timeline Analysis - FIXED: Using safe size parameter
        st.subheader("FSD Timeline Performance", 
                    help="Comparison of planned vs actual FSD walkthrough dates")

        fsd_data = df.dropna(subset=['FSD Planned Del Date', 'FSD Actual Walkthrough Date'])
        if not fsd_data.empty:
            fig1 = px.scatter(
                fsd_data,
                x='FSD Planned Del Date',
                y='FSD Actual Walkthrough Date',
                color='Complexity',
                size='ABAP Effort Safe',  # FIXED: Using safe size parameter
                hover_name='Project Name',
                title="FSD Planned vs Actual Walkthrough Dates"
            )

            # Add diagonal reference line manually
            min_date = min(fsd_data['FSD Planned Del Date'].min(), fsd_data['FSD Actual Walkthrough Date'].min())
            max_date = max(fsd_data['FSD Planned Del Date'].max(), fsd_data['FSD Actual Walkthrough Date'].max())

            fig1.add_shape(
                type="line",
                x0=min_date, y0=min_date,
                x1=max_date, y1=max_date,
                line=dict(color="red", width=2, dash="dash"),
                name="Perfect Timeline"
            )

            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No FSD timeline data available")

    with col2:
        # FSD Duration Distribution
        st.subheader("FSD Duration Analysis", 
                    help="Distribution of FSD processing times by complexity")

        duration_data = df.dropna(subset=['FSD Duration'])
        if not duration_data.empty:
            fig2 = px.violin(
                duration_data,
                x='Complexity',
                y='FSD Duration',
                color='Complexity',
                box=True,
                title="FSD Duration Distribution by Complexity"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No FSD duration data available")

def create_fut_analysis(df):
    """Create FUT analysis - FIXED VERSION"""
    st.header("🔍 FUT (Functional Unit Testing) Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # FUT Status Distribution
        st.subheader("FUT Status Overview", 
                    help="Current status distribution of FUT testing")

        fut_status = df['FUT Status'].value_counts()
        fig1 = px.pie(
            values=fut_status.values,
            names=fut_status.index,
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
            title="FUT Status Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # FUT Timeline Performance - FIXED: Using safe size parameter
        st.subheader("FUT Timeline Analysis", 
                    help="Planned vs actual FUT completion timeline")

        fut_timeline = df.dropna(subset=['Planned FUT Date', 'Actual FUT Date'])
        if not fut_timeline.empty:
            fig2 = px.scatter(
                fut_timeline,
                x='Planned FUT Date',
                y='Actual FUT Date',
                color='Priority of Delivery',
                size='FUT Duration Safe',  # FIXED: Using safe size parameter
                hover_name='Project Name',
                title="FUT Planned vs Actual Dates"
            )

            # Add diagonal reference line
            min_date = min(fut_timeline['Planned FUT Date'].min(), fut_timeline['Actual FUT Date'].min())
            max_date = max(fut_timeline['Planned FUT Date'].max(), fut_timeline['Actual FUT Date'].max())

            fig2.add_shape(
                type="line",
                x0=min_date, y0=min_date,
                x1=max_date, y1=max_date,
                line=dict(color="red", width=2, dash="dash"),
                name="On-Time Delivery"
            )

            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No FUT timeline data available")

def create_development_analysis(df):
    """Create development delivery analysis - FIXED VERSION"""
    st.header("🚀 Development Delivery Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Development Stage Distribution
        st.subheader("Development Stage Status", 
                    help="Current stage distribution of development projects")

        stage_counts = df['Stage'].value_counts().head(8)
        fig1 = px.bar(
            x=stage_counts.index,
            y=stage_counts.values,
            color=stage_counts.values,
            color_continuous_scale='RdYlBu_r',
            title="Development Stage Distribution"
        )
        fig1.update_xaxes(tickangle=45)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Development Duration vs Effort - FIXED: Using numeric vs numeric only
        st.subheader("Duration vs Effort Analysis", 
                    help="Relationship between development duration and effort")

        dev_data = df.dropna(subset=['DEV Duration', 'ABAP Effort Forecast (hrs)'])
        if not dev_data.empty:
            fig2 = px.scatter(
                dev_data,
                x='DEV Duration',
                y='ABAP Effort Forecast (hrs)',
                color='WRICEF Type',
                size='DEV Duration Safe',  # FIXED: Using safe size parameter
                hover_name='Project Name',
                title="Development Duration vs ABAP Effort"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No development duration data available")

def create_abap_analysis(df):
    """Create ABAP development analysis - FIXED VERSION"""
    st.header("💻 ABAP Development Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # ABAP Effort Accuracy - Works with numeric vs numeric
        st.subheader("ABAP Effort Forecast Accuracy", 
                    help="Comparison of forecasted vs actual ABAP effort")

        abap_data = df.dropna(subset=['ABAP Effort Forecast (hrs)', 'ABAP Actual Effort (hrs)'])
        if not abap_data.empty:
            fig1 = px.scatter(
                abap_data,
                x='ABAP Effort Forecast (hrs)',
                y='ABAP Actual Effort (hrs)',
                color='Complexity',
                hover_name='Project Name',
                title="ABAP Effort: Forecast vs Actual"
            )
            # Add perfect estimation line
            max_effort = max(abap_data['ABAP Effort Forecast (hrs)'].max(), 
                           abap_data['ABAP Actual Effort (hrs)'].max())
            fig1.add_shape(
                type="line",
                x0=0, y0=0, x1=max_effort, y1=max_effort,
                line=dict(color="red", width=2, dash="dash"),
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No ABAP effort data available")

    with col2:
        # ABAP Timeline Performance
        st.subheader("ABAP Delivery Timeline", 
                    help="ABAP planned vs actual delivery performance")

        abap_timeline = df.dropna(subset=['ABAP Planned Delivery Date', 'ABAP Actual Delivery Date'])
        if not abap_timeline.empty:
            abap_timeline['ABAP Delivery Variance'] = (
                abap_timeline['ABAP Actual Delivery Date'] - 
                abap_timeline['ABAP Planned Delivery Date']
            ).dt.days

            fig2 = px.histogram(
                abap_timeline,
                x='ABAP Delivery Variance',
                color='Complexity',
                title="ABAP Delivery Variance Distribution (Days)",
                nbins=20
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No ABAP timeline data available")

def create_team_analysis(df):
    """Create team member analysis - FIXED VERSION"""
    st.header("👥 Team Member Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Functional Owner Distribution
        st.subheader("Functional Owner Workload", 
                    help="Distribution of projects across functional owners")
        owner_counts = df['Functional Owner'].value_counts().head(10)
        if not owner_counts.empty:
            fig1 = px.bar(
                x=owner_counts.values,
                y=owner_counts.index,
                orientation='h',
                color=owner_counts.values,
                color_continuous_scale='Blues',
                title="Top 10 Functional Owners by Project Count"
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No functional owner data available")

    with col2:
        # ABAP Developer Distribution
        st.subheader("ABAP Developer Workload", 
                    help="Distribution of projects across ABAP developers")
        dev_counts = df['ABAP Developer '].value_counts().head(10)
        if not dev_counts.empty:
            fig2 = px.bar(
                x=dev_counts.values,
                y=dev_counts.index,
                orientation='h',
                color=dev_counts.values,
                color_continuous_scale='Greens',
                title="Top 10 ABAP Developers by Project Count"
            )
            fig2.update_layout(showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No ABAP developer data available")

    # Team Collaboration Matrix
    st.subheader("Team Collaboration Analysis", 
                help="Heatmap showing collaboration patterns between roles")

    # Create a simple collaboration count matrix
    collab_data = df.dropna(subset=['Functional Owner', 'Dev Lead '])
    if not collab_data.empty:
        collab_matrix = pd.crosstab(
            collab_data['Functional Owner'].head(8), 
            collab_data['Dev Lead '].head(8)
        )

        if not collab_matrix.empty:
            fig3 = px.imshow(
                collab_matrix.values,
                x=collab_matrix.columns,
                y=collab_matrix.index,
                color_continuous_scale='Viridis',
                title="Functional Owner - Dev Lead Collaboration Matrix"
            )
            fig3.update_xaxes(tickangle=45)
            st.plotly_chart(fig3, use_container_width=True)

def main():
    st.title("📊 WRICEF Tracker Comprehensive Analytics")

    df = load_data()
    if df.empty:
        st.warning("No data loaded. Please check your input file.")
        return

    st.success(f"✅ Successfully loaded {len(df)} records with {len(df.columns)} columns")

    # Key Metrics Dashboard
    st.header("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_projects = len(df)
        st.metric("Total Projects", total_projects, 
                 help="Total number of WRICEF implementations")

    with col2:
        avg_fsd_duration = df['FSD Duration'].mean()
        st.metric("Avg FSD Duration", f"{avg_fsd_duration:.1f} days",
                 help="Average FSD processing time")

    with col3:
        completed_projects = len(df[df['Stage'] == '06 - Dev Completed'])
        completion_rate = (completed_projects / total_projects) * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%",
                 help="Percentage of completed projects")

    with col4:
        avg_effort_variance = df['ABAP Effort Variance'].mean()
        st.metric("Avg Effort Variance", f"{avg_effort_variance:.1f} hrs",
                 help="Average difference between forecast and actual effort")

    st.markdown("---")

    # Main Analysis Sections - All Previous Charts Retained
    create_basic_charts(df)
    st.markdown("---")

    create_timeline_analysis(df)
    st.markdown("---")

    create_fsd_analysis(df)
    st.markdown("---")

    create_fut_analysis(df)
    st.markdown("---")

    create_development_analysis(df)
    st.markdown("---")

    create_abap_analysis(df)
    st.markdown("---")

    create_team_analysis(df)

    # Additional Insights
    st.header("💡 Additional Insights")

    col1, col2 = st.columns(2)

    with col1:
        # Implementation Performance
        st.subheader("Implementation Performance Comparison")
        impl_performance = df.groupby('Implementation').agg({
            'ABAP Effort Variance': 'mean',
            'FSD Duration': 'mean',
            'Development ID': 'count'
        }).round(2)

        if not impl_performance.empty:
            fig = px.scatter(
                impl_performance,
                x='FSD Duration',
                y='ABAP Effort Variance',
                size='Development ID',
                hover_name=impl_performance.index,
                title="Implementation Performance Matrix"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Priority Distribution
        st.subheader("Priority Analysis")
        priority_counts = df['Priority of Delivery'].value_counts()
        if not priority_counts.empty:
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Priority Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()