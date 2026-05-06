import random
from individual import Individual
#from individual_optimized import Individual
#from individual_cpp_accelerated import Individual
import math


# ======================
# INITIALISATION
# ======================

def create_population(data,item,lvl_max,recipe_df,ingredient_quality_coefficient,pop_size):
    return [Individual(data=data,item=item,lvl_max=lvl_max,recipes_df=recipe_df,ingredient_quality_coefficient=ingredient_quality_coefficient) for _ in range(pop_size)]

# ======================
# SÉLECTION
# ======================
def roulette_selection(population, n_select, focused_stat,duration_min,min_max_or_mean,req_stats):
    fitnesses = [
        ind.fitness(focused_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = req_stats)
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
        
def sus_selection(population, n_select, translated_stat,duration_min,min_max_or_mean,req_stats):
    total_fitness = sum(ind.fitness(translated_stat,duration_min = duration_min, min_max_or_mean = min_max_or_mean, req_stats = req_stats) for ind in population)
    step = total_fitness / n_select
    start = random.uniform(0, step)
    
    points = [start + i * step for i in range(n_select)]
    
    selected = []
    current = 0
    i = 0
    
    for ind in population:
        current += ind.fitness(translated_stat,duration_min = duration_min, min_max_or_mean = min_max_or_mean, req_stats = req_stats)
        while i < len(points) and current >= points[i]:
            selected.append(ind)
            i += 1
    
    return selected  

def tournament_selection(population, n_select,translated_stat,duration_min,min_max_or_mean,req_stats, tournament_selection_rounds = 3):
    selected = []
    
    for _ in range(n_select):
        tournament = random.sample(population, tournament_selection_rounds)
        winner = max(
            tournament,
            key=lambda ind: ind.fitness(translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = req_stats)
        )
        selected.append(winner)
    
    return selected 

def rank_selection(population, n_select, translated_stat, duration_min, min_max_or_mean,req_stats):
    sorted_pop = sorted(
        population,
        key=lambda ind: ind.fitness(translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = req_stats)
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
def elitism_selection(population, n_elite, translated_stat, duration_min, min_max_or_mean, req_stats):
    return sorted(
        population,
        key=lambda ind: ind.fitness(translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = req_stats),
        reverse=True
    )[:n_elite]


def boltzmann_selection(population, n_select, translated_stat, duration_min, min_max_or_mean, req_stats, boltzmann_selection_temperature = 1):
    fitnesses = [
        ind.fitness(translated_stat, duration_min=duration_min, min_max_or_mean=min_max_or_mean, req_stats = req_stats)
        for ind in population
    ]
    
    exp_values = [math.exp(f / boltzmann_selection_temperature) for f in fitnesses]
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

def select_with_elite(population, translated_stat, duration_min, min_max_or_mean, req_stats, method="tournament", n_select=80, elite_ratio = 0.1, **kwargs):
    n_elite = int(n_select*elite_ratio)
    elite = elitism_selection(population, n_elite, translated_stat, duration_min, min_max_or_mean, req_stats)
    
    rest = SELECTION_METHODS[method](
        population,
        n_select - n_elite,
        **kwargs
    )
    
    return elite + rest

def select(population, translated_stat, duration_min, min_max_or_mean, req_stats, method="sus", n_select=80, **kwargs):
    if method not in SELECTION_METHODS:
        raise ValueError(f"Unknown selection method: {method}")
    
    return SELECTION_METHODS[method](population, n_select,translated_stat, duration_min, min_max_or_mean, req_stats, **kwargs)

# ======================
# CROSSOVER
# ======================
def crossover(parent1, parent2,data,item, lvl_max, raw_recipe, ingredient_quality_coefficient):
    crossover_ingredients = [parent1.recipe.flat[i] for i in [0,2,4]] + [parent2.recipe.flat[i] for i in [1,3,5]]
    child = Individual(data,chosen_ingredients=crossover_ingredients,item=item,lvl_max=lvl_max,recipes_df=raw_recipe,ingredient_quality_coefficient=ingredient_quality_coefficient)
    return child

# ======================
# MUTATION
# ======================

#Pour la mutation, je remplace un ingredient par un autre aléatoire
def mutation(ind, data, mutation_rate):
    if random.random() < mutation_rate:
        ind.recipe[random.randint(0, 2),random.randint(0, 1)] = random.choice(data)
        ind.recalculate_duration()
    return ind