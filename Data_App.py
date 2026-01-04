import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
from scipy import stats

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
if "selected_operations" not in st.session_state:
    st.session_state.selected_operations = {}

# Header
st.markdown("""
<div style="margin-bottom: 20px;">
    <div class="header-title">🧹 Data Cleaning Tool by Deku Robert Marsh</div>
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
    st.markdown("### 🛠️ Cleaning Operations (Select Multiple)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Handle Missing Values")
        
        missing_cols = st.session_state.df.columns[st.session_state.df.isnull().any()].tolist()
        
        if missing_cols:
            missing_strategy = st.radio(
                "Strategy for missing values:",
                ["Drop rows with missing values", "Fill with mean (numeric)", "Fill with median (numeric)", "Fill with mode"],
                key="missing_strategy"
            )
            
            st.session_state.selected_operations["missing"] = {
                "enabled": st.checkbox("Apply missing values handling", key="apply_missing"),
                "strategy": missing_strategy
            }
        else:
            st.info("✅ No missing values found!")
    
    with col2:
        st.markdown("#### Handle Duplicates")
        
        dup_count = st.session_state.df.duplicated().sum()
        
        if dup_count > 0:
            st.session_state.selected_operations["duplicates"] = {
                "enabled": st.checkbox("Remove duplicate rows", key="remove_duplicates")
            }
        else:
            st.info("✅ No duplicate rows found!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Remove Columns")
        
        cols_to_remove = st.multiselect("Select columns to remove:", st.session_state.df.columns, key="cols_remove")
        
        st.session_state.selected_operations["remove_cols"] = {
            "enabled": st.checkbox("Apply column removal", key="apply_cols"),
            "columns": cols_to_remove
        }
    
    with col2:
        st.markdown("#### Standardize Text Case")
        
        st.session_state.selected_operations["lowercase"] = {
            "enabled": st.checkbox("Convert text to lowercase", key="apply_lowercase")
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Remove Whitespace")
        
        st.session_state.selected_operations["trim_whitespace"] = {
            "enabled": st.checkbox("Trim whitespace from text", key="apply_trim")
        }
    
    with col2:
        st.markdown("#### Remove Special Characters")
        
        st.session_state.selected_operations["special_chars"] = {
            "enabled": st.checkbox("Remove special characters from text", key="apply_special")
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Data Type Conversion")
        
        col_to_convert = st.selectbox("Select column to convert:", st.session_state.df.columns, key="col_convert")
        new_dtype = st.selectbox("Convert to:", ["int", "float", "string", "datetime"], key="new_dtype")
        
        st.session_state.selected_operations["dtype_convert"] = {
            "enabled": st.checkbox("Apply data type conversion", key="apply_dtype"),
            "column": col_to_convert,
            "new_dtype": new_dtype
        }
    
    with col2:
        st.markdown("#### Detect & Remove Outliers")
        
        outlier_cols = st.multiselect("Select numeric columns for outlier detection:", 
                                      st.session_state.df.select_dtypes(include=[np.number]).columns,
                                      key="outlier_cols")
        
        st.session_state.selected_operations["outliers"] = {
            "enabled": st.checkbox("Remove outliers (IQR method)", key="apply_outliers"),
            "columns": outlier_cols
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Rename Columns")
        
        st.session_state.selected_operations["rename_cols"] = {
            "enabled": st.checkbox("Standardize column names", key="apply_rename")
        }
    
    with col2:
        st.markdown("#### Fill Missing with Custom Value")
        
        custom_value = st.text_input("Custom value for missing data:", "N/A", key="custom_value")
        
        st.session_state.selected_operations["custom_fill"] = {
            "enabled": st.checkbox("Fill with custom value", key="apply_custom"),
            "value": custom_value
        }
    
    # Apply all selected operations
    st.markdown("---")
    if st.button("▶️ Apply All Selected Operations", use_container_width=True, key="apply_all"):
        operations_applied = []
        df_working = st.session_state.df.copy()
        
        # Missing values handling
        if st.session_state.selected_operations.get("missing", {}).get("enabled"):
            strategy = st.session_state.selected_operations["missing"]["strategy"]
            before_count = len(df_working)
            
            if strategy == "Drop rows with missing values":
                df_working = df_working.dropna()
                operations_applied.append(f"Dropped {before_count - len(df_working)} rows with missing values")
            
            elif strategy == "Fill with mean (numeric)":
                numeric_cols = df_working.select_dtypes(include=[np.number]).columns
                df_working[numeric_cols] = df_working[numeric_cols].fillna(df_working[numeric_cols].mean())
                operations_applied.append("Filled numeric columns with mean")
            
            elif strategy == "Fill with median (numeric)":
                numeric_cols = df_working.select_dtypes(include=[np.number]).columns
                df_working[numeric_cols] = df_working[numeric_cols].fillna(df_working[numeric_cols].median())
                operations_applied.append("Filled numeric columns with median")
            
            elif strategy == "Fill with mode":
                for col in df_working.columns:
                    if not df_working[col].mode().empty:
                        df_working[col] = df_working[col].fillna(df_working[col].mode()[0])
                    else:
                        df_working[col] = df_working[col].fillna("Unknown")
                operations_applied.append("Filled columns with mode")
        
        # Remove duplicates
        if st.session_state.selected_operations.get("duplicates", {}).get("enabled"):
            dup_count = df_working.duplicated().sum()
            df_working = df_working.drop_duplicates()
            operations_applied.append(f"Removed {dup_count} duplicate rows")
        
        # Remove columns
        if st.session_state.selected_operations.get("remove_cols", {}).get("enabled"):
            cols_to_remove = st.session_state.selected_operations["remove_cols"]["columns"]
            if cols_to_remove:
                df_working = df_working.drop(columns=cols_to_remove)
                operations_applied.append(f"Removed columns: {', '.join(cols_to_remove)}")
        
        # Convert to lowercase
        if st.session_state.selected_operations.get("lowercase", {}).get("enabled"):
            str_cols = df_working.select_dtypes(include=['object']).columns
            for col in str_cols:
                df_working[col] = df_working[col].str.lower()
            operations_applied.append("Converted text to lowercase")
        
        # Trim whitespace
        if st.session_state.selected_operations.get("trim_whitespace", {}).get("enabled"):
            str_cols = df_working.select_dtypes(include=['object']).columns
            for col in str_cols:
                df_working[col] = df_working[col].str.strip()
            operations_applied.append("Trimmed whitespace from text columns")
        
        # Remove special characters
        if st.session_state.selected_operations.get("special_chars", {}).get("enabled"):
            str_cols = df_working.select_dtypes(include=['object']).columns
            for col in str_cols:
                df_working[col] = df_working[col].str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)
            operations_applied.append("Removed special characters from text")
        
        # Data type conversion
        if st.session_state.selected_operations.get("dtype_convert", {}).get("enabled"):
            try:
                col = st.session_state.selected_operations["dtype_convert"]["column"]
                dtype = st.session_state.selected_operations["dtype_convert"]["new_dtype"]
                
                if dtype == "int":
                    df_working[col] = df_working[col].astype(int)
                elif dtype == "float":
                    df_working[col] = df_working[col].astype(float)
                elif dtype == "string":
                    df_working[col] = df_working[col].astype(str)
                elif dtype == "datetime":
                    df_working[col] = pd.to_datetime(df_working[col])
                
                operations_applied.append(f"Converted {col} to {dtype}")
            except Exception as e:
                st.error(f"Error converting {col}: {str(e)}")
        
        # Remove outliers
        if st.session_state.selected_operations.get("outliers", {}).get("enabled"):
            outlier_cols = st.session_state.selected_operations["outliers"]["columns"]
            if outlier_cols:
                before_count = len(df_working)
                
                for col in outlier_cols:
                    Q1 = df_working[col].quantile(0.25)
                    Q3 = df_working[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df_working = df_working[(df_working[col] >= lower_bound) & (df_working[col] <= upper_bound)]
                
                operations_applied.append(f"Removed {before_count - len(df_working)} outlier rows")
        
        # Rename columns
        if st.session_state.selected_operations.get("rename_cols", {}).get("enabled"):
            df_working.columns = df_working.columns.str.lower().str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)
            operations_applied.append("Standardized column names")
        
        # Fill with custom value
        if st.session_state.selected_operations.get("custom_fill", {}).get("enabled"):
            custom_val = st.session_state.selected_operations["custom_fill"]["value"]
            df_working = df_working.fillna(custom_val)
            operations_applied.append(f"Filled missing values with '{custom_val}'")
        
        # Update main dataframe and log
        st.session_state.df = df_working
        st.session_state.cleaning_log.extend(operations_applied)
        
        if operations_applied:
            st.success(f"✅ Applied {len(operations_applied)} operation(s)!")
        else:
            st.warning("⚠️ No operations selected")
    
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
            st.session_state.selected_operations = {}
            st.success("✅ Reset to original data!")

else:
    st.markdown("""
    <div class="info-box">
    <strong>👋 Welcome to Advanced Data Cleaning Tool!</strong><br><br>
    This tool helps you automatically clean and prepare your data. Simply upload a CSV file and you can:<br><br>
    ✅ Handle missing values (drop, fill with mean/median/mode/custom)<br>
    ✅ Remove duplicate rows<br>
    ✅ Delete unnecessary columns<br>
    ✅ Convert data types<br>
    ✅ Clean whitespace<br>
    ✅ Standardize text to lowercase<br>
    ✅ Remove special characters<br>
    ✅ Detect and remove outliers (IQR method)<br>
    ✅ Rename columns to standard format<br>
    ✅ Download cleaned data in CSV, Excel, or JSON<br>
    ✅ <strong>Apply multiple operations simultaneously!</strong><br><br>
    Start by uploading a CSV file above!
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <p>🚀 Advanced Data Cleaning Tool | Built with Streamlit & Pandas</p>
</div>
""", unsafe_allow_html=True)