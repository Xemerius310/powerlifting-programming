import streamlit as st
import pandas as pd
import numpy as np
from st_supabase_connection import execute_query
from streamlit_app import get_user_id



supabase = st.session_state["supabase"]


def get_exercise_list():
    exercises_query = execute_query(
        supabase.table("exercise_settings").select("*").eq("setting", "base_lift"), ttl = 0
    )
    exercises = pd.DataFrame(exercises_query.data)
    exercises["date"] = pd.to_datetime(exercises["date"])
    # group by exercise and select row with max date, then rename value column to exercise
    exercises = (exercises.loc[exercises.groupby("exercise")["date"].idxmax()]
                 .rename(columns = {"value": "base_lift"})
                 [["exercise", "base_lift"]])
    
    st.session_state["exercise_list"] = exercises




def add_set(exercise, set_type, weight, reps, RPE):
    """Function to add a new set or update an existing one."""
    new_set = {
        'exercise': exercise,
        'set_type': set_type,
        'set_number': len(st.session_state.sets_df) + 1,  # Assign the next set number
        'weight': weight,
        'reps': reps,
        'RPE': RPE
    }
    
    if st.session_state.editing_set is not None:
        # Update existing set
        st.session_state.sets_df.iloc[st.session_state.editing_set] = new_set
        st.session_state.editing_set = None
    else:
        # Add new set using concat (instead of append)
        st.session_state.sets_df = pd.concat([st.session_state.sets_df, pd.DataFrame([new_set])], ignore_index=True)



    


@st.dialog("Add/Edit Set")
def open_dialog(is_editing = False, selected_row = None, exercise = None):
    """Open the dialog for adding or editing a set."""
    exercises = list(st.session_state["exercise_list"]["exercise"])
    set_types = ["top", "back off", "back off 1", "back off 2", "straight"]  # Example set types

    logged_at_date_exercise = (logged_at_date[logged_at_date["exercise"] == exercise]
                                .reset_index(drop = False))

    if is_editing:
        selected_row_data = logged_at_date_exercise.iloc[selected_row]

        # get index of the exercise to prefill default value in form
        exercise_index = exercises.index(exercise)
        
        # do the same for set type
        set_type = selected_row_data["set_type"]
        set_type_index = set_types.index(set_type)

        set_number = selected_row_data["set_number"]
        weight = selected_row_data["weight"]
        reps = selected_row_data["reps"]
        rpe = selected_row_data["RPE"]
    else:
        exercise_index, set_type_index, weight, reps, rpe = 0, 0, 0.0, 0, 0.0
        if not logged_at_date.empty:
            last_logged_set = logged_at_date.iloc[logged_at_date["set_number"].idxmax()]
            exercise_index = exercises.index(last_logged_set["exercise"])
            set_type_index = set_types.index(last_logged_set["set_type"])
            set_number = logged_at_date["set_number"].max() + 1
            weight = last_logged_set["weight"]
            reps = last_logged_set["reps"]
            rpe = last_logged_set["RPE"]

        # set the set number 1 if no sets have been logged
        else:
            set_number = 1
    
    exercise = st.selectbox("exercise", options = exercises, index = exercise_index)
    col1, col2 = st.columns(2)
    with col1:
        set_type = st.selectbox("set type", options = set_types, index = set_type_index)
    with col2:
        set_number = st.number_input("set number", value = set_number, min_value = 1, step = 1, disabled = True)
    weight = st.number_input("weight", value = weight, min_value = 0.0, step = 0.5)
    reps = st.number_input("reps", value = reps, min_value = 0, step = 1)
    rpe = st.number_input("RPE", value = rpe, max_value = 10.0, step = 0.5)

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Save Set"):
            edit_response = execute_query(
                supabase.table("training_log").upsert({
                    "user_id": st.session_state["user_id"],
                    "date": date.strftime("%Y-%m-%d"),
                    "exercise": exercise,
                    "set_type": set_type,
                    "set_number": set_number,
                    "weight": weight,
                    "reps": reps,
                    "RPE": rpe},
                    on_conflict = "user_id, date, set_number"),
                ttl = 0
            )
            st.write(edit_response)
            st.rerun()

    with col2:
        if st.button("Delete Set"):
            delete_response = execute_query(
                supabase.table("training_log")
                    .delete()
                    .eq("user_id", st.session_state["user_id"])
                    .eq("date", date.strftime("%Y-%m-%d"))
                    .eq("set_number", set_number),
                ttl = 0
            )
            st.write(delete_response)
            st.rerun()





if supabase.auth.get_user():
    if not "user_id" in st.session_state:
        get_user_id()

    user_id = st.session_state["user_id"]

    # get training log
    training_log_response = execute_query(supabase.table("training_log").select("*").eq("user_id", user_id), ttl = 0)
    training_log_df = pd.DataFrame(training_log_response.data)
    training_log_df["date"] = pd.to_datetime(training_log_df["date"])
    training_log_df.sort_values(["date", "set_number"], inplace = True)

    date = st.date_input(label = "Date", value = training_log_df["date"].iloc[-1])
    logged_at_date = training_log_df[training_log_df["date"] == np.datetime64(date, "D")]

    if "exercise_list" not in st.session_state:
        get_exercise_list()

    # join logged_at_date with exercise list
    logged_at_date = (logged_at_date.merge(st.session_state["exercise_list"], on = "exercise")
                      .sort_values("set_number"))
    

    for exercise in logged_at_date["exercise"].unique():
        if f"selection for {exercise}" in st.session_state and st.session_state[f"selection for {exercise}"] is not None:
            # st.write(f"selection for {exercise}")
            # st.write(st.session_state[f"selection for {exercise}"])

            selected_row_list = st.session_state[f"selection for {exercise}"]["selection"]["rows"]
            if len(selected_row_list) > 0:
                # reset the selection
                st.session_state[f"selection for {exercise}"] = None
                # selected_row_list only contains one element because selection_mode is set to "single-row"
                open_dialog(True, selected_row_list[0], exercise)
                break

    # button to add new set
    if st.button('Add New Set'):
        open_dialog()

    for exercise, exercise_sets in logged_at_date.groupby("exercise"):
        st.subheader(exercise)
        st.session_state[f"selection for {exercise}"] = st.dataframe(
            exercise_sets[["set_number", "set_type", "weight", "reps", "RPE"]],
            selection_mode = "single-row",
            on_select = "rerun",
            hide_index = True)
    

    