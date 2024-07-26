import streamlit as st
import pandas as pd
import numpy as np


if "program_df" in st.session_state:
    program_df = st.session_state.program_df

    today = pd.to_datetime("today").normalize()

    future_training_days = program_df[program_df["date"] >= today]["date"].unique()
    next_training_day = future_training_days[0]


    cols = ["base_lift", "exercise", "set_type", "sets", "reps", "RPE", "weight_planned_rounded", "planned_1RM" ]
    
    next_workout = (program_df[program_df["date"] == next_training_day]
                    .reset_index(drop = True)
                    .drop(columns = ["date", "mean_e1RM", "adjust_planned_1RM_using_e1RM"])
                    [cols]
    )

    date = np.datetime_as_string(next_training_day, unit = "D")

    st.header(f"Workout for {date}")
    st.write(next_workout)