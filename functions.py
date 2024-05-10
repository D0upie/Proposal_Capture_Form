import streamlit as st
import pandas as pd
import csv, pyodbc
import snowflake.connector
import uuid
from datetime import datetime

# Define radio options
radio_options = ["None", "Low", "Moderate", "High"]


def generate_session_id():
    # Generate a UUID4 session ID
    session_id = str(uuid.uuid4())
    st.session_state.session_id =  session_id


# Function to iterate through the "Key Challenges" section of the proposal sections
def radio_select(selected_solution, key_challenges, parent_list=""):
    # Retrieve client's name from session state
    client_name = st.session_state.client_name
    session_id = st.session_state.session_id

    for challenge, challenge_value in key_challenges.items():
        if isinstance(challenge_value, dict):  # Check if the challenge is a nested dictionary
            with st.expander(challenge):
                # Pass the parent list's name to the recursive call
                radio_select(selected_solution, challenge_value, parent_list=challenge)
        else:
            # Get the selected option from session state
            selected_option = st.session_state.selected_options.get(challenge_value, radio_options[0])
            # Get the corresponding user input from session state
            user_input = st.session_state.selected_options.get(f"{challenge_value}_input", "")

            # Include the parent list's name in the Sub-Category value
            sub_category = f"{parent_list} - {challenge}" if parent_list else challenge

            # Create two columns
            col1, col2 = st.columns([1, 2])

            with col1:
                # Display radio input on left
                selected_option = st.radio(f"Select level for {challenge}:", radio_options, index=radio_options.index(selected_option), key=f"{challenge_value}", horizontal=True)

            with col2:
                # Display text input boxes based on dropdown selection on right
                if selected_option != "None":
                    user_input = st.text_area(f"Enter details for {challenge} ({selected_option}):", value=user_input, key=f"{challenge_value}_input", placeholder="Enter details here")

                    # Create a DataFrame with the most recent input
                    new_entry_df = pd.DataFrame({
                        'Session ID': [session_id],
                        'Client'   : [client_name], 
                        'Solution': [selected_solution],
                        'Category': ['Key Challenges'],
                        'Sub-Category': [sub_category],
                        'Importance': [selected_option],
                        'User Input': [user_input],
                        'Date Loaded': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                    })

                    # Remove existing entries for the same Sub-Category
                    st.session_state.user_inputs = st.session_state.user_inputs[~(st.session_state.user_inputs['Sub-Category'] == sub_category)]

                    # Concatenate the existing DataFrame with the new DataFrame
                    st.session_state.user_inputs = pd.concat([st.session_state.user_inputs, new_entry_df], ignore_index=True)
                else:
                    # If selected option is "None", remove the sub-category value from user_input
                    st.session_state.user_inputs = st.session_state.user_inputs[~(st.session_state.user_inputs['Sub-Category'] == sub_category)]

            # Store the selected option and user input in session state
            st.session_state.selected_options[challenge_value] = selected_option
            st.session_state.selected_options[f"{challenge_value}_input"] = user_input



# Function to iterate through the "Solutions Aspect" section of the proposal sections
def text_input(selected_solution, solutions_aspect):
    # Retrieve client's name from session state
    client_name = st.session_state.client_name
    session_id = st.session_state.session_id
    for category, sub_categories in solutions_aspect.items():
        user_input = st.session_state.selected_options.get(f"{category}_input", "")

        # Display text area for user to input details
        user_input = st.text_area(f"{category}:", value=user_input, key=f"{category}_input", placeholder="Enter details here")

        # Determine the index for any existing entries for this category
        existing_index = st.session_state.user_inputs[st.session_state.user_inputs['Sub-Category'] == category].index

        # If user input is not empty, update or add new entry
        if user_input.strip():  # Check if input is not just whitespace
            if not existing_index.empty:
                # If entry exists, update it
                st.session_state.user_inputs.loc[existing_index, 'User Input'] = user_input
            else:
                # If no entry exists, create a new one
                new_entry_df = pd.DataFrame({
                    'Session ID': [session_id],
                    'Client'  : [client_name],
                    'Solution': [selected_solution],
                    'Category': ['Solutions Aspect'],
                    'Sub-Category': [category],
                    'Importance': [''],  # Adjust if necessary
                    'User Input': [user_input],
                    'Date Loaded': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                })
                # Concatenate the existing DataFrame with the new DataFrame
                st.session_state.user_inputs = pd.concat([st.session_state.user_inputs, new_entry_df], ignore_index=True)
        else:
            # If user input is empty and an entry exists, remove it
            if not existing_index.empty:
                st.session_state.user_inputs = st.session_state.user_inputs.drop(existing_index)

        # Store the user input in session state, regardless of its content
        st.session_state.selected_options[f"{category}_input"] = user_input


# Function to export DataFrame to CSV and return its content
def generate_csv(data):
    csv = data.to_csv(index=False)
    return csv.encode()

def connect_to_db():

    # Access secrets
    username = st.secrets["snowflake"]["username"]
    password = st.secrets["snowflake"]["password"]
    account = st.secrets["snowflake"]["account"]
    warehouse = st.secrets["snowflake"]["warehouse"]
    database = st.secrets["snowflake"]["database"]
    schema = st.secrets["snowflake"]["schema"]


    # Connect to Snowflake
    cnxn = snowflake.connector.connect(
            user=username,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema)

    return cnxn

# Function to export DataFrame to snowflake
def export_to_sql(data, cnxn):
    cursor = cnxn.cursor()
    try:
        for index, row in data.iterrows():
            query = """
            INSERT INTO Captured_Data
            (Session_id,Client, Solution, Category, Sub_Category, Importance, User_Input, Date_Loaded)
            VALUES (%(session_id)s,%(client)s, %(solution)s, %(category)s, %(sub_category)s, %(importance)s, %(user_input)s, %(date_loaded)s)
            """
            row_data = {
                'session_id': row['Session ID'],
                'client'  : row['Client'],
                'solution': row['Solution'],
                'category': row['Category'],
                'sub_category': row['Sub-Category'],
                'importance': row['Importance'],
                'user_input': row['User Input'],
                'date_loaded': row['Date Loaded']
            }
            cursor.execute(query, row_data)
        cnxn.commit()  # Commit the transaction using the connection object
    except Exception as e:
        print(f"Error during database operation: {e}")
        cnxn.rollback()  # Rollback in case of error
    finally:
        cursor.close()  # Ensure the cursor is closed after operation

