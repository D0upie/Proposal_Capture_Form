import streamlit as st
import csv
import pandas as pd

# Define radio options
radio_options = ["None", "Low", "Moderate", "High"]

# Function to iterate through the "Key Challenges" section of the proposal sections
def radio_select(selected_solution, key_challenges, parent_list=""):
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
                        'Solution': [selected_solution],
                        'Category': ['Key Challenges'],
                        'Sub-Category': [sub_category],
                        'Importance': [selected_option],
                        'User Input': [user_input]
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
    for category, sub_categories in solutions_aspect.items():
        user_input = st.session_state.selected_options.get(f"{category}_input", "")

        #st.write(category)
        user_input = st.text_area(f"{category}:", value=user_input, key=f"{category}_input", placeholder="Enter details here")

        # Check if the user input is not empty
        if user_input.strip():
            # Check if entry already exists in DataFrame
            existing_index = st.session_state.user_inputs[st.session_state.user_inputs['Sub-Category'] == category].index

            # If entry exists, update it with the most recent input
            if not existing_index.empty:
                st.session_state.user_inputs.loc[existing_index, 'User Input'] = user_input
            else:
                # Create a DataFrame with the most recent input
                new_entry_df = pd.DataFrame({
                    'Solution': selected_solution,
                    'Category': ['Solutions Aspect'],
                    'Sub-Category': [category],
                    'Importance': [''],
                    'User Input': [user_input]
                })

                # Concatenate the existing DataFrame with the new DataFrame
                st.session_state.user_inputs = pd.concat([st.session_state.user_inputs, new_entry_df], ignore_index=True)

        # Store the user input in session state
        st.session_state.selected_options[f"{category}_input"] = user_input

# Function to export DataFrame to CSV and return its content
def generate_csv(data):
    csv = data.to_csv(index=False)
    return csv.encode()