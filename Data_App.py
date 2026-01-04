import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# Page config
st.set_page_config(
    page_title="Data Cleaning Tool",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ultra-modern CSS
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #16213e 50%, #0f3460 100%) !important;
        min-height: 100vh;
        font-family: 'Segoe UI', Trebuchet MS, sans-serif;
    }
    
    .stApp {
        background: transparent !important;
    }
    
    .main {
        background: transparent !important;
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(34, 197, 94, 0.5); }
        50% { text-shadow: 0 0 40px rgba(34, 197, 94, 0.8); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .header-title {
        font-size: 3em;
        font-weight: 900;
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        letter-spacing: -1px;
        animation: glow 3s ease-in-out infinite;
    }
    
    .header-subtitle {
        font-size: 1.1em;
        color: #cbd5e1;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        backdrop-filter: blur(10px);
        animation: slideIn 0.6s ease-out;
    }
    
    .stat-value {
        font-size: 2em;
        font-weight: 800;
        color: #22c55e;
        margin: 10px 0;
    }
    
    .stat-label {
        color: #94a3b8;
        font-size: 0.9em;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 24px rgba(34, 197, 94, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 12px 32px rgba(34, 197, 94, 0.5) !important;
    }
    
    .section-title {
        font-size: 1.5em;
        font-weight: 800;
        color: #e2e8f0;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(34, 197, 94, 0.3);
    }
    
    .info-box {
        background: rgba(34, 197, 94, 0.05);
        border-left: 4px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        color: #cbd5e1;
    }
    
    .footer {
        text-align: center;
        color: #94a3b8;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid rgba(148, 163, 184, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
if "original_df" not in st.session_state:
    st.session_state.original_df = None
if "cleaning_log" not in st.session_state:
    st.session_state.cleaning_log = []

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <div class="header-title">🧹 Data Cleaning Tool by Robert Marsh Deku</div>
    <div class="header-subtitle">Automatically clean, validate, and transform your messy data</div>
</div>
""", unsafe_allow_html=True)

# File upload
st.markdown("### 📤 Upload Your Data")
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    # Load data
    st.session_state.df = pd.read_csv(uploaded_file)
    st.session_state.original_df = st.session_state.df.copy()
    
    # Display stats
    st.markdown("### 📊 Data Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Rows</div>
            <div class="stat-value">{len(st.session_state.df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Total Columns</div>
            <div class="stat-value">{len(st.session_state.df.columns)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        missing = st.session_state.df.isnull().sum().sum()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Missing Values</div>
            <div class="stat-value">{missing:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        duplicates = st.session_state.df.duplicated().sum()
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Duplicate Rows</div>
            <div class="stat-value">{duplicates:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Preview original data
    with st.expander("👁️ Preview Original Data"):
        st.dataframe(st.session_state.df.head(10), use_container_width=True)
    
    # Cleaning options
    st.markdown("### 🛠️ Cleaning Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Handle Missing Values")
        
        missing_cols = st.session_state.df.columns[st.session_state.df.isnull().any()].tolist()
        
        if missing_cols:
            missing_strategy = st.radio(
                "Strategy for missing values:",
                ["Drop rows with missing values", "Fill with mean (numeric)", "Fill with median (numeric)", "Fill with mode", "Fill with custom value"],
                key="missing_strategy"
            )
            
            if st.button("🔧 Apply Missing Values Handling", use_container_width=True, key="apply_missing"):
                before_count = len(st.session_state.df)
                
                if missing_strategy == "Drop rows with missing values":
                    st.session_state.df = st.session_state.df.dropna()
                    st.session_state.cleaning_log.append(f"Dropped {before_count - len(st.session_state.df)} rows with missing values")
                
                elif missing_strategy == "Fill with mean (numeric)":
                    numeric_cols = st.session_state.df.select_dtypes(include=[np.number]).columns
                    st.session_state.df[numeric_cols] = st.session_state.df[numeric_cols].fillna(st.session_state.df[numeric_cols].mean())
                    st.session_state.cleaning_log.append("Filled numeric columns with mean")
                
                elif missing_strategy == "Fill with median (numeric)":
                    numeric_cols = st.session_state.df.select_dtypes(include=[np.number]).columns
                    st.session_state.df[numeric_cols] = st.session_state.df[numeric_cols].fillna(st.session_state.df[numeric_cols].median())
                    st.session_state.cleaning_log.append("Filled numeric columns with median")
                
                elif missing_strategy == "Fill with mode":
                    for col in st.session_state.df.columns:
                        if not st.session_state.df[col].mode().empty:
                            st.session_state.df[col] = st.session_state.df[col].fillna(st.session_state.df[col].mode()[0])
                        else:
                            st.session_state.df[col] = st.session_state.df[col].fillna("Unknown")
                    st.session_state.cleaning_log.append("Filled columns with mode")
                
                st.success("✅ Missing values handled!")
        else:
            st.info("✅ No missing values found!")
    
    with col2:
        st.markdown("#### Handle Duplicates")
        
        dup_count = st.session_state.df.duplicated().sum()
        
        if dup_count > 0:
            if st.button("🗑️ Remove Duplicate Rows", use_container_width=True, key="remove_duplicates"):
                st.session_state.df = st.session_state.df.drop_duplicates()
                st.session_state.cleaning_log.append(f"Removed {dup_count} duplicate rows")
                st.success(f"✅ Removed {dup_count} duplicate rows!")
        else:
            st.info("✅ No duplicate rows found!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Remove Columns")
        
        cols_to_remove = st.multiselect("Select columns to remove:", st.session_state.df.columns, key="cols_remove")
        
        if st.button("❌ Remove Selected Columns", use_container_width=True, key="remove_cols"):
            if cols_to_remove:
                st.session_state.df = st.session_state.df.drop(columns=cols_to_remove)
                st.session_state.cleaning_log.append(f"Removed columns: {', '.join(cols_to_remove)}")
                st.success("✅ Columns removed!")
            else:
                st.warning("Please select columns to remove")
    
    with col2:
        st.markdown("#### Data Type Conversion")
        
        col_to_convert = st.selectbox("Select column to convert:", st.session_state.df.columns, key="col_convert")
        new_dtype = st.selectbox("Convert to:", ["int", "float", "string", "datetime"], key="new_dtype")
        
        if st.button("🔄 Convert Data Type", use_container_width=True, key="convert_dtype"):
            try:
                if new_dtype == "int":
                    st.session_state.df[col_to_convert] = st.session_state.df[col_to_convert].astype(int)
                elif new_dtype == "float":
                    st.session_state.df[col_to_convert] = st.session_state.df[col_to_convert].astype(float)
                elif new_dtype == "string":
                    st.session_state.df[col_to_convert] = st.session_state.df[col_to_convert].astype(str)
                elif new_dtype == "datetime":
                    st.session_state.df[col_to_convert] = pd.to_datetime(st.session_state.df[col_to_convert])
                
                st.session_state.cleaning_log.append(f"Converted {col_to_convert} to {new_dtype}")
                st.success(f"✅ Converted to {new_dtype}!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Remove Whitespace")
        
        if st.button("🔲 Trim Whitespace from All Text", use_container_width=True, key="trim_whitespace"):
            str_cols = st.session_state.df.select_dtypes(include=['object']).columns
            for col in str_cols:
                st.session_state.df[col] = st.session_state.df[col].str.strip()
            st.session_state.cleaning_log.append("Trimmed whitespace from text columns")
            st.success("✅ Whitespace removed!")
    
    with col2:
        st.markdown("#### Convert to Lowercase")
        
        if st.button("🔡 Convert Text to Lowercase", use_container_width=True, key="lowercase"):
            str_cols = st.session_state.df.select_dtypes(include=['object']).columns
            for col in str_cols:
                st.session_state.df[col] = st.session_state.df[col].str.lower()
            st.session_state.cleaning_log.append("Converted text to lowercase")
            st.success("✅ Text converted to lowercase!")
    
    # Preview cleaned data
    st.markdown("### 👁️ Preview Cleaned Data")
    with st.expander("View cleaned data", expanded=True):
        st.dataframe(st.session_state.df.head(10), use_container_width=True)
    
    # Cleaning log
    if st.session_state.cleaning_log:
        st.markdown("### 📋 Cleaning Log")
        for i, log in enumerate(st.session_state.cleaning_log, 1):
            st.markdown(f"<div class='info-box'>{i}. {log}</div>", unsafe_allow_html=True)
    
    # Download cleaned data
    st.markdown("### 📥 Download Cleaned Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = st.session_state.df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_buffer = io.BytesIO()
        st.session_state.df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        st.download_button(
            label="📊 Download as Excel",
            data=excel_buffer,
            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        json_str = st.session_state.df.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Download as JSON",
            data=json_str,
            file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    # Reset button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Reset to Original", use_container_width=True, key="reset_data"):
            st.session_state.df = st.session_state.original_df.copy()
            st.session_state.cleaning_log = []
            st.success("✅ Reset to original data!")

else:
    st.markdown("""
    <div class="info-box">
    <strong>👋 Welcome to Data Cleaning Tool!</strong><br><br>
    This tool helps you automatically clean and prepare your data. Simply upload a CSV file and you can:<br><br>
    ✅ Handle missing values (drop, fill with mean/median/mode)<br>
    ✅ Remove duplicate rows<br>
    ✅ Delete unnecessary columns<br>
    ✅ Convert data types<br>
    ✅ Clean whitespace<br>
    ✅ Convert text to lowercase<br>
    ✅ Download cleaned data in CSV, Excel, or JSON<br><br>
    Start by uploading a CSV file above!
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <p>🚀 Data Cleaning Tool | Built with Streamlit & Pandas</p>
</div>
""", unsafe_allow_html=True)