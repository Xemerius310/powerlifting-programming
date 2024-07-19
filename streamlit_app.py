import streamlit as st
import pandas as pd
import numpy as np
from streamlit_gsheets import GSheetsConnection



# defining pages
public_sheet_planning_page = st.Page("navigation/public_sheet_planning.py", title = "Public Sheet Planning")
mesocycle_creator_page = st.Page("navigation/mesocycle_creator.py", title = "Mesocycle Creator")

navigation = st.navigation([public_sheet_planning_page, mesocycle_creator_page])
navigation.run()

