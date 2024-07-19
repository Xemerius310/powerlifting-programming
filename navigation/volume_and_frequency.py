import streamlit as st

sex = st.radio(label = "sex", options = ["male", "female"])

col1, col2, col3 = st.columns(3)

with col1:
    weight = st.number_input(min_value = 0, label = "weight")
    squat_1RM = st.number_input(min_value = 0, label = "squat 1RM")

with col2:
    height = st.number_input(min_value = 0, label = "height")
    bench_1RM = st.number_input(min_value = 0, label = "bench 1RM")


with col3:
    age = st.number_input(min_value = 0, label = "age")
    deadlift_1RM = st.number_input(min_value = 0, label = "deadlift 1RM")

col4, col5, col6 = st.columns(3)


    