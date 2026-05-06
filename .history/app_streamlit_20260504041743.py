import streamlit as st

st.set_page_config(page_title="Réglages", layout="centered")

st.title("⚙️ Réglages")

# -------------------------
# Initialisation des valeurs
# -------------------------
if "settings" not in st.session_state:
    st.session_state.settings = {
        "level_max": 120,
        "pop_size": 500,
        "generations": 100,
        "duration_min": 20
    }

settings = st.session_state.settings

# -------------------------
# Formulaire réglages
# -------------------------
with st.form("settings_form"):

    st.subheader("Paramètres de l'algorithme")

    level_max = st.slider(
        "Niveau max",
        min_value=1,
        max_value=120,
        value=settings["level_max"]
    )

    pop_size = st.number_input(
        "Population size",
        min_value=10,
        max_value=5000,
        value=settings["pop_size"]
    )

    generations = st.number_input(
        "Generations",
        min_value=1,
        max_value=5000,
        value=settings["generations"]
    )

    duration_min = st.number_input(
        "Duration min",
        min_value=0,
        max_value=1000,
        value=settings["duration_min"]
    )

    submitted = st.form_submit_button("💾 Sauvegarder")

    if submitted:
        st.session_state.settings = {
            "level_max": level_max,
            "pop_size": pop_size,
            "generations": generations,
            "duration_min": duration_min
        }

        st.success("Réglages sauvegardés ✔️")