import random

# ======================
# PARAMÈTRES
# ======================
POP_SIZE = 20
GENOME_LENGTH = 10
GENERATIONS = 50
MUTATION_RATE = 0.1

# ======================
# INITIALISATION
# ======================
def create_individual():
    return [random.randint(0, 1) for _ in range(GENOME_LENGTH)]

def create_population():
    return [create_individual() for _ in range(POP_SIZE)]

# ======================
# FITNESS
# ======================
def fitness(individual):
    # Exemple simple : maximiser le nombre de 1
    return sum(individual)

# ======================
# SÉLECTION (roulette)
# ======================
def selection(population):
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