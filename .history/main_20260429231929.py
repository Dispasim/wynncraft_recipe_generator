import random
import json
import numpy as np
from individual import Individual,remove_ingredients_not_in_level_range

# ======================
# PARAMÈTRES
# ======================
POP_SIZE = 20
GENERATIONS = 50
MUTATION_RATE = 0.1
DURABILITY_MIN = 100
LEVEL_MIN = 0
LEVEL_MAX = 105
FOCUSED_STAT = "waterDamage"


with open("resultat_scribing.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = remove_ingredients_not_in_level_range(data,LEVEL_MIN,LEVEL_MAX)    

with open("stats.json", "r") as f:
    possible_stats = set(json.load(f))

# ======================
# INITIALISATION
# ======================


def create_population():
    return [Individual(data=data,lvl_min=LEVEL_MIN,lvl_max=LEVEL_MAX) for _ in range(POP_SIZE)]

# ======================
# SÉLECTION
# ======================
def roulette_selection(population,fitness):
    total_fitness = sum(ind.fitness(FOCUSED_STAT) for ind in population)
    pick = random.uniform(0, total_fitness)
    current = 0

    for ind in population:
        current += fitness(ind)
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
        current += ind["fitness"]
        while i < len(points) and current >= points[i]:
            selected.append(ind)
            i += 1
    
    return selected        

# ======================
# CROSSOVER
# ======================
def crossover(parent1, parent2):
    crossover_ingredients = [parent1[i] for i in [0,2,4]] + [parent2[i] for i in [1,3,5]]
    child = Individual(data,chosen_ingredients=crossover_ingredients)
    return child

# ======================
# MUTATION
# ======================

#Pour la mutation, je remplace un ingredient par un autre aléatoire
def mutation(ind):
    if random.random() < MUTATION_RATE:
        ind.recipe[random.randint(0, 2),random.randint(0, 1)] = random.choice(data)
    return ind

# ======================
# ALGO PRINCIPAL
# ======================
def genetic_algorithm():
    population = create_population()

    for generation in range(GENERATIONS):
        new_population = []

        for _ in range(POP_SIZE):
            parent1 = sus_selection(population)
            parent2 = sus_selection(population)

            child = crossover(parent1, parent2)
            child = mutation(child)

            new_population.append(child)

        population = new_population

        best = max(population, key=lambda ind: ind.fitness())
        print(f"Génération {generation} | Best fitness: {best.fitness()}")

    return max(population, key=lambda ind: ind.fitness())

# ======================
# EXECUTION
# ======================
if __name__ == "__main__":
    best_solution = genetic_algorithm()
    print("Meilleure solution :", best_solution.display_recipe)