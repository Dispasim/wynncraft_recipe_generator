import streamlit as st
from genetic_components import create_population,roulette_selection,select_with_elite, select, crossover,mutation
from utils import timer,remove_ingredients_not_in_level_range,remove_blacklisted_ingredients,sort_ingredients,import_recipe_df,calculate_ingredient_quality_bonus,translate_stat,remove_useless_ingredients,give_ingredients_list
import json


st.set_page_config(page_title="Recipe Generator", layout="wide")
# -------------------------
# IMPORTS DE FICHIERS
# -------------------------

with open(f"ressources/ingreds_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients_list  = give_ingredients_list(data)

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

if "mutation_rate" not in st.session_state:
    st.session_state.mutation_rate = 0.1    

if "elitism" not in st.session_state:
    st.session_state.elitism = False     

if "lvl_min" not in st.session_state:
    st.session_state.lvl_min = 0        

if "blacklist" not in st.session_state:
        st.session_state.blacklist = []


# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.title("⚙️ Paramètres")

    item = st.selectbox("Item", ["scroll","chestplate",
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
                    "food"])
    stat = st.selectbox(
        "Stat",
        options=stats_list,
        index=stats_list.index("Loot Quality") if "Loot Quality" in stats_list else 0
    )

    translated_stat = stats_data[stat]

    level = st.number_input("Level", min_value=1, max_value=120, value=105)
    duration_or_durability = "Duration" if item in ["potion","scroll","food"] else "Durability"

    duration_min = st.number_input(duration_or_durability, min_value=1, value=100)

    st.subheader("Qualité du matériau")

    ingredient_one = {"Helmet": "Ingot","Chestplate" : "Ingot", "leggings" : "Ingot", "Boots" : "Ingot", "Relik" : "Oil", "Wand" : "String", "Bow" : "String", "Spear" : "Ingot", "Dagger" : "Ingot", "Ring" : "Gem", "Necklace" : "Gem", "Bracelet" : "Gem", "Potion" : "Oil", "Scroll" : "Oil", "Food" : "Meat"}

    ingredient_two = {"Helmet": "Papier", "Chestplate" : "Paper", "leggings" : "String", "Boots" : "String", "Relik" : "Planks", "Wand" : "Planks", "Bow" : "Planks", "Spear" : "Planks", "Dagger" : "Planks", "Ring" : "Oil", "Necklace" : "Oil", "Bracelet" : "Oil", "Potion" : "Grains", "Scroll" : "Paper", "Food" : "Grains"}

    quality = st.radio(
        "Qualité",
        options=[1, 2, 3],
        format_func=lambda x: "⭐" * x
    )

    stats = ["Strength", "Dexterity", "Intelligence", "Defense", "Agility"]

    values = {}

    st.subheader("Prérequis")

    for stat in stats:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(stat)

        with col2:
            values[stat] = st.number_input(
                label=f"{stat}_input",
                min_value=0,
                max_value=150,
                value=0,
                label_visibility="collapsed"
            )

    #st.write(values)
    
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

        

        progress_bar = st.progress(0)
        status_text = st.empty()

        pop_size = st.session_state.pop
        generations = st.session_state.gen
        mean_max_or_mean = st.session_state.mean_max_or_mean
        lvl_min = st.session_state.lvl_min

        raw_recipes = import_recipe_df("ressources/Recipes.xlsx",item)

        data = sort_ingredients(data,item)
        data = remove_ingredients_not_in_level_range(data,lvl_min,level)    
        data = remove_blacklisted_ingredients(data,INGREDIENT_BLACKLIST)

        # init population
        population = create_population(data=None, item=item, lvl_max=level,
                                    recipe_df=raw_recipes,
                                    ingredient_quality_coefficient=None,
                                    pop_size=pop_size)

        for gen_idx in range(generations):
            # 🔹 Ton algo génétique
            selected = select(population,translated_stat,duration_min,mean_max_or_mean)
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
# PAGE AVANCÉE
# -------------------------
def advanced_page():
    st.title("🔧 Détails avancés")

    st.session_state.mutation_rate = st.number_input("Mutation rate", min_value=0.0, max_value=1.0,  value=0.1)
    st.session_state.elitism = st.checkbox("Elitism activé", value=False)
    st.session_state.pop = st.number_input("Population size",min_value=0, value=500)
    st.session_state.gen = st.number_input("Generations",min_value=0, value=100)
    st.session_state.min_max_or_mean = st.selectbox("Way to juge stats", ["mean","max","min"])
    st.session_state.lvl_min = st.number_input("Niveau minimum des ingrédients",min_value=0,max_value=200, value=0)


    

    st.subheader("Blacklist")

    st.session_state.blacklist = st.multiselect(
        "Ingrédients à exclure",
        options=ingredients_list,
        default=st.session_state.blacklist
    )


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