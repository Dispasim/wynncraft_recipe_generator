import random
import json
import numpy as np
import pandas as pd

def remove_ingredients_not_in_level_range(ingredients, lvl_min, lvl_max):
    return [
        ing for ing in ingredients
        if lvl_min <= ing["requirements"]["level"] <= lvl_max
    ]

def remove_blacklisted_ingredients(ingredients,blacklisted_ingredients):
    return [
        ing for ing in ingredients
        if ing["displayName"] not in blacklisted_ingredients
    ]

def sort_ingredients(ingredients,item):
    if item not in ["chestplate",
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
                    "bracelet",
                    "potion",
                    "scroll",
                    "food"]:
        raise ValueError("item incorrect")
    if item in ["chestplate",
                    "helmet"]:
        return [
            ing for ing in ingredients
            if "armouring" in ing["requirements"]["skills"]
        ]
    elif item in ["leggins",
                    "boots"]:
        return [
            ing for ing in ingredients
            if "tailoring" in ing["requirements"]["skills"]
        ]
    elif item in ["relik",
                    "wand","bow"]:
        return [
            ing for ing in ingredients
            if "woodworking" in ing["requirements"]["skills"]
        ]
    elif item in ["dagger",
                    "spear"]:
        return [
            ing for ing in ingredients
            if "weaponsmithing" in ing["requirements"]["skills"]
        ]
    elif item in ["dagger",
                    "spear"]:
        return [
            ing for ing in ingredients
            if "weaponsmithing" in ing["requirements"]["skills"]
        ]
    elif item in ["ring",
                    "necklace","bracelet"]:
        return [
            ing for ing in ingredients
            if "jeweling" in ing["requirements"]["skills"]
        ]
    elif item in ["potion"]:
        return [
            ing for ing in ingredients
            if "alchemism" in ing["requirements"]["skills"]
        ]
    elif item in ["scroll"]:
        return [
            ing for ing in ingredients
            if "scribing" in ing["requirements"]["skills"]
        ]
    elif item in ["food"]:
        return [
            ing for ing in ingredients
            if "cooking" in ing["requirements"]["skills"]
        ]
    else:
        raise ValueError("item incorrect")

def import_recipe_df(path,item):
        dfs = pd.read_excel(path, sheet_name=None)
        if item in ["chestplate",
                    "helmet",
                    "leggins",
                    "boots",
                    "ring",
                    "necklace",
                    "bracelet"]:
            df = dfs["armour"]
        elif item in ["relik",
                    "wand",
                    "bow",
                    "spear",
                    "dagger"]:
            df = dfs["weapon"]    
        elif item in ["food"]:
            df = dfs["cooking"]   
        elif item in ["potion"]:
            df = dfs["alchemism"]   
        elif item in ["scroll"]:
            df = dfs["scribing"]    
        else:
            raise ValueError("Error Item")   
        return df    

def calculate_ingredient_quality_bonus(item,q_ing1,q_ing2):
    if 0> q_ing1 >3 or 0> q_ing1 >3:
        raise ValueError("Item quality problem")
    if item == "helmet" or item == "boots" or item == "wand" or item == "spear" or item == "potion":
        if q_ing1 == 1 and q_ing2 == 1:
            rep = 1
        elif q_ing1 == 2 and q_ing2 == 1:
            rep = 1.0833
        elif q_ing1 == 3 and q_ing2 == 1:
            rep = 1.1333   
        elif q_ing1 == 1 and q_ing2 == 2:
            rep = 1.1666   
        elif q_ing1 == 2 and q_ing2 == 2:
            rep = 1.25   
        elif q_ing1 == 3 and q_ing2 == 2:
            rep = 1.30    
        elif q_ing1 == 1 and q_ing2 == 3:
            rep = 1.2666
        elif q_ing1 == 2 and q_ing2 == 3:
            rep = 1.35  
        elif q_ing1 == 3 and q_ing2 == 3:
            rep = 1.40    
    elif item == "chestplate" or item == "leggins" or item == "bow" or item == "relik" or item == "dagger" or item == "food":
        if q_ing1 == 1 and q_ing2 == 1:
            rep = 1
        elif q_ing1 == 2 and q_ing2 == 1:
            rep = 1.1666
        elif q_ing1 == 3 and q_ing2 == 1:
            rep = 1.2666  
        elif q_ing1 == 1 and q_ing2 == 2:
            rep = 1.0833  
        elif q_ing1 == 2 and q_ing2 == 2:
            rep = 1.25   
        elif q_ing1 == 3 and q_ing2 == 2:
            rep = 1.35   
        elif q_ing1 == 1 and q_ing2 == 3:
            rep = 1.1333
        elif q_ing1 == 2 and q_ing2 == 3:
            rep = 1.30 
        elif q_ing1 == 3 and q_ing2 == 3:
            rep = 1.40       
    elif item == "scroll":
        if q_ing1 == 1 and q_ing2 == 1:
            rep = 1
        elif (q_ing1 == 2 and q_ing2 == 1) or (q_ing1 == 1 and q_ing2 == 2):
            rep = 1.125
        elif (q_ing1 == 3 and q_ing2 == 1) or (q_ing1 == 1 and q_ing2 == 3):
            rep = 1.2 
        elif q_ing1 == 2 and q_ing2 == 2:
            rep = 1.25   
        elif (q_ing1 == 3 and q_ing2 == 2) or (q_ing1 == 2 and q_ing2 == 3):
            rep = 1.325  
        elif q_ing1 == 3 and q_ing2 == 3:
            rep = 1.40      
    else:
        raise ValueError("Problem with item in ingredient quality function") 
    return rep             


def get_max_per_stat(stats):
    pass