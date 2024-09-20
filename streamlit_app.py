import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection
from streamlit_cookies_controller import CookieController
from st_supabase_connection import SupabaseConnection, execute_query



supabase = st.connection("supabase", type = SupabaseConnection)
st.session_state["supabase"] = supabase


# import needs to happen here since the functions above need to be defined before public_sheet_planning.py is loaded
from navigation.public_sheet_planning import get_supabase_data, read_gsheets, calculate_planned_progression

# gets the user id based on auth id and saves it to session state
def get_user_id():
    user_response = supabase.auth.get_user()
    auth_id = user_response.user.id

    # get user data from user table in database, based on the user's auth_id
    user_data = execute_query(
        supabase.table("user").select("id, username").eq("auth_id", auth_id), ttl = 0
    )
    st.session_state["username"] = user_data.data[0].get("username")
    st.session_state["user_id"] = user_data.data[0].get("id")


cookie_controller = CookieController()

all_cookies = cookie_controller.getAll()

# user_response = supabase.auth.get_user()
# if user_response is None and "access_token" in all_cookies and "refresh_token" in all_cookies:
#     supabase.auth.set_session(all_cookies["access_token"], all_cookies["refresh_token"])

#     session_response = supabase.auth.get_session()

#     cookie_controller.set(name = "access_token", value = session_response.access_token)
#     cookie_controller.set(name = "refresh_token", value = session_response.refresh_token)

#     get_user_id()


with st.sidebar:
    default_metadata_spreadsheet_url = cookie_controller.get("metadata_spreadsheet_url")
    metadata_spreadsheet_url = st.text_input(label = "metadata spreadsheet url", value = default_metadata_spreadsheet_url)

    st.session_state["metadata_spreadsheet_url"] = metadata_spreadsheet_url

    if metadata_spreadsheet_url:
        cookie_controller.set(name = "metadata_spreadsheet_url", value = metadata_spreadsheet_url)
    
        if st.button("load gsheets data"):
            read_gsheets(metadata_spreadsheet_url)
            calculate_planned_progression()
            st.rerun()

    email = st.text_input(label = "username")
    password = st.text_input(label = "password", type = "password")

    col1, col2 = st.columns(2)
    with col1:
        login_button = st.button("login")
    with col2:
        logout_button = st.button("logout")

    if login_button:
        try:
            supabase.auth.sign_in_with_password(dict(email = email, password = password))
            st.write(f"Welcome, {email}!")
            

            get_user_id()

            session_response = supabase.auth.get_session()

            cookie_controller.set(name = "access_token", value = session_response.access_token)
            cookie_controller.set(name = "refresh_token", value = session_response.refresh_token)
            
            # get_supabase_data()
            # calculate_planned_progression()
            # st.rerun()

        except:
            st.write("login failed")

        cookie_controller.set(name = "email", value = email)
    
    if logout_button:
        logout_result = supabase.auth.sign_out()
        cookie_controller.remove("email")
        cookie_controller.remove("access_token")
        cookie_controller.remove("refresh_token")



    st.session_state["round_multiple"] = st.number_input(label = "round weights to nearest multiple of", value = 2.5)



#---------------------------------------------------------------------------------------------------
# defining pages
#---------------------------------------------------------------------------------------------------

public_sheet_planning_page = st.Page("navigation/public_sheet_planning.py", title = "📆 Public Sheet Planning")
mesocycle_creator_page = st.Page("navigation/mesocycle_creator.py", title = "🛠️ Mesocycle Creator")
oneRM_calculator_page = st.Page("navigation/calculators.py", title = "🧮 Calculators")
athlete_view_page = st.Page("navigation/athlete_view.py", title = "🏋 Athlete View")
analysis_page = st.Page("navigation/analysis.py", title = "📊 Analysis")
bodyweight_page = st.Page("navigation/bodyweight.py", title = "⚖️ Weight")
training_log_page = st.Page("navigation/training_log.py", title = "📝 Training Log")

navigation = st.navigation({
    "Planning": [
        public_sheet_planning_page,
        analysis_page,
        mesocycle_creator_page,
    ],
    "Training": [
        oneRM_calculator_page,
        athlete_view_page,
        bodyweight_page,
        training_log_page
    ],
})

navigation.run()





