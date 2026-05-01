import random
import json
import numpy as np
from individual import Individual
from utils import remove_ingredients_not_in_level_range,remove_blacklisted_ingredients,sort_ingredients,import_recipe_df,calculate_ingredient_quality_bonus

# ======================
# PARAMÈTRES
# ======================
POP_SIZE = 200
GENERATIONS = 500
MUTATION_RATE = 0.1
LEVEL_MIN = 0
LEVEL_MAX = 104
FOCUSED_STAT = "spellDamage"
INGREDIENT_BLACKLIST = []#["Aspect of the Void"]
ITEM = "scroll"
RAW_RECIPE_PATH = "Recipes.xlsx"
NUMBER_OF_INDIVIDUALS_SELECTED_PER_GENERATION = 80
DURATION_MIN = 600
MIN_MAX_OR_MEAN = "max"
#Le premier ingrédient est celui à gauche sur wynnbuilder
FIRST_INGREDIENT_QUALITY = 1 #1, 2 ou 3 étoiles
SECOND_INGREDIENT_QUALITY = 1 #1, 2 ou 3 étoiles

with open(f"resultat.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = sort_ingredients(data,ITEM)
data = remove_ingredients_not_in_level_range(data,LEVEL_MIN,LEVEL_MAX)    
data = remove_blacklisted_ingredients(data,INGREDIENT_BLACKLIST)


with open("stats.json", "r") as f:
    possible_stats = set(json.load(f))

raw_recipes = import_recipe_df(RAW_RECIPE_PATH,ITEM)

coef = calculate_ingredient_quality_bonus(ITEM,FIRST_INGREDIENT_QUALITY,SECOND_INGREDIENT_QUALITY)
# ======================
# INITIALISATION
# ======================

print("1")
def create_population():
    return [Individual(data=data,item=ITEM,lvl_max=LEVEL_MAX,recipes_df=raw_recipes,ingredient_quality_coefficient=coef) for _ in range(POP_SIZE)]

# ======================
# SÉLECTION
# ======================
print("2")
def roulette_selection(population,fitness):
    total_fitness = sum(ind.fitness(FOCUSED_STAT) for ind in population)
    pick = random.uniform(0, total_fitness)
    current = 0

    for ind in population:
        current += fitness(ind,duration_min = DURATION_MIN)
        if current > pick:
            return ind
        
def sus_selection(population, n_select):
    total_fitness = sum(ind.fitness(FOCUSED_STAT) for ind in population)
    step = total_fitness / n_select
    start = random.uniform(0, step)
    
    points = [start + i * step for i in range(n_select)]
    
    selected = []
    current = 0
    i = 0
    
    for ind in population:
        current += ind.fitness(FOCUSED_STAT)
        while i < len(points) and current >= points[i]:
            selected.append(ind)
            i += 1
    
    return selected        

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
    for generation in range(GENERATIONS):
        new_population = []

        selected_individuals = sus_selection(population,NUMBER_OF_INDIVIDUALS_SELECTED_PER_GENERATION)
        for _ in range(POP_SIZE) :
            #parent1 = sus_selection(population)
            #parent2 = sus_selection(population)
            parent1,parent2 = random.sample(selected_individuals, 2)

            child = crossover(parent1, parent2)
            child = mutation(child)

            new_population.append(child)

        population = new_population

        best = max(population, key=lambda ind: ind.fitness(FOCUSED_STAT,duration_min = DURATION_MIN))
        if best.fitness(FOCUSED_STAT,duration_min = DURATION_MIN)>best_total[1]:
            best_total = (best,best.fitness(FOCUSED_STAT,duration_min = DURATION_MIN))
        print(f"Génération {generation} | Best fitness: {best.fitness(FOCUSED_STAT,duration_min = DURATION_MIN)}")


    #return max(population, key=lambda ind: ind.fitness(FOCUSED_STAT))
    return best_total

# ======================
# EXECUTION
# ======================
if __name__ == "__main__":
    best_solution = genetic_algorithm()
    print("Meilleur score : ", best_solution[1])
    print("Meilleure solution :", best_solution[0].display_recipe())
    print("Matrice de boost : ", best_solution[0].give_boost_array())