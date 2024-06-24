import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection



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

st.write("Choose the mesocycle length, i.e. how many microcycle the macrocycle should consist of:")
meso_length = st.slider(label = "mesocycle length", min_value = 1, max_value = 16, value = 6)

st.write("Choose the microcycle length, i.e. how many days (including rest days) the microcycle should consist of:")
micro_length = st.slider(label = "microcycle length", min_value = 1, max_value = 16, value = 7)


microcycle = st.data_editor(
    pd.DataFrame(columns = [f"day {i}" for i in range(1, micro_length + 1)]),
    num_rows = "dynamic"
)

for day in list(microcycle):

    if not microcycle[day].isnull().all():
        
        st.markdown(f"## {day}")

        for exercise in microcycle[day].dropna():
            st.markdown(f"### {exercise}")

            current_exercise_programming = st.data_editor(
                pd.DataFrame(columns = ["microcycle", "set type", "sets", "reps", "RPE"]),
                num_rows = "dynamic",
                key = f"{day}-{exercise}-data"
            )

            if f"{day}-{exercise}-data" not in st.session_state:
                st.session_state[f"{day}-{exercise}-data"] = current_exercise_programming
            
            series_creator(f"{day}-{exercise}-data", f"{day}-{exercise}")


'''
test = st.data_editor(pd.DataFrame(columns = ["test1", "test2"]))

test_button = st.button(label = "add sequence test",
    on_click = add_sequence,
    args = [test, "test1", "linear", 7, .5]

)
'''

'''
exercices_per_day = []

for day in range(1, micro_length + 1):
    st.markdown(f"## day {day}")
    current_day_exercises = st.data_editor(
        pd.DataFrame({"exercise": ["comp bench", "comp bench"], "set type": ["top", "back off"]}),
        num_rows = "dynamic",
        key = f"day_{day}"
    )
    
    exercices_per_day.append(current_day_exercises)

full_microcycle = st.dataframe(
    pd.concat(exercices_per_day, keys = [str(day) for day in range(1, micro_length + 1)])
)
'''
