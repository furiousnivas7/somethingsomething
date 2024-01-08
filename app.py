import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import openai
from openai import OpenAI
import base64

def load_data_from_json(file_name):
    """Load data from a JSON file."""
    try:
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                return json.load(file)
        else:
            return []
    except Exception as e:
        print(f"Error in loading JSON data: {e}")
        return []

def save_data_to_json(data, file_name):
    """Save data to a JSON file."""
    try:
        with open(file_name, "w") as file:
            json.dump(data, file, indent=12)
    except Exception as e:
        print(f"Error in saving JSON data: {e}")

def add_user_data(new_data, file_name="user_data.json"):
    existing_data = load_data_from_json(file_name)
    existing_data.append(new_data)
    save_data_to_json(existing_data, file_name)



def call_gpt3(prompt):
    openai.api_key = os.environ['OPENAI_API_KEY']  # Environment variable-l irunthu API key get pannuthu
    client = OpenAI()  # OpenAI client create pannuthu

    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # GPT-3.5 model specify pannuthu
        prompt=prompt,  # User kudutha prompt pass pannuthu
        max_tokens = 1000  # Maximum number of tokens (words) specify pannuthu
    )
   
    return response.choices[0].text 

# Function to save data to a JSON file
def save_data(data, filename="user_data.json"):
    try:
        with open(filename, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=12)


def clear_form_fields():
    """Clears all fields in st.session_state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def match_profiles(user_prompt, user_data):
    matched_profiles = []
    for profile in user_data:
        if any(user_prompt.lower() in (profile.get(key, "") or "").lower() for key in ["interest", "religion", "star"]):
            if profile["gender"] != user_data[-1]["gender"]:  # Compare with the last entry's gender
                matched_profiles.append(profile)
    return matched_profiles
def find_matching_profiles(user_data, current_user):
    matches = []
    # Ensure user_data is a list and current_user is a dictionary with required keys
    if isinstance(user_data, list) and isinstance(current_user, dict) and \
       "star" in current_user and "Planetary_position" in current_user and "gender" in current_user:
        for profile in user_data:
            # Check if the necessary keys exist in the profile
            if all(key in profile for key in ["star", "Planetary_position", "gender"]):
                if profile["star"] == current_user["star"] and \
                   profile["Planetary_position"] == current_user["Planetary_position"] and \
                   profile["gender"] != current_user["gender"]:
                    matches.append(profile)
    return matches
# Function to calculate matching percentage
def calculate_matching_percentage(current_user, match):
    matching_criteria = 2  # Same star and planetary position
    matched_criteria = sum([current_user[key] == match[key] for key in ["star", "Planetary_position"]])
    return (matched_criteria / matching_criteria) * 100


# Streamlit app
def main():
   



    st.title("User Information Form")
    file_name = "user_data.json"
    st.session_state.user_data_json = str(load_data_from_json(file_name))
    user_data = load_data_from_json(file_name)
    # st.json(user_data)


    with st.form("user_info_form"):
        name = st.text_input("Name", key="name")
        age = st.number_input("Age", key="age",min_value=0,max_value=100)
        gender = st.radio("Gender", ["Male", "Female", "Other"], key="gender")
        interest = st.text_area("Interest", key="interest")
        work = st.text_input("Work", key="work")
        salary = st.number_input("Salary", key="salary")
        dob = st.date_input("Date of Birth", key="dob")
        religion = st.text_input("Religion", key="religion")
        photo = st.file_uploader("Upload a photo", key="photo")
        horoscope_chart = st.file_uploader("Upload your horoscope chart", key="horoscope_chart")
        star = st.selectbox("Star", options=['Ashwini','Bharani','Krittika','Rohini','Mrighasira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishaka','Anuradha','Jyestha','Moola','Purvashada','Uttarashada','Sharavan','Dhanishta','Shatabisha','Purvabhadra','Uttarabhadra','Revat'], key="star")  # add all star names
        planetary_position = st.text_input("Planetary Position" , key="planetary_position")
        st.text("please pressed enter key for the submition")

        # submit= st.form_submit_button("Submit")

        photo_uploaded = photo is not None and photo.getvalue() != b''
        horoscope_chart_uploaded = horoscope_chart is not None and horoscope_chart.getvalue() != b''

        all_fields_filled = all([
            name, 
            age > 0, 
            gender, 
            interest, 
            work, 
            salary > 0, 
            dob, 
            religion, 
            planetary_position, 
            star,
            photo_uploaded,
            horoscope_chart_uploaded
        ])

        
        # st.write(f"All fields filled: {all_fields_filled}")
        submitted = st.form_submit_button("Submit")
        if submitted and all_fields_filled:
            encoded_photo = base64.b64encode(photo.getvalue()).decode() if photo else None
            encoded_horoscope_chart = base64.b64encode(horoscope_chart.getvalue()).decode() if horoscope_chart else None

            new_user_data = {
                    "name": name,
                    "age":age,
                    "gender": gender,
                    "interest": interest,
                    "work":work,
                    "salary":salary,
                    "dob": dob.strftime("%Y-%m-%d"),
                    "religion": religion,
                    "photo": encoded_photo,
                    "Planetary_position":planetary_position,
                    "horoscope_chart": encoded_horoscope_chart,
                    "star":star 
                }
            add_user_data(new_user_data, file_name)
            save_data(new_user_data)
            st.success("Data Saved Successfully!")

            user_data = load_data_from_json("user_data.json")
            current_user = user_data[-1]  # Assuming the last user is the current user
            matches = find_matching_profiles(user_data, current_user)

            if matches:
                st.subheader("Matching Profiles:")
                for match in matches:
                    percentage = calculate_matching_percentage(current_user, match)
                    match_details = (
                        f"Name: {match['name']}, "
                        f"DOB: {match.get('dob', 'Not available')}, "
                        f"Work: {match.get('work', 'Not available')}, "
                        f"Salary: {match.get('salary', 'Not available')}, "
                        f"Match Percentage: {percentage}%"
                    )
                    st.write(match_details)
                    # Call GPT-3 to explain the matching
                    user_prompt = f"Explain why two people with star {current_user['star']} and planetary position {current_user['Planetary_position']} are {percentage}% match, considering they have different genders."
                    explanation = call_gpt3(user_prompt)
                    st.write(f"Explanation: {explanation}")
            else:
                st.info("No matching profiles found.")
        elif submitted:
                st.warning("Please fill in all required fields.")
    # clear_form_fields()
    # st.rerun() 
    # if isinstance(user_data, list):
    #     df = pd.DataFrame(user_data)
    #     st.table(df)
    # else:
    #     st.error("User data is not in the correct format.")
    try:
        with open("user_data.json", "r") as file:
            user_data_json_content = file.read()
    except FileNotFoundError:
         user_data_json_content = "{}"
    st.download_button(
        label="Download JSON file",
        data=user_data_json_content,
        file_name="user_data.json",
        mime="application/json"
        )
    
    if 'full_prompt' not in st.session_state:
        st.session_state.full_prompt=""
    if 'gpt3_response' not in st.session_state:
        st.session_state.gpt3_response=""

    if 'user_data.json' not in st.session_state:
        file_name = "user_data.json"
        st.session_state.user_data_json = load_data_from_json(file_name)
    user_prompt = f"Explain why two people with star {current_user['star']} and planetary position {current_user['Planetary_position']} , considering they have different genders."
    button = st.button("Send Data to GPT-3.5") 

    if button:
        full_prompt = str(st.session_state.user_data_json) + user_prompt  
        gpt3_response = call_gpt3(full_prompt)  
    
        # user_data = {
        #         "interest": user_prompt,
        #         "gpt3_response": gpt3_response,
        #         # "photo": st.file_uploader("Upload a photo").read()
        #     }

        # save_data(user_data)
        st.write("OpenAI Response:", gpt3_response)
    #    st.success("Data Saved Successfully!") 



if __name__ == "__main__":
    main()
