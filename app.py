import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import io

from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)

st.title("CSV Viewer App")

# Upload CSV from local machine
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df)

    # Display basic statistics
    st.subheader("Data Statistics")
    st.write(df.describe())

    # Plotting
    st.subheader("Data Visualization")
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    if not numeric_columns.empty:
        column_to_plot = st.selectbox("Select a column to plot", numeric_columns)
        plt.figure(figsize=(10, 4))
        df[column_to_plot].hist()
        st.pyplot(plt)
    else:
        st.write("No numeric columns to plot.")

    # Display images if URLs are present
    image_columns = df.select_dtypes(include=['object']).columns
    for col in image_columns:
        if df[col].str.contains('http').any():
            st.subheader(f"Images from column: {col}")
            for url in df[col].dropna():
                if url.startswith('http'):
                    st.image(url, width=150)
            break  # Display images from the first column with URLs

# Optionally load CSV from S3
st.subheader("Load CSV from AWS S3")
bucket_name = st.text_input("Enter S3 Bucket Name")
file_key = st.text_input("Enter S3 File Key (e.g., folder/filename.csv)")

if st.button("Load from S3"):
    if bucket_name and file_key:
        try:
            s3 = boto3.client('s3')
            obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            df_s3 = pd.read_csv(io.BytesIO(obj['Body'].read()))
            st.success("File loaded successfully from S3!")
            st.dataframe(df_s3)
        except Exception as e:
            st.error(f"Error loading file from S3: {e}")
    else:
        st.warning("Please provide both bucket name and file key.")
