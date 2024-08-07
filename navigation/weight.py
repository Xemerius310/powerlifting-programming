import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


if "weight_df" in st.session_state:
    weight_df = st.session_state["weight_df"]

    st.title("Weight Tracking")


    # calculate 7 day rolling mean for weight
    weight_df["rolling_mean"] = weight_df["weight"].rolling(window = 7).mean()

    # calculate difference between rolling mean today and 30 days ago
    weight_df["rolling_mean_diff"] = weight_df["rolling_mean"] - weight_df["rolling_mean"].shift(30)



    st.dataframe(weight_df, hide_index = True)

    # count total number of months from first to last entry
    all_months = int(np.ceil((weight_df["date"].max() - weight_df["date"].min()) / np.timedelta64(1, "M")))

    def month_selection_formatting(months):
        if months == 1:
            return "last month"
        else:
            return f"last {months} months"

    # select time period for the weight chart
    st.write("Select the time period for the weight chart")

    col1, col2 = st.columns(2)
    with col1:
        months = st.selectbox(label = "time period", options = [1, 3, 6, 12, 24, all_months], format_func = month_selection_formatting)
    with col2:
        months = st.number_input(label = "months", min_value = 1, value = months)

    today = pd.to_datetime("today").normalize()
    start_date = today - pd.DateOffset(months = months)
    
    weights_subset = weight_df[weight_df["date"] >= start_date]

    # Create the base weight chart
    weight_chart = (
        alt.Chart(weights_subset)
        .mark_line()
        .encode(
            x = "date",
            y = alt.Y("weight", scale = alt.Scale(zero = False)),
            tooltip = ["date", "weight"]
        )
    )

    # Create the rolling mean chart
    rolling_mean_chart = (
        alt.Chart(weights_subset)
        .mark_line(color = 'orange')
        .encode(
            x = "date",
            y = alt.Y("rolling_mean", scale = alt.Scale(zero = False)),
            tooltip = ["date", "rolling_mean"]
        )
    )

    # combine both charts
    combined_chart = alt.layer(weight_chart, rolling_mean_chart)

    # display the combined chart
    st.altair_chart(combined_chart)


    # display the rolling mean difference
    st.write("Difference between rolling mean today and 30 days ago")

    rolling_mean_diff_chart = (
        alt.Chart(weights_subset)
        .mark_line()
        .encode(
            x = "date",
            y = alt.Y("rolling_mean_diff", scale = alt.Scale(zero = False)),
            tooltip = ["date", "rolling_mean_diff"]
        )
    )

    st.altair_chart(rolling_mean_diff_chart)