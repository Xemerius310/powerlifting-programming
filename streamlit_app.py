import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection


#---------------------------------------------------------------------------------------------------
# defining common functions used in multiple pages
#---------------------------------------------------------------------------------------------------

# defining the RPE to percentage of 1RM conversion function
RPE_to_pct_df = pd.read_csv("data/DDS_RPE-to-percent1RM.csv")

# interpolation factor is the factor by which the low and high DDS values will be interpolated
# variation_adj_factor scales the percentage of 1RM based on the variation
def RPE_to_pct(reps, RPE, interpolation_factor, variation_adj_factor = 1.0):
    potential_reps = reps + (10 - RPE)
    RPE_to_pct_df["interpolated"] = (
        variation_adj_factor * (RPE_to_pct_df["DDS_low"] * (1-interpolation_factor) + RPE_to_pct_df["DDS_high"] * interpolation_factor)
    )

    return float(RPE_to_pct_df.loc[RPE_to_pct_df["reps_at_RPE_10"] == potential_reps, "interpolated"])

st.session_state["RPE_to_pct_fun"] = RPE_to_pct


# defining the function for rounding weights to the nearest multiple given
def round_to_multiple(number, multiple):
    """
    Rounds a given number to the nearest specified multiple.

    Parameters:
    - number (float or int): The number to be rounded.
    - multiple (float or int): The multiple to round the number to.

    Returns:
    - float: The number rounded to the nearest specified multiple.
    """
    if multiple == 0:
        return number
    
    if pd.isna(number):
        return pd.NA

    return round(number / multiple) * multiple

st.session_state["round_to_multiple_fun"] = round_to_multiple


with st.sidebar:
    st.session_state["metadata_spreadsheet_url"] = st.text_input(label = "metadata spreadsheet url")
    st.session_state["round_multiple"] = st.number_input(label = "round weights to nearest multiple of", value = 2.5)

#---------------------------------------------------------------------------------------------------
# defining pages
#---------------------------------------------------------------------------------------------------

public_sheet_planning_page = st.Page("navigation/public_sheet_planning.py", title = "📆 Public Sheet Planning")
mesocycle_creator_page = st.Page("navigation/mesocycle_creator.py", title = "🛠️ Mesocycle Creator")
oneRM_calculator_page = st.Page("navigation/calculators.py", title = "🧮 Calculators")
athlete_view_page = st.Page("navigation/athlete_view.py", title = "🏋 Athlete View")
analysis_page = st.Page("navigation/analysis.py", title = "📊 Analysis")
weight_page = st.Page("navigation/weight.py", title = "⚖️ Weight")

navigation = st.navigation(
    [
        public_sheet_planning_page,
        analysis_page,
        mesocycle_creator_page,
        oneRM_calculator_page,
        athlete_view_page,
        weight_page
    ]
)

navigation.run()





