import streamlit as st
import pandas as pd

# Define thresholds and criteria for identifying potential fake followers
high_numerical_ratio_username = 0.2
high_numerical_ratio_fullname = 0.1
short_fullname_threshold = 1
short_bio_threshold = 50
low_posts_threshold = 20
low_followers_threshold = 500

# Function to check if the dataset contains all required columns
def validate_columns(df):
    required_columns = [
        'profile pic',
        'nums/length username',
        'fullname words',
        'nums/length fullname',
        'name==username',
        'description length',
        'external URL',
        'private',
        '#posts',
        '#followers'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns

# Function to process the data and identify potential fake followers
def identify_fake_followers(df):
    # Convert boolean columns to boolean type
    df['profile pic'] = df['profile pic'].astype(bool)
    df['name==username'] = df['name==username'].astype(bool)
    df['external URL'] = df['external URL'].astype(bool)
    df['private'] = df['private'].astype(bool)

    # Convert numerical columns to appropriate types
    df['nums/length username'] = df['nums/length username'].astype(float)
    df['fullname words'] = df['fullname words'].astype(int)
    df['nums/length fullname'] = df['nums/length fullname'].astype(float)
    df['description length'] = df['description length'].astype(int)
    df['#posts'] = df['#posts'].astype(int)
    df['#followers'] = df['#followers'].astype(int)

    # Flag potential fake followers
    df['Potential Fake'] = (
        (df['profile pic'] == False) &
        ((df['nums/length username'] > high_numerical_ratio_username) |
        (df['fullname words'] <= short_fullname_threshold) |
        (df['nums/length fullname'] > high_numerical_ratio_fullname) |
        (df['name==username'] == True) |
        (df['description length'] < short_bio_threshold) |
        (df['external URL'] == False) |
        (df['private'] == True)) &
        ((df['#posts'] < low_posts_threshold) & (df['#followers'] < low_followers_threshold))
    )
    
    # Output the list of potential fake followers
    potential_fake_followers = df[df['Potential Fake']]
    
    return potential_fake_followers

# Streamlit app
def main():
    st.title("Fake Followers Detection")

    st.write("""
    ### Instructions
    Please upload a CSV file that contains the following columns:
    - `profile pic` (boolean)
    - `nums/length username` (float)
    - `fullname words` (integer)
    - `nums/length fullname` (float)
    - `name==username` (boolean)
    - `description length` (integer)
    - `external URL` (boolean)
    - `private` (boolean)
    - `#posts` (integer)
    - `#followers` (integer)
    """)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        valid, missing_cols = validate_columns(df)
        
        if not valid:
            st.error(f"The uploaded file is missing the following required columns: {', '.join(missing_cols)}")
        else:
            st.write("Dataset loaded successfully!")
            st.write(f"Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")
            
            # Process data
            potential_fake_followers = identify_fake_followers(df)
            
            # Display results
            st.write(f"Number of potential fake followers identified: {len(potential_fake_followers)}")
            st.write(potential_fake_followers)
            
            # Save results and download link
            potential_fake_followers_csv = potential_fake_followers.to_csv(index=False)
            st.download_button(
                label="Download Potential Fake Followers",
                data=potential_fake_followers_csv,
                file_name='potential_fake_followers.csv',
                mime='text/csv'
            )
            
            # Generate and display report
            report_content = f"""
            Criteria for Potential Fake Followers:
            1. No Profile Picture
            2. High Ratio of Numerical Characters in Username (> {high_numerical_ratio_username})
            3. Short Full Name (<= {short_fullname_threshold} words)
            4. High Ratio of Numerical Characters in Full Name (> {high_numerical_ratio_fullname})
            5. Username Equals Full Name
            6. Short Bio (<= {short_bio_threshold} characters)
            7. No External URL
            8. Private Profile
            9. Low Number of Posts (< {low_posts_threshold}) and Low Number of Followers (< {low_followers_threshold})

            Number of Potential Fake Followers Identified: {len(potential_fake_followers)}
            """
            st.text_area("Report", report_content, height=300)

if __name__ == "__main__":
    main()
