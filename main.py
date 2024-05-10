import streamlit as st
import pandas as pd
import json, datetime
import uuid
# Import necessary functions or modules
from functions import radio_select, text_input, generate_csv, connect_to_db, export_to_sql, generate_session_id
from datetime import datetime

st.set_page_config(layout="wide")

# Load proposal sections from the JSON file
with open("proposal_sections.json", "r") as json_file:
    st.session_state.proposal_sections = json.load(json_file)

# def generate_session_id():
#     # Generate a UUID4 session ID
#     session_id = str(uuid.uuid4())
#     st.session_state.session_id = session_id
#     return session_id

session_id = generate_session_id()
st.session_state.session_id = session_id

# Define the main function to render different sections based on sidebar selection
def main():
    st.sidebar.title("Client Details ")
    client_name = st.sidebar.text_input("Enter client name:", placeholder="Please enter client name here", value=st.session_state.get("client_name", ""))
    # Store client's name in session state
    st.session_state.client_name = client_name

    # Initiate solution option if not already set
    if 'selected_solution' not in st.session_state:
        # If selected_solution is not yet stored in session state, initialize it with the default value
        selected_solution = st.sidebar.selectbox("Select proposal solution:", ["ILA", "Gen AI"], placeholder="Choose an option")
        # Store the selected solution in session state
        st.session_state.selected_solution = selected_solution
    else:
        # Display the selectbox with the default value
        selected_solution = st.sidebar.selectbox("Select proposal solution:", ["ILA", "Gen AI"], placeholder="Choose an option", index=["ILA", "Gen AI"].index(st.session_state.selected_solution ))  
        # Store the selected solution in session state
        st.session_state.selected_solution = selected_solution

    page = st.sidebar.selectbox("Go to", ["Key Challenges", "Solutions Aspect", "Additional Info", "Summary"])

    if page == "Main Menu":
        render_page_1()
    elif page == "Key Challenges":
        render_page_2()
    elif page == "Solutions Aspect":
        render_page_3()
    elif page == "Additional Info":
        render_page_4()
    elif page == "Summary":
        render_page_5()

# Define functions to render each page
def render_page_1():
    st.title("Client Details:")
    # Initiate client name
    client_name = st.text_input("Enter client name:", placeholder="Please enter client name here", value=st.session_state.get("client_name", ""))
    # Store client's name in session state
    st.session_state.client_name = client_name
    
    # Initiate solution option if not already set
    if 'selected_solution' not in st.session_state:
        # If selected_solution is not yet stored in session state, initialize it with the default value
        selected_solution = st.selectbox("Select proposal solution:", ["ILA", "Gen AI"], placeholder="Choose an option")
        # Store the selected solution in session state
        st.session_state.selected_solution = selected_solution
    else:
        # Display the selectbox with the default value
        selected_solution = st.selectbox("Select proposal solution:", ["ILA", "Gen AI"], placeholder="Choose an option", index=["ILA", "Gen AI"].index(st.session_state.selected_solution ))  
        # Store the selected solution in session state
        st.session_state.selected_solution = selected_solution


def render_page_2():
    # Retrieve solution option from session state
    selected_solution = st.session_state.selected_solution

    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = {}

    # Retrieve client's name from session state
    client_name = st.session_state.client_name

    # Retrieve proposal_sections from session state
    proposal_sections = st.session_state.proposal_sections

    # Initialize DataFrame to store user inputs
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = pd.DataFrame(columns=['Session ID','Client','Solution','Category', 'Sub-Category', 'Importance', 'User Input','Date Loaded'])

    st.title(f"Key Challenges - *{st.session_state.selected_solution}* for *{st.session_state.client_name}*")
    radio_select(selected_solution, proposal_sections[st.session_state.selected_solution]["Key Challenges"])

    capture_key_challenges = st.session_state.user_inputs[(st.session_state.user_inputs['Category'] == 'Key Challenges') & (st.session_state.user_inputs['Solution'] == selected_solution)]

    # Display the captured data DataFrame
    with st.expander("See Captured data"):
        st.write(capture_key_challenges)

def render_page_3():
    # Retrieve solution option from session state
    selected_solution = st.session_state.selected_solution

    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = {}

    # Retrieve client's name from session state
    client_name = st.session_state.client_name

    # Retrieve proposal_sections from session state
    proposal_sections = st.session_state.proposal_sections

    # Initialize DataFrame to store user inputs
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = pd.DataFrame(columns=['Session ID','Client', 'Solution','Category', 'Sub-Category', 'Importance', 'User Input', 'Date Loaded'])

    st.title(f"Solutions Aspect - *{st.session_state.selected_solution}* for *{st.session_state.client_name}*")
    text_input(selected_solution, proposal_sections[st.session_state.selected_solution]["Solution Aspect"])

    capture_solution_aspects = st.session_state.user_inputs[(st.session_state.user_inputs['Category'] == 'Solutions Aspect') & (st.session_state.user_inputs['Solution'] == selected_solution)]

    # Display the captured data DataFrame
    with st.expander("See Captured data"):
        st.write(capture_solution_aspects)

def render_page_4():
    # Retrieve solution option from session state
    selected_solution = st.session_state.selected_solution

    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = {}

    # Retrieve client's name from session state
    client_name = st.session_state.client_name

    # Retrieve or generate session ID
    # session_id = generate_session_id()  # You need to define a function to generate session IDs


    # Initialize DataFrame to store user inputs
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = pd.DataFrame(columns=['Session ID','Client', 'Solution','Category', 'Sub-Category', 'Importance', 'User Input', 'Date Loaded'])

    st.title(f"Additional Info for *{client_name}*")
    
    additional_info = st.session_state.selected_options.get("additional_info_input", "")

    additional_info = st.text_area("Please add any additional information that may be relevant to the proposal",
                                   value=additional_info, 
                                   key="additional_info_input",
                                   placeholder="Enter additional info here")

    # Always remove existing entries for 'Additional Info' category first
    st.session_state.user_inputs = st.session_state.user_inputs[st.session_state.user_inputs['Category'] != 'Additional Info']
    
    # Only add new entry if additional_info is not empty
    if additional_info.strip():  # .strip() to check if input is not just whitespace
        new_entry_df = pd.DataFrame({
            'Session ID': [st.session_state.session_id],
            'Client'  : [client_name],
            'Solution': [selected_solution],
            'Category': ['Additional Info'],
            'Sub-Category': [''],  # Adjust if necessary
            'Importance': [''],  # Adjust if necessary
            'User Input': [additional_info],
            'Date Loaded': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        })
        # Concatenate the existing DataFrame with the new DataFrame
        st.session_state.user_inputs = pd.concat([st.session_state.user_inputs, new_entry_df], ignore_index=True)

    # Store the additional info in session state regardless of its content
    st.session_state.selected_options["additional_info_input"] = additional_info


def render_page_5():
    # Retrieve solution option from session state
    selected_solution = st.session_state.selected_solution

    # Retrieve user inputs DataFrame from session state
    user_inputs = st.session_state.user_inputs[st.session_state.user_inputs['Solution'] == selected_solution]

    # Page title
    st.title("Solutions Overview")

    # Display user inputs DataFrame
    st.write(user_inputs)

    # Define CSV file path
    client_name = st.session_state.client_name
    Year = datetime.now().strftime("%Y")
    Hour = datetime.now().strftime("%H")
    Minutes = datetime.now().strftime("%M")
    Seconds = datetime.now().strftime("%S")
    file_name = (f"Proposal_Form_{client_name}_{Year}{Hour}{Minutes}{Seconds}.csv")
    csv_data = generate_csv(user_inputs)


    st.download_button(label='Download CSV', data=csv_data, file_name=file_name, mime='text/csv')


    if st.button('Export to Snowflake'):
        cnxn = connect_to_db()  # Get the connection object
        export_to_sql(user_inputs, cnxn)  # Pass the connection to the function
        cnxn.close()  # Close the connection after operation
        st.success('Data exported successfully to SQL database.')


# Entry point of the application
if __name__ == "__main__":
    main()
