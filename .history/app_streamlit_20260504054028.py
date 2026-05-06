import streamlit as st
from genetic_components import create_population,roulette_selection,select_with_elite, select, crossover,mutation
import json


st.set_page_config(page_title="Recipe Generator", layout="wide")
# -------------------------
# IMPORTS DE FICHIERS
# -------------------------

with open("stats.json") as f:
    stats_data = json.load(f)

# -------------------------
# INIT PAGE STATE
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "main"


# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.title("⚙️ Paramètres")

    item = st.selectbox("Item", ["helmet", "chestplate", "boots"])
    stat = st.text_input("Stat", "Melee Damage %")

    level = st.number_input("Level", min_value=1, max_value=120, value=117)
    pop = st.number_input("Population size", value=500)
    gen = st.number_input("Generations", value=100)

    st.divider()

    run = st.button("🚀 Run")

    if st.button("⚙️ Détails avancés"):
        st.session_state.page = "advanced"
        st.rerun()


# -------------------------
# PAGE PRINCIPALE
# -------------------------
def main_page():
    st.title("Recipe Generator")

    if run:
        st.write("Running algo...")

        st.json({
            "item": item,
            "stat": stat,
            "level": level,
            "pop": pop,
            "gen": gen
        })
    st.iframe("https://wynnbuilder-beta.github.io/crafter/#4ixixawaZCZCZ8ga0", height=1700)    


# -------------------------
# PAGE AVANCÉE
# -------------------------
def advanced_page():
    st.title("🔧 Détails avancés")

    mutation_rate = st.slider("Mutation rate", 0.0, 1.0, 0.2)
    elitism = st.checkbox("Elitism activé", value=True)
    diversity = st.slider("Diversité population", 0, 100, 50)

    st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "main"
        st.rerun()


# -------------------------
# ROUTING (IMPORTANT)
# -------------------------
if st.session_state.page == "advanced":
    advanced_page()
else:
    main_page()