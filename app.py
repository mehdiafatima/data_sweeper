import streamlit as st
import pandas as pd
import os 
from io import BytesIO

# This must be the first Streamlit command
st.set_page_config(page_title="💽 Data Sweeper", layout='wide')

# Custom styling after set_page_config
st.markdown("""
<style>
    /* Base styles */
    :root {
        --dark-blue: #1E3D59;
        --light-blue: #4A90E2;
    }

    /* Main container */
    .main {
        background: transparent;
        padding: 15px;
        max-width: 100%;
    }

    /* Remove all white backgrounds */
    .stDataFrame, div[data-testid="stFileUploader"], .stCheckbox, .stRadio, 
    .stButton > button, .stMarkdown, .stSelectbox, .stMultiSelect {
        background: transparent !important;
    }

    /* Default text styling for large screens */
    body, .stMarkdown, .stDataFrame, div[data-testid="stFileUploader"],
    .stCheckbox, .stRadio, .stSelectbox, .stMultiSelect, p, span {
        color: var(--dark-blue) !important;
    }

    /* Button styling */
    .stButton > button {
        border: 2px solid var(--light-blue);
        border-radius: 8px;
        padding: clamp(0.4rem, 2vw, 0.8rem) clamp(0.8rem, 4vw, 1.5rem);
        transition: all 0.3s ease;
        font-size: clamp(16px, 3vw, 18px) !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background: var(--light-blue) !important;
        color: white !important;
        transform: translateY(-2px);
    }

    /* Headers styling */
    .stSubheader, h1, h2, h3 {
        color: var(--dark-blue) !important;
        font-size: clamp(18px, 4vw, 24px) !important;
        font-weight: 600 !important;
        margin: 15px 0 !important;
    }

    /* DataFrame styling */
    .dataframe {
        border: none !important;
        width: 100%;
        font-size: clamp(12px, 1.5vw, 14px);
    }
    .dataframe thead th {
        color: var(--dark-blue) !important;
        padding: clamp(5px, 2vw, 10px) !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--light-blue);
        min-width: 200px;
    }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        border: 2px solid var(--light-blue);
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }

    /* Mobile styles */
    @media screen and (max-width: 768px) {
        /* Change all text to white on mobile */
        body, .stMarkdown, .stDataFrame, div[data-testid="stFileUploader"],
        .stCheckbox, .stRadio, .stSelectbox, .stMultiSelect,
        .stSubheader, h1, h2, h3, p, span, label, 
        .dataframe thead th, .dataframe tbody td {
            color: white !important;
        }

        /* Button styling for mobile */
        .stButton > button {
            color: white !important;
            border-color: white;
        }
        .stButton > button:hover {
            background: white !important;
            color: var(--light-blue) !important;
        }

        /* File uploader border for mobile */
        [data-testid="stFileUploader"] {
            border-color: white;
        }

        /* Dark overlay background for better white text readability */
        .main {
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7));
        }

        /* Columns adjustment */
        .stColumns {
            flex-direction: column;
        }
        .stColumn {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }

    /* Extra small screens */
    @media screen and (max-width: 480px) {
        .dataframe {
            font-size: clamp(12px, 2vw, 14px);
        }
        .stButton > button {
            padding: 0.4rem 0.8rem;
        }
        .stMarkdown {
            font-size: clamp(14px, 2vw, 16px);
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("💽 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization! ✨")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

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
                try:
                    if conversion_type == "CSV":
                        df.to_csv(buffer, index=False)
                        file_name = file.name.replace(file_ext, ".csv")
                        mime_type = "text/csv"
                    elif conversion_type == "Excel":
                        try:
                            import openpyxl
                            df.to_excel(buffer, index=False)
                            file_name = file.name.replace(file_ext, ".xlsx")
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        except ImportError:
                            st.error("Excel conversion requires openpyxl package. Please install it or choose CSV format.")
                            continue
                    
                    buffer.seek(0)
                    
                    # Download Button
                    st.download_button(
                        label=f"⤵️ Download {file_name} as {conversion_type}",
                        data=buffer,
                        file_name=file_name,
                        mime=mime_type
                    )
                    st.success("✅ File processed successfully!")
                except Exception as e:
                    st.error(f"Error during conversion: {str(e)}")
