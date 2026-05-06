import streamlit as st
from genetic_components import create_population,roulette_selection,select_with_elite, select, crossover,mutation
import json


st.set_page_config(page_title="Recipe Generator", layout="wide")
# -------------------------
# IMPORTS DE FICHIERS
# -------------------------

with open("ressources/stats.json") as f:
    stats_data = json.load(f)

stats_list = list(stats_data.keys())
# -------------------------
# INIT PAGE STATE
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "main"

if "pop" not in st.session_state:
    st.session_state.pop = 500

if "gen" not in st.session_state:
    st.session_state.gen = 100
# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.title("⚙️ Paramètres")

    item = st.selectbox("Item", ["chestplate",
                    "helmet",
                    "leggings",
                    "boots",
                    "relik",
                    "wand",
                    "spear",
                    "dagger",
                    "bow",
                    "ring",
                    "necklace",
                    "bracelet",
                    "potion",
                    "scroll",
                    "food"])
    stat = st.selectbox(
        "Stat",
        options=stats_list,
        index=stats_list.index("Melee Damage %") if "Melee Damage %" in stats_list else 0
    )

    translated_stat = stats_data[stat]

    level = st.number_input("Level", min_value=1, max_value=120, value=117)
    
    st.divider()

    run = st.button("🚀 Run")

    if st.button("⚙️ Détails avancés"):
        st.session_state.page = "advanced"
        st.rerun()

# -------------------------
# PAGE AVANCÉE
# -------------------------
def advanced_page():
    st.title("🔧 Détails avancés")

    st.session_state.mutation_rate = st.slider("Mutation rate", 0.0, 1.0, 0.2)
    st.session_state.elitism = st.checkbox("Elitism activé", value=True)
    st.session_state.diversity = st.slider("Diversité population", 0, 100, 50)
    st.session_state.pop = st.number_input("Population size", value=500)
    st.session_state.gen = st.number_input("Generations", value=100)

    st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "main"
        st.rerun()

# -------------------------
# PAGE PRINCIPALE
# -------------------------
def main_page():
    st.title("Recipe Generator")

    if run:
        st.write("Running algo...")

        progress_bar = st.progress(0)
        status_text = st.empty()

        pop_size = st.session_state.pop
        generations = st.session_state.gen

        # init population
        population = create_population(data=None, item=item, lvl_max=level,
                                    recipe_df=None,
                                    ingredient_quality_coefficient=None,
                                    pop_size=pop_size)

        for gen_idx in range(generations):
            # 🔹 Ton algo génétique
            selected = select(population)
            offspring = crossover(selected)
            population = mutation(offspring)

            # 🔹 Update UI
            progress = int((gen_idx + 1) / generations * 100)
            progress_bar.progress(progress)

            status_text.text(f"Génération {gen_idx + 1}/{generations}")

        st.success("Algo terminé ✅")

        # 👉 afficher le meilleur individu si tu veux
        best = max(population, key=lambda ind: ind.fitness)
        st.write("Best fitness:", best.fitness)
        

    has_result= False 

    if has_result:  
        st.iframe("https://wynnbuilder-beta.github.io/crafter/#4ixixawaZCZCZ8ga0", height=1700)    





# -------------------------
# ROUTING (IMPORTANT)
# -------------------------
if st.session_state.page == "advanced":
    advanced_page()
else:
    main_page()