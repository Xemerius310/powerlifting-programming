import streamlit as st
import pandas as pd


RPE_to_pct = st.session_state["RPE_to_pct_fun"]
round_to_multiple = st.session_state["round_to_multiple_fun"]
round_multiple = st.session_state["round_multiple"]


st.markdown("## Weight Recommendation Calculator")

if "variations_df" in st.session_state:
    variations_df = st.session_state.variations_df
    base_lifts = variations_df["base_lift"].unique()

    base_lift_col, variation_col = st.columns(2)

    with base_lift_col:
        base_lift = st.selectbox("select a base lift", base_lifts)

    base_lift_variations = variations_df[variations_df["base_lift"] == base_lift]["variation"]
    with variation_col:
        variation = st.selectbox("select a variation", base_lift_variations)
    
    default_variation_adj_factor = variations_df[variations_df["variation"] == variation]["variation_pct_of_1RM"].values[0]
else:
    default_variation_adj_factor = 1.0


if "increments" in st.session_state:
    increments = st.session_state.increments
    daily_increment = increments[increments["base_lift"] == base_lift]["daily_increment"].values[0]

if "all_planned_base_lift_progressions" in st.session_state:
    all_planned_base_lift_progressions = st.session_state.all_planned_base_lift_progressions
    planned_base_lift_progression_till_today = (
        all_planned_base_lift_progressions[(all_planned_base_lift_progressions["base_lift"] == base_lift) &
                                           (all_planned_base_lift_progressions["date"] <= pd.Timestamp.today())]
                                           .sort_values("date")
    )
    
    last_day_before_today = pd.to_datetime(planned_base_lift_progression_till_today.tail(1)["date"].values[0])
    last_planned_1RM_before_today = planned_base_lift_progression_till_today.tail(1)["planned_1RM"].values[0]

    today = pd.to_datetime("today").normalize()
    
    if last_day_before_today == today:
        default_1RM = last_planned_1RM_before_today
    else:
        days_since_last_day = (today - last_day_before_today).days
        default_1RM = last_planned_1RM_before_today + days_since_last_day * daily_increment

else:
    default_1RM = 100.0


#---------------------------------------------------------------------------------------------------
# UI
#---------------------------------------------------------------------------------------------------


col1, col2, col3 = st.columns(3)

with col1:
    reps = st.number_input("desired number of reps", min_value = 1, max_value = 30, value = 1)

with col2:
    RPE = st.number_input("desired RPE", min_value = 0.0, max_value = 10.0, value = 8.0, step = .5)

with col3:
    oneRM = st.number_input("your 1RM", min_value = 0.0, value = default_1RM)

col4, col5 = st.columns(2)
with col4:
    interpolation_factor = st.slider("rep capacity factor", min_value = 0.0, max_value = 1.0, value = 0.5)

with col5:
    variation_adj_factor = st.slider("variation adjustment factor", min_value = 0.0, max_value = 2.0, value = default_variation_adj_factor)

recommended_weight = RPE_to_pct(reps, RPE, interpolation_factor, variation_adj_factor) * oneRM


col6, col7 = st.columns(2)
with col6:
    st.metric("recommended weight rounded", round_to_multiple(recommended_weight, round_multiple))

with col7:
    st.metric("recommended weight", round(recommended_weight, 2))


st.divider()

st.write(r"""
        ### Instructions
        This calculator will recommend a weight for a given number of reps and RPE you want to hit based on your 1RM.

        If you have entered a metadata spreadsheet url in the sidebar, you can select a base lift from a dropdown menu.
        The calculator will then use your planned 1RM for today for the selected base lift.

        The calculator is basesd on two tables from the YouTube channel [Data Driven Strength](https://www.youtube.com/watch?v=cy4ZzbAdx9E)
        that map RPE and reps to percentages of your 1RM. The tables are for exercises on which you have a high capacity
        to perform reps and exercises on which you have a low capacity to perform reps.
        
        To match this calculator to your capacity to perform reps, you can adjust the rep capacity factor.
        This yields a percentage of your 1RM that is interpolated between the low and high capacity values.
        $$
        DDS_{interpolated}(reps, RPE) = DDS_{low}(reps, RPE) \cdot (1 - \text{rep capacity factor}) + DDS_{high}(reps, RPE) \cdot \text{rep capacity factor}
        $$
        where $DDS_{low}(reps, RPE)$ and $DDS_{high}(reps, RPE)$ are percentages of your 1RM at the given number of reps and RPE
        from the low or high capacity table.
        The rep capacity factor determines how much the percentage of 1RM will be interpolated between the low and
        high capacity values.

        The formula used to calculate the recommended weight is:
        $$
        weight = DDS_{interpolated}(reps, RPE) \cdot \text{rep capacity factor} \cdot 1RM \cdot \text{variation adjustment factor}
        $$
        The variation adjustment factor scales the percentage of 1RM up or down if you do not perform the competition lift itself
        but some variation in which you are weaker or stronger.

""")

