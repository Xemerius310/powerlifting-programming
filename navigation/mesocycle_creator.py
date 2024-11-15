
import streamlit as st
import pandas as pd
import numpy as np


def add_sequence(df_key, column, sequence_type, start, increment):
    st.write("test")

    dataframe = st.session_state[df_key]

    if sequence_type == "linear":
        dataframe[column] = start + np.arange(0, meso_length) * increment
        st.write(start + np.arange(0, meso_length) * increment)


def series_creator(current_exercise_programming, key):
    col1, col2, col3, col4 = st.columns(4)

    sequence_col = "RPE"
    sequence_type = "linear"
    increment = .5

    with col1:
        start = st.number_input(min_value = 1.0, step = 0.5, label = "start", key = f"{key}-start")

        add_sequence_button = st.button(label = "add sequence",
            on_click = add_sequence,
            args = [current_exercise_programming, sequence_col, sequence_type, start, increment],
            key = f"{key}-add_seq_button")
        
    with col2:
        increment = st.number_input(min_value = 0.0, step = 0.5, label = "increment", key = f"{key}-increment")
    
    with col3:
        sequence_type = st.selectbox(label = "sequence type", options = ["linear", "+1,-1,+2,-1"], key = f"{key}-seq_type")
        
    with col4:
        sequence_col = st.selectbox(label = "sequence column", options = ["sets", "reps", "RPE"], key = f"{key}-seq_col")




st.title("Mesocycle Creator")

st.write("Choose the mesocycle length, i.e. how many microcycles the macrocycle should consist of:")
meso_length = st.slider(label = "mesocycle length", min_value = 1, max_value = 16, value = 6)

st.write("Choose the microcycle length, i.e. how many days (including rest days) the microcycle should consist of:")
micro_length = st.slider(label = "microcycle length", min_value = 1, max_value = 16, value = 7)



microcycle = st.data_editor(
    pd.DataFrame(columns = [f"day {i}" for i in range(1, micro_length + 1)]),
    num_rows = "dynamic"
)

microcycle_flattened = microcycle.values.flatten()
exercises_without_nulls = microcycle_flattened[pd.notnull(microcycle_flattened)]
all_exercises = list(set(exercises_without_nulls))


for exercise in all_exercises:
    st.markdown(f"## {exercise}")
    exercise_days = microcycle.columns[microcycle.isin([exercise]).any()].tolist()

    exercise_set_types = st.data_editor(
        pd.DataFrame(columns = exercise_days),
        num_rows = "dynamic",
        key = f"{exercise}-set_types"
    )

    all_exercise_set_types = list(set(exercise_set_types.values.flatten()))
    
    for set_type in all_exercise_set_types:
        st.markdown(f"### {set_type}")

        n_set_type_days = len(exercise_set_types.isin([set_type]).any())
        sequence_length = n_set_type_days * meso_length

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write("sets"); st.write(""); st.write("")
            st.write("reps"); st.write(""); st.write(""); st.write("")
            st.write("RPE")

        with col2:
            start_sets = st.number_input(min_value = 1, step = 1, label = "start", key = f"{exercise}-{set_type}-start_sets")
            start_reps = st.number_input(min_value = 1, step = 1, label = "start", key = f"{exercise}-{set_type}-start_reps")
            start_RPE = st.number_input(min_value = 1.0, step = 0.5, label = "start", key = f"{exercise}-{set_type}-start_RPE")
        
        with col3:
            step_sets = st.number_input(min_value = 0, step = 1, label = "step", key = f"{exercise}-{set_type}-step_sets")
            step_reps = st.number_input(min_value = 0, step = 1, label = "step", key = f"{exercise}-{set_type}-step_reps")
            step_RPE = st.number_input(min_value = 0.0, step = 0.5, label = "step", key = f"{exercise}-{set_type}-step_RPE")
        
        with col4:
            sequence_options = ["linear", "+1,-1,+2,-1", "repeat"]
            sequence_type_sets = st.selectbox(label = "sequence type", options = sequence_options, key = f"{exercise}-{set_type}-seq_type_sets")
            sequence_type_reps = st.selectbox(label = "sequence type", options = sequence_options, key = f"{exercise}-{set_type}-seq_type_reps")
            sequence_type_RPE = st.selectbox(label = "sequence type", options = sequence_options, key = f"{exercise}-{set_type}-seq_type_RPE")

        with col5:
            repeat_sequence_sets = st.text_input(label = "repeat sequence", key = f"{exercise}-{set_type}-repeat_seq_sets")
            repeat_sequence_reps = st.text_input(label = "repeat sequence", key = f"{exercise}-{set_type}-repeat_seq_reps")
            repeat_sequence_RPE = st.text_input(label = "repeat sequence", key = f"{exercise}-{set_type}-repeat_seq_RPE")
        





  

for day in list(microcycle):
    st.write(day)
    st.write(microcycle[day])

    if not microcycle[day].isnull().all():
        
        st.markdown(f"## {day}")

        for exercise in microcycle[day].dropna():
            st.markdown(f"### {exercise}")


            current_exercise_programming = st.data_editor(
                pd.DataFrame(columns = ["microcycle", "set type", "sets", "reps", "RPE"]),
                num_rows = "dynamic",
                key = f"{day}-{exercise}-data"
            )

            st.write(current_exercise_programming)

            # if f"{day}-{exercise}-data" not in st.session_state:
            #     st.session_state[f"{day}-{exercise}-data"] = current_exercise_programming
            
            # series_creator(f"{day}-{exercise}-data", f"{day}-{exercise}")
