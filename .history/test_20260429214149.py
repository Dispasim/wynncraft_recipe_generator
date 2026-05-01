import random
import json
import numpy as np

with open("stats.json", "r") as f:
    possible_stats = set(json.load(f))
chosen_ingredients_test = [{'displayName': 'Ancient Scripture', 'internalName': 'Ancient Scripture', 'type': 'ingredient', 'icon': {'value': {'id': 'minecraft:potion', 'name': 'ingredient.ancientScripture', 'customModelData': {'rangeDispatch': [1704]}}, 'format': 'attribute'}, 'emblem': 'square', 'tier': 'TIER_2', 'requirements': {'level': 118, 'skills': ['scribing']}, 'identifications': {'gatherXpBonus': {'min': 4, 'raw': 4, 'max': 5}, 'combatExperience': {'min': 7, 'raw': 7, 'max': 9}}, 'consumableOnlyIDs': {'duration': -210, 'charges': 0}, 'ingredientPositionModifiers': {'left': 0, 'right': 0, 'above': 0, 'under': 0, 'touching': 0, 'notTouching': 0}, 'itemOnlyIDs': {'durabilityModifier': 0, 'strengthRequirement': 0, 'dexterityRequirement': 0, 'intelligenceRequirement': 0, 'defenceRequirement': 0, 'agilityRequirement': 0}}, {'displayName': 'Decomposing Snapdragon', 'internalName': 'Decomposing Snapdragon', 'type': 'ingredient', 'icon': {'value': {'id': 'minecraft:potion', 'name': 'ingredient.decomposingSnapdragon', 'customModelData': {'rangeDispatch': [1859]}}, 'format': 'attribute'}, 'emblem': 'square', 'tier': 'TIER_2', 'requirements': {'level': 113, 'skills': ['tailoring', 'scribing']}, 'identifications': {'lifeSteal': {'min': 100, 'raw': 100, 'max': 120}, 'earthDamage': {'min': 8, 'raw': 8, 'max': 10}, 'waterDamage': {'min': 8, 'raw': 8, 'max': 10}}, 'consumableOnlyIDs': {'duration': -180, 'charges': 0}, 'ingredientPositionModifiers': {'left': 0, 'right': 0, 'above': 0, 'under': 0, 'touching': 0, 'notTouching': 0}, 'itemOnlyIDs': {'durabilityModifier': -114000, 'strengthRequirement': 16, 'dexterityRequirement': 0, 'intelligenceRequirement': 16, 'defenceRequirement': 0, 'agilityRequirement': 0}}, {'displayName': 'Soulbound Cinders', 'internalName': 'Soulbound Cinders', 'type': 'ingredient', 'icon': {'value': {'id': 'minecraft:potion', 'name': 'ingredient.soulboundCinders', 'customModelData': {'rangeDispatch': [2417]}}, 'format': 'attribute'}, 'emblem': 'square', 'tier': 'TIER_2', 'requirements': {'level': 93, 'skills': ['scribing']}, 'identifications': {'manaSteal': {'min': 4, 'raw': 4, 'max': 4}, 'fireDamage': {'min': 6, 'raw': 6, 'max': 8}, 'rawSpellDamage': {'min': 45, 'raw': 45, 'max': 55}}, 'consumableOnlyIDs': {'duration': -180, 'charges': 0}, 'ingredientPositionModifiers': {'left': 0, 'right': 0, 'above': 0, 'under': 0, 'touching': 0, 'notTouching': 0}, 'itemOnlyIDs': {'durabilityModifier': 0, 'strengthRequirement': 0, 'dexterityRequirement': 0, 'intelligenceRequirement': 0, 'defenceRequirement': 0, 'agilityRequirement': 0}, 'droppedBy': [{'name': 'Draconic Spirit', 'coords': [[1443, 25, -5536, 6], [1482, 31, -5540, 6], [1464, 29, -5552, 6], [1465, 71, -5594, 9], [1478, 73, -5572, 9], [1508, 32, -5578, 19], [1508, 32, -5578, 19]]}, {'name': 'Draconic Aspect', 'coords': [[1443, 25, -5536, 6], [1482, 31, -5540, 6], [1464, 29, -5552, 6], [1465, 71, -5594, 9], [1478, 73, -5572, 9], [1508, 32, -5578, 19], [1508, 32, -5578, 19]]}, {'name': 'Smelted Soul', 'coords': [[1232, 11, -5408, 8], [1223, 16, -5394, 8]]}, {'name': 'Flaming Wisp', 'coords': [[1227, 15, -5399, 10], [1346, 1, -5410, 20]]}, {'name': 'Lava Spitting Limus', 'coords': [1422, 13, -5130, 55]}]}, {'displayName': 'Soul Essence', 'internalName': 'Soul Essence', 'type': 'ingredient', 'icon': {'value': {'id': 'minecraft:potion', 'name': 'ingredient.soulEssence', 'customModelData': {'rangeDispatch': [2421]}}, 'format': 'attribute'}, 'emblem': 'square', 'tier': 'TIER_0', 'requirements': {'level': 103, 'skills': ['scribing']}, 'identifications': {'mainAttackDamage': {'min': 5, 'raw': 5, 'max': 6}, 'rawMainAttackDamage': {'min': 23, 'raw': 23, 'max': 27}}, 'consumableOnlyIDs': {'duration': -97, 'charges': 0}, 'ingredientPositionModifiers': {'left': 0, 'right': 0, 'above': 0, 'under': 0, 'touching': 0, 'notTouching': 0}, 'itemOnlyIDs': {'durabilityModifier': 0, 'strengthRequirement': 0, 'dexterityRequirement': 0, 'intelligenceRequirement': 0, 'defenceRequirement': 0, 'agilityRequirement': 0}, 'droppedBy': [{'name': 'Void Soul Roamer', 'coords': [1196, 135, -1120, 40]}, {'name': 'Crystal of Insanity', 'coords': [1382, 142, -1008, 30]}, {'name': 'Cursed Shrieker', 'coords': [1175, 101, -1053, 6]}, {'name': '�Fool Eater', 'coords': None}]}, {'displayName': 'Hydrofluoric Acid', 'internalName': 'Hydrofluoric Acid', 'type': 'ingredient', 'icon': {'value': {'id': 'minecraft:potion', 'name': 'ingredient.hydrofluoricAcid', 'customModelData': {'rangeDispatch': [2038]}}, 'format': 'attribute'}, 'emblem': 'square', 'tier': 'TIER_2', 'requirements': {'level': 97, 'skills': ['woodworking', 'scribing']}, 'identifications': {'poison': {'min': 3200, 'raw': 3200, 'max': 3400}, 'waterDamage': {'min': 10, 'raw': 10, 'max': 12}}, 'consumableOnlyIDs': {'duration': -190, 'charges': 0}, 'ingredientPositionModifiers': {'left': 0, 'right': 0, 'above': 0, 'under': 0, 'touching': 0, 'notTouching': 0}, 'itemOnlyIDs': {'durabilityModifier': -105000, 'strengthRequirement': 0, 'dexterityRequirement': 0, 'intelligenceRequirement': 20, 'defenceRequirement': 0, 'agilityRequirement': 0}, 'droppedBy': [{'name': 'U-45tabot', 'coords': [[-1737, 75, -2650, 180], [-1496, 75, -2529, 220]]}]}, {'displayName': 'Zhight Herbal Mix', 'internalName': 'Zhight Herbal Mix', 'type': 'ingredient', 'icon': {'value': {'id': 'minecraft:potion', 'name': 'ingredient.zhightHerbalMix', 'customModelData': {'rangeDispatch': [2576]}}, 'format': 'attribute'}, 'emblem': 'square', 'tier': 'TIER_0', 'requirements': {'level': 55, 'skills': ['cooking', 'scribing', 'alchemism']}, 'identifications': {'spellDamage': {'min': -4, 'raw': -4, 'max': -1}, 'mainAttackDamage': {'min': -4, 'raw': -4, 'max': -1}}, 'consumableOnlyIDs': {'duration': 24, 'charges': 0}, 'ingredientPositionModifiers': {'left': 0, 'right': 0, 'above': 0, 'under': 0, 'touching': 0, 'notTouching': 0}, 'itemOnlyIDs': {'durabilityModifier': 0, 'strengthRequirement': 0, 'dexterityRequirement': 0, 'intelligenceRequirement': 0, 'defenceRequirement': 0, 'agilityRequirement': 0}, 'droppedBy': [{'name': 'Ingredient Dummy', 'coords': None}]}]    

class Individual:
    def __init__(self,data,base_duration = 1000,chosen_ingredients = None):
        if chosen_ingredients == None:
            chosen_ingredients = random.choices(data, k=6)
            #print(chosen_ingredients)

        self.duration = base_duration + sum(ing["consumableOnlyIDs"]["duration"] for ing in chosen_ingredients) 

        while self.duration < 0:
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
                test = self.recipe[i][j].keys()
                if "identification" in self.recipe[i][j].keys():
                    if stat in self.recipe[i][j]["identification"]:
                        stat_array[i][j] = (self.recipe[i][j]["identification"]["stats"]["min"] + self.recipe[i][j]["identification"]["stats"]["max"])/2
        print(stat_array) 
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
                    temp_coord = ([k for k in range(1,4) not in [i-1,i,i+1]],[k for k in range(1,3) not in [j-1,j,j+1]])
                    for ki in temp_coord[0]:
                        for kj in temp_coord[1]:
                            boost_array[ki,kj] += self.recipe[i-1][j-1]["ingredientPositionModifiers"]["notTouching"]
        temp_boost_array = boost_array[1:4,1:3]
        #cette étape est combinable avec la première 
        for i in range(3):
            for j in range(2):
                stat_array[i][j] = stat_array[i][j] * ((temp_boost_array[i][j]/100) + 1)
        
        print(boost_array)         
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

import json

with open("resultat_scribing.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ind = Individual(data,chosen_ingredients=chosen_ingredients_test)        

ind.display_recipe()

ind.fitness("rawSpellDamage",0)