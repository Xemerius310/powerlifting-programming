import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection



RPE_to_pct_df = pd.read_csv("data/DDS_RPE-to-percent1RM.csv")

def RPE_to_pct(reps, RPE, interpolation_factor):
    potential_reps = reps + (10 - RPE)
    RPE_to_pct_df["interpolated"] = RPE_to_pct_df["DDS_low"] * (1-interpolation_factor) + RPE_to_pct_df["DDS_high"] * interpolation_factor

    return RPE_to_pct_df.loc[RPE_to_pct_df["reps_at_RPE_10"] == potential_reps, "interpolated"]





metadata_spreadsheet_url = st.text_input(label = "metadata spreadsheet url")


if metadata_spreadsheet_url:
    metadata_conn = st.connection("gsheets", type = GSheetsConnection)
    metadata_df = metadata_conn.read(spreadsheet = metadata_spreadsheet_url, ttl = 5)


    metadata_df.set_index("spreadsheet", inplace = True)

    st.dataframe(metadata_df)

    # planned progression
    planned_progression_conn = st.connection("gsheets", type = GSheetsConnection)
    planned_progression_df = planned_progression_conn.read(spreadsheet = metadata_df.loc["planned_progression", "url"])

    st.dataframe(planned_progression_df)

    # actual progression
    actual_progression_conn = st.connection("gsheets", type = GSheetsConnection)
    actual_progression_df = actual_progression_conn.read(spreadsheet = metadata_df.loc["actual_progression", "url"])

    st.dataframe(actual_progression_df)

    # variations
    variations_conn = st.connection("gsheets", type = GSheetsConnection)
    variations_df = variations_conn.read(spreadsheet = metadata_df.loc["variations", "url"])

    st.dataframe(variations_df)

