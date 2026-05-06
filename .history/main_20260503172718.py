import random
import json
import numpy as np
from individual import Individual
from utils import remove_ingredients_not_in_level_range,remove_blacklisted_ingredients,sort_ingredients,import_recipe_df,calculate_ingredient_quality_bonus,translate_stat,remove_useless_ingredients
from tqdm.auto import tqdm
import math

# ======================
# PARAMÈTRES
# ======================
POP_SIZE = 2000
GENERATIONS = 200
MUTATION_RATE = 0.1
LEVEL_MIN = 0
LEVEL_MAX = 104
FOCUSED_STAT = "Gather XP Bonus"
INGREDIENT_BLACKLIST = []
ITEM = "scroll"
RAW_RECIPE_PATH = "Recipes.xlsx"
NUMBER_OF_INDIVIDUALS_SELECTED_PER_GENERATION = 800
DURATION_MIN = 600
MIN_MAX_OR_MEAN = "max"
#Le premier ingrédient est celui à gauche sur wynnbuilder
FIRST_INGREDIENT_QUALITY = 3 #1, 2 ou 3 étoiles
SECOND_INGREDIENT_QUALITY = 3 #1, 2 ou 3 étoiles
SELECTION_METHOD = "sus" #sus, tournament, roulette, rank ou boltz
USE_ELITE = False
TOURNAMENT_SELECTION_ROUND = 3
BOLTZMANN_SELECTION_TEMPERATURE = 1.0
REQ_MAX = [100,100,100,100,100] #dans l'ordre : str,dex,int,def,agi

with open(f"ingreds_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = sort_ingredients(data,ITEM)
data = remove_ingredients_not_in_level_range(data,LEVEL_MIN,LEVEL_MAX)    
data = remove_blacklisted_ingredients(data,INGREDIENT_BLACKLIST)

with open("stats.json", "r") as f:
    possible_stats = set(json.load(f))

raw_recipes = import_recipe_df(RAW_RECIPE_PATH,ITEM)

coef = calculate_ingredient_quality_bonus(ITEM,FIRST_INGREDIENT_QUALITY,SECOND_INGREDIENT_QUALITY)

TRANSLATED_STAT = translate_stat(FOCUSED_STAT)

#data = remove_useless_ingredients(data,TRANSLATED_STAT,ITEM)
#for ing in data:
#    print(ing["name"])

#raise ValueError
#%% Génétique


# ======================
# INITIALISATION
# ======================

def create_population():
    return [Individual(data=data,item=ITEM,lvl_max=LEVEL_MAX,recipes_df=raw_recipes,ingredient_quality_coefficient=coef) for _ in range(POP_SIZE)]

# ======================
# SÉLECTION
# ======================
def roulette_selection(population, n_select):
    fitnesses = [
        ind.fitness(FOCUSED_STAT, duration_min=DURATION_MIN, min_max_or_mean=MIN_MAX_OR_MEAN, req_stats = REQ_MAX)
        for ind in population
    ]
    
    total = sum(fitnesses)
    selected = []
    
    for _ in range(n_select):
        pick = random.uniform(0, total)
        current = 0
        
        for ind, fit in zip(population, fitnesses):
            current += fit
            if current >= pick:
                selected.append(ind)
                break
    
    return selected
        
def sus_selection(population, n_select):
    total_fitness = sum(ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX) for ind in population)
    step = total_fitness / n_select
    start = random.uniform(0, step)
    
    points = [start + i * step for i in range(n_select)]
    
    selected = []
    current = 0
    i = 0
    
    for ind in population:
        current += ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX)
        while i < len(points) and current >= points[i]:
            selected.append(ind)
            i += 1
    
    return selected  

def tournament_selection(population, n_select, k=TOURNAMENT_SELECTION_ROUND):
    selected = []
    
    for _ in range(n_select):
        tournament = random.sample(population, k)
        winner = max(
            tournament,
            key=lambda ind: ind.fitness(TRANSLATED_STAT, duration_min=DURATION_MIN, min_max_or_mean=MIN_MAX_OR_MEAN, req_stats = REQ_MAX)
        )
        selected.append(winner)
    
    return selected 

def rank_selection(population, n_select):
    sorted_pop = sorted(
        population,
        key=lambda ind: ind.fitness(TRANSLATED_STAT, duration_min=DURATION_MIN, min_max_or_mean=MIN_MAX_OR_MEAN, req_stats = REQ_MAX)
    )
    
    ranks = list(range(1, len(sorted_pop) + 1))
    total = sum(ranks)
    
    selected = []
    
    for _ in range(n_select):
        pick = random.uniform(0, total)
        current = 0
        
        for ind, rank in zip(sorted_pop, ranks):
            current += rank
            if current >= pick:
                selected.append(ind)
                break
    return selected     

#à combiner avec sus ou tournoi 
def elitism_selection(population, n_elite):
    return sorted(
        population,
        key=lambda ind: ind.fitness(TRANSLATED_STAT, duration_min=DURATION_MIN, min_max_or_mean=MIN_MAX_OR_MEAN, req_stats = REQ_MAX),
        reverse=True
    )[:n_elite]


def boltzmann_selection(population, n_select, T=BOLTZMANN_SELECTION_TEMPERATURE):
    fitnesses = [
        ind.fitness(TRANSLATED_STAT, duration_min=DURATION_MIN, min_max_or_mean=MIN_MAX_OR_MEAN, req_stats = REQ_MAX)
        for ind in population
    ]
    
    exp_values = [math.exp(f / T) for f in fitnesses]
    total = sum(exp_values)
    
    selected = []
    
    for _ in range(n_select):
        pick = random.uniform(0, total)
        current = 0
        
        for ind, val in zip(population, exp_values):
            current += val
            if current >= pick:
                selected.append(ind)
                break
    
    return selected

SELECTION_METHODS = {
    "sus": sus_selection,
    "tournament": tournament_selection,
    "roulette": roulette_selection,
    "rank": rank_selection,
    "boltz": boltzmann_selection
}

def select_with_elite(population, method="tournament", n_select=80, elite_ratio = 0.1, **kwargs):
    n_elite = int(n_select*elite_ratio)
    elite = elitism_selection(population, n_elite)
    
    rest = SELECTION_METHODS[method](
        population,
        n_select - n_elite,
        **kwargs
    )
    
    return elite + rest

def select(population, method="sus", n_select=80, **kwargs):
    if method not in SELECTION_METHODS:
        raise ValueError(f"Unknown selection method: {method}")
    
    return SELECTION_METHODS[method](population, n_select, **kwargs)

# ======================
# CROSSOVER
# ======================
def crossover(parent1, parent2):
    crossover_ingredients = [parent1.recipe.flat[i] for i in [0,2,4]] + [parent2.recipe.flat[i] for i in [1,3,5]]
    child = Individual(data,chosen_ingredients=crossover_ingredients,item=ITEM,lvl_max=LEVEL_MAX,recipes_df=raw_recipes,ingredient_quality_coefficient=coef)
    return child

# ======================
# MUTATION
# ======================

#Pour la mutation, je remplace un ingredient par un autre aléatoire
def mutation(ind):
    if random.random() < MUTATION_RATE:
        ind.recipe[random.randint(0, 2),random.randint(0, 1)] = random.choice(data)
        ind.recalculate_duration()
    return ind

# ======================
# ALGO PRINCIPAL
# ======================
def genetic_algorithm():
    population = create_population()
    best_total  = (None,0)
    for generation in tqdm(range(GENERATIONS),desc="Processing..."):
        new_population = []

        #selected_individuals = sus_selection(population,NUMBER_OF_INDIVIDUALS_SELECTED_PER_GENERATION)
        if USE_ELITE:
            selected_individuals = select_with_elite(population,method=SELECTION_METHOD,n_select=NUMBER_OF_INDIVIDUALS_SELECTED_PER_GENERATION)
        else:
            selected_individuals = select(population,method=SELECTION_METHOD,n_select=NUMBER_OF_INDIVIDUALS_SELECTED_PER_GENERATION)
        for _ in range(POP_SIZE) :
            #parent1 = sus_selection(population)
            #parent2 = sus_selection(population)
            parent1,parent2 = random.sample(selected_individuals, 2)

            child = crossover(parent1, parent2)
            child = mutation(child)

            new_population.append(child)

        population = new_population

        best = max(population, key=lambda ind: ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX))
        if best.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX)>best_total[1]:
            best_total = (best,best.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX))
        print(f"Génération {generation} | Best fitness: {best.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX)}")


    #return max(population, key=lambda ind: ind.fitness(TRANSLATED_STAT))
    return best_total
#%%Greddy 


def greedy_search(data):
    best_total  = (None,0)
    for ing1 in tqdm(data,desc = "1"):
        for ing2 in data:
            for ing3 in data:
                for ing4 in data:
                    for ing5 in data:
                        for ing6 in data:
                            ind = Individual(data,chosen_ingredients = [ing1,ing2,ing3,ing4,ing5,ing6],item=ITEM,lvl_max=LEVEL_MAX,recipes_df=raw_recipes,ingredient_quality_coefficient=coef)
                            fitness = ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX)
                            if fitness > best_total[1]:
                                best_total = (ind,fitness)
    return best_total

def greedy_search2(data):
    best_total  = (None,0)
    ind = Individual(data=data,item=ITEM,lvl_max=LEVEL_MAX,recipes_df=raw_recipes,ingredient_quality_coefficient=coef)
    for ing1 in tqdm(data,desc = "1"):
        for ing2 in data:
            for ing3 in data:
                for ing4 in data:
                    for ing5 in data:
                        for ing6 in data:
                            
                            ind.recipe = np.array([[ing1,ing2],
                                                    [ing3,ing4],
                                                    [ing5,ing6]])
                            ind.recalculate_duration()
                            #fitness = ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN)
                            if ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX) > best_total[1]:
                                best_total = (ind,ind.fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX))
    return best_total


# ======================
# EXECUTION
# ======================
if __name__ == "__main__":
    best_solution = genetic_algorithm()
    #best_solution = greedy_search2(data)
    print(f"Meilleur score : {best_solution[1]}")
    print(f"Meilleur score : {best_solution[0].fitness(TRANSLATED_STAT,duration_min = DURATION_MIN, min_max_or_mean = MIN_MAX_OR_MEAN, req_stats = REQ_MAX)}")
    print(f"Meilleure solution : {best_solution[0].display_recipe()}")
    print(f"Matrice de boost : {best_solution[0].give_boost_array()}")
    print(f"stats : {best_solution[0].show_stats()}")
    print(f"Hash : CR-{best_solution[0].encode_wynn_craft_hash([FIRST_INGREDIENT_QUALITY,SECOND_INGREDIENT_QUALITY])}")
    print(f"lien : https://wynnbuilder-beta.github.io/crafter/#{best_solution[0].encode_wynn_craft_hash([FIRST_INGREDIENT_QUALITY,SECOND_INGREDIENT_QUALITY])}")


    