import random
import json
import numpy as np
import pandas as pd

with open("stats.json", "r") as f:
    possible_stats = set(json.load(f))




class Individual:
    def __init__(self,data,recipes_df,item="scroll",chosen_ingredients = None,lvl_max = 120,ingredient_quality_coefficient = 1):
        if chosen_ingredients == None:
            chosen_ingredients = random.choices(data, k=6)

        self.ingredient_quality_coefficient = ingredient_quality_coefficient
        self.recipe = np.array([[chosen_ingredients[0],chosen_ingredients[1]],
                     [chosen_ingredients[2],chosen_ingredients[3]],
                     [chosen_ingredients[4],chosen_ingredients[5]]])
        
        self.item = item
        self.lvl_max = lvl_max
        self.raw_recipe_df = recipes_df
        self.duration = self.calculate_duration()

    def fitness(self,stat,duration_min = 100,min_max_or_mean = "mean"):   
        #dans un premier temps, fitness ne vise qu'un seule stat
        #je pars du principe qu'il n'y a pas d'ingredient qui ont a la fois "left","rigth","above" ou "under" and touching 
        if stat not in possible_stats:
            raise ValueError("La statistique n'existe pas")
        stat_array = np.zeros((3, 2))
        boost_array = np.zeros((7, 4))
        for i in range(3):
            for j in range(2):
                if "identifications" in self.recipe[i][j]:
                    if stat in self.recipe[i][j]["identifications"]:
                        if min_max_or_mean == "mean":
                            stat_array[i][j] = (self.recipe[i][j]["identifications"][stat]["min"] + self.recipe[i][j]["identifications"][stat]["max"])/2
                        elif min_max_or_mean == "min":  
                            stat_array[i][j] = self.recipe[i][j]["identifications"][stat]["min"] 
                        elif min_max_or_mean == "max":       
                            stat_array[i][j] = self.recipe[i][j]["identifications"][stat]["max"]
                        elif min_max_or_mean == "raw": 
                            stat_array[i][j] = self.recipe[i][j]["identifications"][stat]["raw"]   
                        else:
                            raise ValueError("MIN MAX OR MEAN incorrect")       
        #je calcule les boosts sur un grille 7X4 pour plus simplement éviter les out of bound
        for i in range(2,5):
            for j in range(1,3): 
                boost_array[i][j-1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["left"]
                boost_array[i][j+1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["right"]
                boost_array[i-1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["above"]
                boost_array[i-2][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["above"]

                boost_array[i+1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["under"]
                boost_array[i+2][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["under"]
                if self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"] != 0:
                    boost_array[i][j-1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                if self.recipe[i-2][j-1]["ingredientPositionModifiers"]["notTouching"] != 0:   
                    for ki in range(2,5):
                        for kj in range(1,3):
                            if [ki,kj] not in [[i-1,j],[i+1,j],[i,j],[i,j-1],[i,j+1]]:
                                boost_array[ki,kj] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["notTouching"]
        temp_boost_array = boost_array[2:5,1:3]                       
        #cette étape est combinable avec la première 
        for i in range(3):
            for j in range(2):
                stat_array[i][j] = stat_array[i][j] * ((temp_boost_array[i][j]/100) + 1)  
      
        if self.duration <= 0:
            rep = 0             
        elif 0 < self.duration < duration_min:
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

    def give_boost_array(self):
        boost_array = np.zeros((7, 4))
        #je calcule les boosts sur un grille 7X4 pour plus simplement éviter les out of bound
        for i in range(2,5):
            for j in range(1,3): 
                boost_array[i][j-1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["left"]
                boost_array[i][j+1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["right"]
                boost_array[i-1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["above"]
                boost_array[i-2][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["above"]

                boost_array[i+1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["under"]
                boost_array[i+2][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["under"]
                if self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"] != 0:
                    boost_array[i][j-1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                if self.recipe[i-2][j-1]["ingredientPositionModifiers"]["notTouching"] != 0:   
                    #temp_coord = ([k for k in range(5) if k not in [i-1,i,i+1]],[k for k in range(4) if k not in [j-1,j,j+1]])
                    for ki in range(2,5):
                        for kj in range(1,3):
                            if [ki,kj] not in [[i-1,j],[i+1,j],[i,j],[i,j-1],[i,j+1]]:
                            #if (ki not in [i-1,i,i+1]) and (kj not in [j-1,j,j+1]):
                                boost_array[ki,kj] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["notTouching"]

        print(boost_array[2:5,1:3])

    

    def import_recipe_df(self,path):
        dfs = pd.read_excel(path, sheet_name=None)
        if self.item in ["chestplate",
                    "helmet",
                    "leggins",
                    "boots",
                    "ring",
                    "necklace",
                    "bracelet"]:
            df = dfs["armour"]
        elif self.item in ["relik",
                    "wand",
                    "bow",
                    "spear",
                    "dagger"]:
            df = dfs["weapon"]    
        elif self.item in ["food"]:
            df = dfs["cooking"]   
        elif self.item in ["potion"]:
            df = dfs["alchemism"]   
        elif self.item in ["scroll"]:
            df = dfs["scribing"]    
        else:
            raise ValueError("Error Item")   
        return df 

    def calculate_duration(self):    
        #base_dura = self.raw_recipe_df[self.raw_recipe_df["lvl"] == self.lvl_max]["dura_min"]
        base_dura = (self.raw_recipe_df[self.raw_recipe_df["lvl"] == self.lvl_max]["dura_min"].iloc[0]) * self.ingredient_quality_coefficient
        if self.item in ["chestplate",
                    "helmet",
                    "leggins",
                    "boots",
                    "relik",
                    "wand",
                    "spear",
                    "dagger",
                    "bow",
                    "ring",
                    "necklace",
                    "bracelet"]:
            rep = base_dura + (sum(ing["itemOnlyIDs"]["durabilityModifier"] for ing in self.recipe.flat)/1000) 
        elif self.item in ["potion",
                    "scroll",
                    "food"]:
            rep = base_dura + sum(ing["consumableOnlyIDs"]["duration"] for ing in self.recipe.flat)  
        else:
            raise ValueError("error item")      
        return rep

    def recalculate_duration(self):    
        self.duration = self.calculate_duration()

    def show_stats(self):
        stats_dic = {}
        boost_array = np.zeros((7, 4))
        for i in range(2,5):
            for j in range(1,3): 
                boost_array[i][j-1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["left"]
                boost_array[i][j+1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["right"]
                boost_array[i-1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["above"]
                boost_array[i-2][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["above"]

                boost_array[i+1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["under"]
                boost_array[i+2][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["under"]
                if self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"] != 0:
                    boost_array[i][j-1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["touching"]
                if self.recipe[i-2][j-1]["ingredientPositionModifiers"]["notTouching"] != 0:   
                    for ki in range(2,5):
                        for kj in range(1,3):
                            if [ki,kj] not in [[i-1,j],[i+1,j],[i,j],[i,j-1],[i,j+1]]:
                                boost_array[ki,kj] += self.recipe[i-2][j-1]["ingredientPositionModifiers"]["notTouching"]
        temp_boost_array = boost_array[2:5,1:3]   
        for i in range(3):
            for j in range(2):
                temp_ing = self.recipe[i][j]
                if "identifications" in temp_ing.keys():
                    for id in temp_ing["identifications"].keys():
                        if id not in stats_dic.keys():
                            stats_dic[id] = {"min":0,"max":0}
                        stats_dic[id]["min"] = stats_dic[id]["min"] + (np.floor(temp_ing["identifications"][id]["min"] * (1 + (temp_boost_array[i,j]/100))))
                        stats_dic[id]["max"] = stats_dic[id]["max"] + (np.floor(temp_ing["identifications"][id]["max"] * (1 + (temp_boost_array[i,j]/100)))) 
        for id in stats_dic.keys():
            print(f"{id} : {stats_dic[id]["min"]} - {stats_dic[id]["max"]}")            




