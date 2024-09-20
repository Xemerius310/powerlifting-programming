import streamlit as st
import pandas as pd
import numpy as np

today = pd.to_datetime("today").normalize()

if "program_df" in st.session_state:
    program_df = st.session_state.program_df


    future_training_days = program_df[program_df["date"] >= today]["date"].unique()
    
    next_training_day = st.selectbox("Select a future training day", np.datetime_as_string(future_training_days, unit = "D"))
    next_training_day = np.datetime64(next_training_day, "D")


    cols = ["base_lift", "exercise", "set_type", "sets", "reps", "RPE", "weight_planned_rounded", "planned_1RM" ]
    
    next_workout = (program_df[program_df["date"] == next_training_day]
                    .reset_index(drop = True)
                    .drop(columns = ["date", "mean_e1RM", "adjust_planned_1RM_using_e1RM"])
                    [cols]
    )

    date = np.datetime_as_string(next_training_day, unit = "D")

    st.header(f"Workout for {date}")

    for base_lift, base_lift_df in next_workout.groupby("base_lift"):
        st.subheader(base_lift.title())

        base_lift_df.drop(columns = "base_lift", inplace = True)
        st.dataframe(base_lift_df, hide_index = True)

    
    if "actual_progression_df" in st.session_state:
        actual_progression_df = st.session_state.actual_progression_df

        st.markdown("## Unlogged Workouts")

        # get number of logged sets for combinations of date and base lift
        logged_sets_per_day_and_base_lift = (actual_progression_df
                                             .groupby(["date", "base_lift"], as_index = False)
                                             .size()
                                             .rename(columns = {"size": "logged_sets"}))

        # get number of planned sets for combinations of date and base lift
        planned_sets_per_day_and_base_lift = (program_df
                                              .groupby(["date", "base_lift"], as_index = False)
                                              .agg({"sets": "sum"})
                                              .rename(columns = {"sets": "planned_sets"}))

        # only consider planned workouts before today
        planned_sets_per_day_and_base_lift = planned_sets_per_day_and_base_lift[planned_sets_per_day_and_base_lift["date"] < today]

        # join the two dataframes to see which workouts are planned but not logged using the "indicator"
        # planned but not logged workouts will have the value "left_only" in the "_merge" column
        planned_and_logged_join = planned_sets_per_day_and_base_lift.merge(logged_sets_per_day_and_base_lift,
                                                                           on        = ["date", "base_lift"],
                                                                           how       = "left",
                                                                           indicator = True)

        planned_but_not_logged = (planned_and_logged_join[planned_and_logged_join["_merge"] == "left_only"]
                                  .drop(columns = "_merge"))

        program_and_planned_but_not_logged_join = program_df.merge(planned_but_not_logged, on = ["date", "base_lift"], how = "inner")


        if planned_but_not_logged.empty:
            st.write("No workouts to log.")
        else:
            st.write("Workouts to log:")
            st.dataframe(planned_but_not_logged, hide_index = True)
            st.dataframe(program_and_planned_but_not_logged_join, hide_index = True)