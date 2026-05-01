import random
import json
import numpy as np

with open("stats.json", "r") as f:
    possible_stats = set(json.load(f))

def remove_ingredients_not_in_level_range(ingredients, lvl_min, lvl_max):
    return [
        ing for ing in ingredients
        if lvl_min <= ing["requirements"]["level"] <= lvl_max
    ]

class Individual:
    def __init__(self,data,base_duration = 1000,chosen_ingredients = None,lvl_min = 0,lvl_max = 120):
        #data = remove_ingredients_not_in_level_range(data,lvl_min,lvl_max)
        print("check")
        if chosen_ingredients == None:
            chosen_ingredients = random.choices(data, k=6)
            #print(chosen_ingredients)

        self.duration = base_duration + sum(ing["consumableOnlyIDs"]["duration"] for ing in chosen_ingredients) 

        while self.duration < 0:
            print("check1")
            chosen_ingredients = random.choices(data, k=6)


        self.recipe = np.array([[chosen_ingredients[0],chosen_ingredients[1]],
                     [chosen_ingredients[2],chosen_ingredients[3]],
                     [chosen_ingredients[4],chosen_ingredients[5]]])
        

    def fitness(self,stat,duration_min = 100):   
        #dans un premier temps, fitness ne vise qu'un seule stat
        #je pars du principe qu'il n'y a pas d'ingredient qui ont a la fois "left","rigth","above" ou "under" and touching 
        if stat not in possible_stats:
            raise ValueError("La statistique n'existe pas")
        stat_array = np.zeros((3, 2))
        boost_array = np.zeros((5, 4))
        for i in range(3):
            for j in range(2):
                if "identifications" in self.recipe[i][j]:
                    if stat in self.recipe[i][j]["identifications"]:
                        stat_array[i][j] = (self.recipe[i][j]["identifications"][stat]["min"] + self.recipe[i][j]["identifications"][stat]["max"])/2
        for i in range(1,4):
            for j in range(1,3): 
                boost_array[i][j-1] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["left"]
                boost_array[i][j+1] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["right"]
                boost_array[i+1][j] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["above"]
                boost_array[i-1][j] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["under"]
                if self.recipe[i-1][j-1]["ingredientPositionModifiers"]["touching"] > 0:
                    boost_array[i][j-1] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["touching"]
                if self.recipe[i-1][j-1]["ingredientPositionModifiers"]["notTouching"] > 0:   
                    temp_coord = ([k for k in range(1,4) if k not in [i-1,i,i+1]],[k for k in range(1,3) if k not in [j-1,j,j+1]])
                    for ki in temp_coord[0]:
                        for kj in temp_coord[1]:
                            boost_array[ki,kj] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["notTouching"]
        temp_boost_array = boost_array[1:4,1:3]
        #cette étape est combinable avec la première 
        for i in range(3):
            for j in range(2):
                stat_array[i][j] = stat_array[i][j] * ((temp_boost_array[i][j]/100) + 1)       
        if self.duration < duration_min:
            rep = sum(stat_array.flat) * (self.duration/duration_min)    
        else:
            rep = sum(stat_array.flat)
        return rep    
    
    def display_recipe(self):
        print(f"duration : {self.duration}")
        print("===============================\n")
        print(f"|   {self.recipe[0,0]['displayName']:10}   |    {self.recipe[0,1]['displayName']:10}  |\n")
        print("===============================\n")
        print(f"|   {self.recipe[1,0]['displayName']:10}   |    {self.recipe[1,1]['displayName']:10}  |\n")
        print("===============================\n")
        print(f"|   {self.recipe[2,0]['displayName']:10}   |    {self.recipe[2,1]['displayName']:10}  |\n")
        print("===============================\n")

