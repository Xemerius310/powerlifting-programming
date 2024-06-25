import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection


url = "https://docs.google.com/spreadsheets/d/1KsKJScBAaXRe723z2yA55rUVXVnVlB7hG-ZzYdnF35A/edit?usp=sharing"

conn = st.connection("gsheets", type = GSheetsConnection)

data = conn.read(spreadsheet = url)
st.dataframe(data)


url = "https://docs.google.com/spreadsheets/d/1tqoOysKmRnTTbE6mBIpnEuPlM3Y2XYZugWJdeYbtI-Q/edit?usp=sharing"


conn2 = st.connection("gsheets", type = GSheetsConnection)

actual_progression = conn2.read(spreadsheet = url)
st.dataframe(actual_progression)

RPE_to_pct_df = pd.read_csv("data/DDS_RPE-to-percent1RM.csv")

def RPE_to_pct(reps, RPE, interpolation_factor):
    potential_reps = reps + (10 - RPE)
    RPE_to_pct_df["interpolated"] = RPE_to_pct_df["DDS_low"] * (1-interpolation_factor) + RPE_to_pct_df["DDS_high"] * interpolation_factor

    st.dataframe(RPE_to_pct_df)
    return RPE_to_pct_df.loc[RPE_to_pct_df["reps_at_RPE_10"] == potential_reps, "interpolated"]



test = RPE_to_pct(6,7,1)


st.write(test)