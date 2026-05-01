import random
import json
import numpy as np

# ======================
# PARAMÈTRES
# ======================
POP_SIZE = 20
GENERATIONS = 50
MUTATION_RATE = 0.1
DURABILITY_MIN = 100
LEVEL_MAX = 120


with open("resultat_scribing.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ======================
# INITIALISATION
# ======================

class individual:
    def __init__(self,data):
        chosen_ingredients = random.choices(data, k=6)

        while sum(ing["consumableOnlyIDs"]["duration"] for ing in self.chosen_ingredients) < 0:
            chosen_ingredients = random.choices(data, k=6)

        self.recipe = np.array([[chosen_ingredients[0],chosen_ingredients[1]],
                     [chosen_ingredients[2],chosen_ingredients[3]],
                     [chosen_ingredients[4],chosen_ingredients[5]]])
        self.durability = sum(ing["consumableOnlyIDs"]["duration"] for ing in chosen_ingredients) 

    def fitness(self,stat):   
        #dans un premier temps, fitness ne vise qu'un seule stat







def create_individual(data):
    chosen_ingredients = random.choices(data, k=6)

    while sum(ing["consumableOnlyIDs"]["duration"] for ing in chosen_ingredients) < 0:
        chosen_ingredients = random.choices(data, k=6)

    recipe = np.array([[chosen_ingredients[0],chosen_ingredients[1]],
                     [chosen_ingredients[2],chosen_ingredients[3]],
                     [chosen_ingredients[4],chosen_ingredients[5]]])
    
    return {"recipe" : recipe,
            "durability" : sum(ing["consumableOnlyIDs"]["duration"] for ing in chosen_ingredients),
            "stats" : {}
            }



def create_population():
    return [create_individual() for _ in range(POP_SIZE)]

def get_stats_from_individual(individual):


# ======================
# FITNESS
# ======================
def fitness_spell_damage(individual):
    #je le fais en deux partie, un première qui répertorie les stats données par chaque coordonnées, puis un autre qui calcule les position modifier et enfin j'additionne le tout 

    return sum(individual)

# ======================
# SÉLECTION (roulette)
# ======================
def selection(population,fitness):
    total_fitness = sum(fitness(ind) for ind in population)
    pick = random.uniform(0, total_fitness)
    current = 0

    for ind in population:
        current += fitness(ind)
        if current > pick:
            return ind

# ======================
# CROSSOVER
# ======================
def crossover(parent1, parent2):
    point = random.randint(1, GENOME_LENGTH - 1)
    child = parent1[:point] + parent2[point:]
    return child

# ======================
# MUTATION
# ======================
def mutation(individual):
    for i in range(len(individual)):
        if random.random() < MUTATION_RATE:
            individual[i] = 1 - individual[i]
    return individual

# ======================
# ALGO PRINCIPAL
# ======================
def genetic_algorithm():
    population = create_population()

    for generation in range(GENERATIONS):
        new_population = []

        for _ in range(POP_SIZE):
            parent1 = selection(population)
            parent2 = selection(population)

            child = crossover(parent1, parent2)
            child = mutation(child)

            new_population.append(child)

        population = new_population

        best = max(population, key=fitness)
        print(f"Génération {generation} | Best fitness: {fitness(best)}")

    return max(population, key=fitness)

# ======================
# EXECUTION
# ======================
if __name__ == "__main__":
    best_solution = genetic_algorithm()
    print("Meilleure solution :", best_solution)