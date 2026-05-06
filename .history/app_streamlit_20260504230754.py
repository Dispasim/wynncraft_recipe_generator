import streamlit as st
from genetic_components import create_population,select_with_elite, select, crossover,mutation
from utils import remove_ingredients_not_in_level_range,remove_blacklisted_ingredients,sort_ingredients,import_recipe_df,calculate_ingredient_quality_bonus,remove_useless_ingredients,give_ingredients_list,get_ingredient_from_string, update_best_archive, update_best_archive_fast
import json
import random
import copy
from individual import Individual

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

if "data" not in st.session_state :
    st.session_state.data = data   

if "pop_size" not in st.session_state:
    st.session_state.pop_size = 500

if "gen" not in st.session_state:
    st.session_state.gen = 100

if "x" not in st.session_state:
    st.session_state.x = 5    

if "n_select" not in st.session_state:
    st.session_state.n_select = 100   

if "mutation_rate" not in st.session_state:
    st.session_state.mutation_rate = 0.1    

if "elitism" not in st.session_state:
    st.session_state.elitism = False     

if "elite_ratio" not in st.session_state:
    st.session_state.elite_ratio = 0.1    

if "lvl_min" not in st.session_state:
    st.session_state.lvl_min = 0        

if "blacklist" not in st.session_state:
        st.session_state.blacklist = []

if "method" not in st.session_state:
    st.session_state.method = "sus"        

if "min_max_or_mean" not in st.session_state:
    st.session_state.min_max_or_mean = "mean"          



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
        index=stats_list.index("Gather XP Bonus") if "Gather XP Bonus" in stats_list else 0
    )

    translated_stat = stats_data[stat]

    level = st.number_input("Level", min_value=1, max_value=120, value=105)
    duration_or_durability = "Duration" if item in ["potion","scroll","food"] else "Durability"

    duration_min = st.number_input(duration_or_durability, min_value=1, value=600)

    st.subheader("Qualité du matériau")

    ingredient_one = {"helmet": "Ingot","chestplate" : "Ingot", "leggings" : "Ingot", "boots" : "Ingot", "relik" : "Oil", "wand" : "String", "bow" : "String", "spear" : "Ingot", "dagger" : "Ingot", "ring" : "Gem", "necklace" : "Gem", "bracelet" : "Gem", "potion" : "Oil", "scroll" : "Oil", "food" : "Meat"}

    ingredient_two = {"helmet": "Papier", "chestplate" : "Paper", "leggings" : "String", "boots" : "String", "relik" : "Planks", "wand" : "Planks", "bow" : "Planks", "spear" : "Planks", "dagger" : "Planks", "ring" : "Oil", "necklace" : "Oil", "bracelet" : "Oil", "potion" : "Grains", "scroll" : "Paper", "food" : "Grains"}

    quality_one = st.radio(
        ingredient_one[item],
        options=[1, 2, 3],
        format_func=lambda x: "⭐" * x
    )

    quality_two = st.radio(
        ingredient_two[item],
        options=[1, 2, 3],
        format_func=lambda x: "⭐" * x
    )

    stats = ["Strength", "Dexterity", "Intelligence", "Defense", "Agility"]

    req_values = {}

    st.subheader("Prérequis")

    for stat in stats:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(stat)

        with col2:
            req_values[stat] = st.number_input(
                label=f"{stat}_input",
                min_value=0,
                max_value=150,
                value=0,
                label_visibility="collapsed"
            )

    #st.write(type(values))
    
    st.divider()

    run = st.button("🚀 Run")

    if st.button("⚙️ Détails avancés"):
        if st.session_state.page == "advanced":
            st.session_state.page = "main"
        else:         
            st.session_state.page = "advanced"
        st.rerun()

    if st.button("🧪 Tests"):
        if st.session_state.page == "test":
            st.session_state.page = "main"
        else:   
            st.session_state.page = "test"
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

        data = st.session_state.data

        pop_size = st.session_state.pop_size
        generations = st.session_state.gen
        elitism = st.session_state.elitism
        elite_ratio = st.session_state.elite_ratio
        n_select = st.session_state.n_select
        min_max_or_mean = st.session_state.min_max_or_mean
        lvl_min = st.session_state.lvl_min
        method = st.session_state.method
        mutation_rate = st.session_state.mutation_rate
        req_stats = list(req_values.values())

        st.session_state.req_stats = req_stats

        ingredient_quality_coefficient = calculate_ingredient_quality_bonus(item,quality_one,quality_two)    

        raw_recipes = import_recipe_df("ressources/Recipes.xlsx",item)

        data = sort_ingredients(data,item)
        data = remove_ingredients_not_in_level_range(data,lvl_min,level)    
        data = remove_blacklisted_ingredients(data,st.session_state.blacklist)
        data = remove_useless_ingredients(data,translated_stat,item)

        # init population
        population = create_population(data=data, item=item, lvl_max=level,
                                    recipe_df=raw_recipes,
                                    ingredient_quality_coefficient=ingredient_quality_coefficient,
                                    pop_size=pop_size)
        best_archive = {}
        #best_total = (None,0)
        for gen_idx in range(generations):
            # 🔹 Ton algo génétique
            if elitism:
                selected = select_with_elite(population=population,translated_stat=translated_stat,duration_min=duration_min,min_max_or_mean = min_max_or_mean, req_stats=st.session_state.req_stats,method=method,n_select=n_select,elite_ratio=elite_ratio)
            else:    
                selected = select(population=population,translated_stat=translated_stat,duration_min=duration_min,min_max_or_mean = min_max_or_mean, req_stats=st.session_state.req_stats,method=method,n_select=n_select)
            new_pop = []
            for _ in range(pop_size):
                parent1,parent2 = random.sample(selected, 2)
                offspring = crossover(parent1,parent2,data,item,level,raw_recipes,ingredient_quality_coefficient)
                offspring_ = mutation(offspring,data,mutation_rate)
                new_pop.append(offspring_)
            population = copy.deepcopy(new_pop)
            # 🔹 Update UI
            progress = int((gen_idx + 1) / generations * 100)
            progress_bar.progress(progress)

            #best = max(population, key=lambda ind: ind.fitness(translated_stat,duration_min = duration_min, min_max_or_mean = min_max_or_mean, req_stats = st.session_state.req_stats))
            #if best.fitness(translated_stat,duration_min = duration_min, min_max_or_mean = min_max_or_mean, req_stats = st.session_state.req_stats)>best_total[1]:
            #    best_total = (copy.deepcopy(best),best.fitness(translated_stat,duration_min = duration_min, min_max_or_mean = min_max_or_mean, req_stats = st.session_state.req_stats))
            best_archive = update_best_archive_fast(
                best_archive,
                population,
                x=st.session_state.x,
                fitness_fn=lambda ind: ind.fitness(
                    stat=translated_stat,
                    duration_min=duration_min,
                    min_max_or_mean=min_max_or_mean,
                    req_stats=req_stats),
                    hash_fn=lambda ind: ind.encode_wynn_craft_hash([quality_one, quality_two]))
            

            #best = max([best] + population, key=lambda ind: ind.fitness(stat=translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = st.session_state.req_stats))

            #status_text.text(f"Génération {gen_idx + 1}/{generations}\nBest fitness = {best.fitness(stat=translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = st.session_state.req_stats)}")
            #status_text.text(f"Génération {gen_idx + 1}/{generations}\nBest fitness = {best_archive[0][1]}")
            status_text.text(f"Génération {gen_idx + 1}/{generations}")
            



        st.success("Algo terminé ✅")

        # 👉 afficher le meilleur individu si tu veux
        #best = max(population, key=lambda ind: ind.fitness)
        #st.write("Best fitness:", best.fitness(stat=translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = st.session_state.req_stats))


        for h, (fit, ind) in best_archive.items():
            st.write("Best fitness:", fit)
            st.write(f"Hash : CR-{h}")
            st.write(f"lien : https://wynnbuilder-beta.github.io/crafter/#{h}")
            st.iframe(f"https://wynnbuilder-beta.github.io/crafter/#{h}", height=1700)

        """st.write("Best fitness:", best_total[1])
        st.write(f"Hash : CR-{best_total[0].encode_wynn_craft_hash([quality_one,quality_two])}")
        st.write(f"lien : https://wynnbuilder-beta.github.io/crafter/#{best_total[0].encode_wynn_craft_hash([quality_one,quality_two])}")
        st.iframe(f"https://wynnbuilder-beta.github.io/crafter/#{best_total[0].encode_wynn_craft_hash([quality_one,quality_two])}", height=1700)"""

# -------------------------
# PAGE AVANCÉE
# -------------------------
def advanced_page():
    st.title("🔧 Détails avancés")

    st.session_state.pop_size = st.number_input("Population size",min_value=0, value=500)
    st.session_state.gen = st.number_input("Generations",min_value=0, value=100)
    st.session_state.x = st.number_input("Nombre de résultats affichés",min_value=0, value=5)
    st.session_state.n_select = st.number_input("Nombre d'individus sélectionnés par génération",min_value=0, value=100)
    st.session_state.mutation_rate = st.number_input("Mutation rate", min_value=0.0, max_value=1.0,  value=0.1)
    st.session_state.elitism = st.checkbox("Elitism activé", value=False)
    st.session_state.elite_ratio = st.number_input("Elite ratio", min_value=0.0, max_value=1.0,  value=0.1)
    
    st.session_state.min_max_or_mean = st.selectbox("Way to juge stats", ["mean","max","min"])
    st.session_state.lvl_min = st.number_input("Niveau minimum des ingrédients",min_value=0,max_value=200, value=0)
    st.session_state.method = st.selectbox("Méthode de sélection", ["sus","tournament","roulette","rank", "boltz"])


    

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
# PAGE TEST
# -------------------------
def test_page():

    col1, col2 = st.columns(2)

    with col1:
        ingredient_1 = st.selectbox(
            "Ingrédient 1",
            options=ingredients_list
        )

        ingredient_3 = st.selectbox(
            "Ingrédient 3",
            options=ingredients_list
        )

        ingredient_5 = st.selectbox(
            "Ingrédient 5",
            options=ingredients_list
        )

    with col2:
        ingredient_2 = st.selectbox(
            "Ingrédient 2",
            options=ingredients_list
        )

        ingredient_4 = st.selectbox(
            "Ingrédient 4",
            options=ingredients_list
        )

        ingredient_6 = st.selectbox(
            "Ingrédient 6",
            options=ingredients_list
        )

    if st.button("generate"):
        ind = Individual(data=data,recipes_df = import_recipe_df("ressources/Recipes.xlsx",item),item = item,chosen_ingredients=[get_ingredient_from_string(data,ingredient_1),get_ingredient_from_string(data,ingredient_2),get_ingredient_from_string(data,ingredient_3),get_ingredient_from_string(data,ingredient_4),get_ingredient_from_string(data,ingredient_5),get_ingredient_from_string(data,ingredient_6)],lvl_max=level,ingredient_quality_coefficient=calculate_ingredient_quality_bonus(item,quality_one,quality_two))
        st.write("Score:", ind.fitness(stat=translated_stat,duration_min=duration_min,min_max_or_mean=st.session_state.min_max_or_mean,req_stats=list(req_values.values())))
        st.write("Matrice de boost :")
        st.write(ind.give_boost_array())
        st.write(f"stats : {ind.show_stats()}")
        st.write(f"Duration : {ind.duration}")

        st.write(f"Hash : CR-{ind.encode_wynn_craft_hash([quality_one,quality_two])}")
        st.write(f"lien : https://wynnbuilder-beta.github.io/crafter/#{ind.encode_wynn_craft_hash([quality_one,quality_two])}")
        st.iframe(f"https://wynnbuilder-beta.github.io/crafter/#{ind.encode_wynn_craft_hash([quality_one,quality_two])}", height=1700)

        
    st.divider()

    if st.button("⬅ Retour"):
        st.session_state.page = "main"
        st.rerun()



# -------------------------
# ROUTING (IMPORTANT)
# -------------------------
if st.session_state.page == "advanced":
    advanced_page()
elif st.session_state.page == "test":   
    test_page() 
else:
    main_page()