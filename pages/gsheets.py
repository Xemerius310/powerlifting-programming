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

data2 = conn2.read(spreadsheet = url)
st.dataframe(data2)