import streamlit as st
import pandas as pd


RPE_to_pct = st.session_state["RPE_to_pct_fun"]
round_to_multiple = st.session_state["round_to_multiple_fun"]
round_multiple = st.session_state["round_multiple"]


st.markdown("## weight recommendation calculator")

if "variations_df" in st.session_state:
    variations_df = st.session_state.variations_df
    base_lifts = variations_df["base_lift"].unique()

    base_lift = st.selectbox("select a base lift", base_lifts)

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
    RPE = st.number_input("desired RPE", min_value = 0, max_value = 10, value = 8)

with col3:
    oneRM = st.number_input("your 1RM", min_value = 0.0, value = default_1RM)

col4, col5 = st.columns(2)
with col4:
    interpolation_factor = st.slider("rep capacity factor", min_value = 0.0, max_value = 1.0, value = 0.5)

with col5:
    variation_adj_factor = st.slider("variation adjustment factor", min_value = 0.0, value = 1.0)

recommended_weight = RPE_to_pct(reps, RPE, interpolation_factor, variation_adj_factor) * oneRM


col6, col7 = st.columns(2)
with col6:
    st.metric("recommended weight rounded", round_to_multiple(recommended_weight, round_multiple))

with col7:
    st.metric("recommended weight", round(recommended_weight, 2))