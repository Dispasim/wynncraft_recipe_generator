import streamlit as st

st.set_page_config(page_title="Recipe Generator", layout="wide")

# -------------------------
# SIDEBAR (GAUCHE)
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
# MAIN PAGE (DROITE)
# -------------------------
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

# -------------------------
# PAGE REGLAGES
# -------------------------    

def advanced_page():
    st.title("🔧 Détails avancés")

    st.write("Réglages et paramètres fins de l'algorithme")

    mutation_rate = st.slider("Mutation rate", 0.0, 1.0, 0.2)
    elitism = st.checkbox("Elitism activé", value=True)
    diversity = st.slider("Diversité population", 0, 100, 50)

    st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "main"
        st.rerun()
