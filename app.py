import streamlit as st
import pandas as pd
import os 
from io import BytesIO

# This must be the first Streamlit command
st.set_page_config(page_title="💽 Data sweeper", layout='wide')

# Custom styling after set_page_config
st.markdown("""
<style>
    /* Responsive container */
    .main {
        padding: 15px;
        max-width: 100%;
    }

    /* Responsive card sections */
    .stDataFrame, div[data-testid="stFileUploader"] {
        background: white;
        padding: clamp(10px, 3vw, 20px);  /* Responsive padding */
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
        width: 100%;
        overflow-x: auto;  /* Horizontal scroll for tables on mobile */
    }

    /* Responsive file uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #4A90E2;
        background: #F8FAFC;
        min-width: 200px;
    }

    /* Responsive buttons */
    .stButton > button {
        background: #4A90E2;
        color: white !important;
        border-radius: 8px;
        padding: clamp(0.4rem, 2vw, 0.8rem) clamp(0.8rem, 4vw, 1.5rem);
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
        width: 100%;  /* Full width on mobile */
        font-size: clamp(14px, 2vw, 16px);  /* Responsive font size */
    }

    /* Responsive checkbox and radio */
    .stCheckbox, .stRadio {
        background: white;
        padding: clamp(10px, 2vw, 15px);
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        width: 100%;
    }

    /* Responsive messages */
    .stSuccess, .stError {
        padding: clamp(10px, 3vw, 20px);
        border-radius: 8px;
        width: 100%;
        font-size: clamp(14px, 2vw, 16px);
    }

    /* Responsive DataFrame */
    .dataframe {
        border: none !important;
        width: 100%;
        font-size: clamp(12px, 1.5vw, 14px);  /* Responsive font size */
    }
    .dataframe thead th {
        background-color: #4A90E2 !important;
        color: white !important;
        padding: clamp(5px, 2vw, 10px) !important;
        white-space: nowrap;  /* Prevent header text wrapping */
    }

    /* Responsive section headers */
    .stSubheader {
        font-size: clamp(1rem, 2.5vw, 1.2rem);
        padding: clamp(0.5rem, 2vw, 1rem) 0;
    }

    /* Responsive download button */
    [data-testid="stDownloadButton"] button {
        width: 100%;
        max-width: 400px;  /* Maximum width on larger screens */
        margin: 0 auto;
    }

    /* Media queries for different screen sizes */
    @media screen and (max-width: 768px) {
        /* Adjustments for tablets */
        .stColumns {
            flex-direction: column;
        }
        .stColumn {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }

    @media screen and (max-width: 480px) {
        /* Adjustments for mobile */
        .dataframe {
            font-size: 12px;
        }
        .stButton > button {
            padding: 0.4rem 0.8rem;
        }
        .stMarkdown {
            font-size: 14px;
        }
    }

    /* Ensure text readability on all screens */
    * {
        word-wrap: break-word;
        overflow-wrap: break-word;
    }

    /* Smooth scrolling for better mobile experience */
    html {
        scroll-behavior: smooth;
    }

    /* Better touch targets for mobile */
    button, input[type="checkbox"], input[type="radio"] {
        min-height: 44px;  /* Minimum touch target size */
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
