import streamlit as st
from main import genetic_algorithm

st.title("Recipe Generator")

if st.button("Run"):
    best = genetic_algorithm()
    st.write(best[1])