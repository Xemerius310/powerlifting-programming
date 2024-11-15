
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from streamlit_app import get_data_and_calculate_progression

from helper_functions import round_to_multiple

supabase = st.session_state["supabase"]

st.title("Progression Analysis")

st.write("The following flow chart shows the adjustment logic for the planned 1RM.")

st.graphviz_chart('''
    digraph {
        end_of_mesocycle -> test_1RM
        test_1RM -> recommend_weight
        recommend_weight -> train
        train -> {RPE_violation, RPE_compliance}
        RPE_violation -> estimate_1RM
        estimate_1RM -> planned_1RM
        RPE_compliance -> add_planned_increment
        add_planned_increment -> planned_1RM
        planned_1RM -> recommend_weight
    }
''')

if "round_multiple" in st.session_state:
    round_multiple = st.session_state["round_multiple"]

if "all_planned_base_lift_progressions" not in st.session_state:
    get_data_and_calculate_progression()
    st.rerun()

if "all_planned_base_lift_progressions" in st.session_state:
    all_planned_base_lift_progressions = st.session_state.all_planned_base_lift_progressions

    for base_lift, base_lift_df in all_planned_base_lift_progressions.groupby("base_lift"):
        st.subheader(f"{base_lift.title()} Progression")

        base_lift_df.drop(columns = ["base_lift"], inplace = True)
        # calculate the direction of the planned 1RM adjustment
        base_lift_df["adjustment_direction"] = np.sign(
            (base_lift_df["mean_e1RM"] - base_lift_df["planned_1RM"]).fillna(0)
        )

        st.dataframe(base_lift_df.drop(columns = "adjustment_direction"), hide_index = True)

        base_lift_df_long = base_lift_df.melt(id_vars = ["date"], var_name = "variable", value_name = "value")
        base_lift_df_long = base_lift_df_long[~base_lift_df_long["variable"]
                                              .isin(["adjust_planned_1RM_using_e1RM", "adjustment_direction"])]

        # transpose to long to work with altair for plotting
        base_lift_df_long["value"] = base_lift_df_long["value"].astype(float)

        # calculate the y-axis limits
        y_min = round_to_multiple(base_lift_df_long["value"].min(), round_multiple) - round_multiple
        y_max = round_to_multiple(base_lift_df_long["value"].max(), round_multiple) + round_multiple

        # generate tick values based on round_multiple
        tick_values = np.arange(y_min, y_max, round_multiple)
        
        base_chart = (
            alt.Chart(base_lift_df_long)
            .mark_line(point = True)
            .encode(
                x = "date:T",
                y = alt.Y("value:Q",
                          scale = alt.Scale(domain = [y_min, y_max]),
                          title = "weight",
                          axis  = alt.Axis(values = tick_values, format = ".1f")
                ),
                color = "variable:N")
            .properties(width = 800, height = 400)
        )


        base_lift_df["date_minus_12h"] = base_lift_df["date"] - pd.Timedelta(hours = 12)
        base_lift_df["date_plus_12h"]  = base_lift_df["date"] + pd.Timedelta(hours = 12)


        # filter the dataframe to include only rows where adjust_planned_1RM_using_e1RM is 1
        # and the planned 1RM is adjusted downwards
        adjust_planned_1RM_down_days = base_lift_df[(base_lift_df["adjust_planned_1RM_using_e1RM"] == 1)
                                                    & (base_lift_df["adjustment_direction"] == -1)]

        adjust_planned_1RM_chart = (
            alt.Chart(adjust_planned_1RM_down_days)
            .mark_rect(color = "red", opacity = 0.2)
            .encode(x = "date_minus_12h:T", x2 = "date_plus_12h:T", y = alt.value(0))
        )

        # filter the dataframe to include only rows where adjust_planned_1RM_using_e1RM is 1
        # and the planned 1RM is adjusted upwards
        adjust_planned_1RM_up_days = base_lift_df[(base_lift_df["adjust_planned_1RM_using_e1RM"] == 1)
                                                  & (base_lift_df["adjustment_direction"] == 1)]
        
        adjust_planned_1RM_chart += (
            alt.Chart(adjust_planned_1RM_up_days)
            .mark_rect(color = "green", opacity = 0.2)
            .encode(x = "date_minus_12h:T", x2 = "date_plus_12h:T", y = alt.value(0))
        )

        combined_chart = alt.layer(base_chart, adjust_planned_1RM_chart)

        st.altair_chart(combined_chart)