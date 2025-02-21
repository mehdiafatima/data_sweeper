import streamlit as st
import pandas as pd
import os 
from io import BytesIO

# This must be the first Streamlit command
st.set_page_config(page_title="💽 Data sweeper", layout='wide')

# Custom styling after set_page_config
st.markdown("""
<style>
    /* Card-like sections */
    .stDataFrame, div[data-testid="stFileUploader"] {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border: 2px dashed #4A90E2;
        background: #F8FAFC;
    }

    /* Button styling with white text */
    .stButton > button {
        background: #4A90E2;
        color: white !important;  /* Force white text always */
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #357ABD;
        box-shadow: 0 5px 10px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        color: white !important;  /* Force white text on hover */
    }

    /* Checkbox and radio styling */
    .stCheckbox, .stRadio {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Success message styling */
    .stSuccess {
        background: #28a745;
        padding: 20px;
        border-radius: 8px;
        color: white;
    }

    /* Error message styling */
    .stError {
        background: #dc3545;
        padding: 20px;
        border-radius: 8px;
        color: white;
    }

    /* DataFrame styling */
    .dataframe {
        border: none !important;
    }
    .dataframe thead th {
        background-color: #4A90E2 !important;
        color: white !important;
        padding: 10px !important;
    }
    .dataframe tbody tr:nth-child(even) {
        background-color: #f8f9fa !important;
    }
    .dataframe tbody tr:hover {
        background-color: #f1f7fe !important;
    }

    /* Section headers */
    .stSubheader {
        font-size: 1.2rem;
        color: #2C3E50;
        font-weight: 600;
        padding: 1rem 0;
        border-bottom: 2px solid #4A90E2;
        margin-bottom: 1rem;
    }

    /* Download button specific styling */
    [data-testid="stDownloadButton"] button {
        background: #28a745;
        width: 100%;
        color: white !important;  /* Force white text */
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #218838;
        color: white !important;  /* Force white text on hover */
    }
</style>
""", unsafe_allow_html=True)

st.title("💽 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization! ✨")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"],
accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display info about the file
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size/1024:.2f} KB")

        # Show 5 rows of our df
        st.write("🔍 Preview the Head of the Dataframe")
        st.dataframe(df.head())

        # Options for data cleaning
        st.subheader("⚙️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
                
            with col2:
                if st.button(f"Fill Missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been Filled!")

            # Choose Specific Columns to keep or Convert
            st.subheader("👆 Select Columns to Convert")
            columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
            df = df[columns]

            # Create Some Visualizations
            st.subheader("📈 Data Visualization")
            if st.checkbox(f"Show Visualization for {file.name}"):
                st.bar_chart(df.select_dtypes(include='number').iloc[:,:2])

            # Convert the File -> CSV to Excel 
            st.subheader("🔃 Conversion Options")  
            conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)  
            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)

                # Download Button
                st.download_button(
                    label=f"⤵️ Download {file_name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                st.success("✅ File processed successfully!")
