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