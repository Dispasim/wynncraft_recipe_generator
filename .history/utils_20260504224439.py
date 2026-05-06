import random
import json
import numpy as np
import pandas as pd

import time
from functools import wraps

WB_B64_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-"

def remove_ingredients_not_in_level_range(ingredients, lvl_min, lvl_max):
    return [
        ing for ing in ingredients
        if lvl_min <= ing["lvl"] <= lvl_max
    ]

def remove_blacklisted_ingredients(ingredients,blacklisted_ingredients):
    return [
        ing for ing in ingredients
        if ing["name"] not in blacklisted_ingredients
    ]

def sort_ingredients(ingredients,item):
    if item not in ["chestplate",
                    "helmet",
                    "leggings",
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
            if "armouring".upper() in ing["skills"]
        ]
    elif item in ["leggings",
                    "boots"]:
        return [
            ing for ing in ingredients
            if "tailoring".upper() in ing["skills"]
        ]
    elif item in ["relik",
                    "wand","bow"]:
        return [
            ing for ing in ingredients
            if "woodworking".upper() in ing["skills"]
        ]
    elif item in ["dagger",
                    "spear"]:
        return [
            ing for ing in ingredients
            if "weaponsmithing".upper() in ing["skills"]
        ]
    elif item in ["dagger",
                    "spear"]:
        return [
            ing for ing in ingredients
            if "weaponsmithing".upper() in ing["skills"]
        ]
    elif item in ["ring",
                    "necklace","bracelet"]:
        return [
            ing for ing in ingredients
            if "jeweling".upper() in ing["skills"]
        ]
    elif item in ["potion"]:
        return [
            ing for ing in ingredients
            if "alchemism".upper() in ing["skills"]
        ]
    elif item in ["scroll"]:
        return [
            ing for ing in ingredients
            if "scribing".upper() in ing["skills"]
        ]
    elif item in ["food"]:
        return [
            ing for ing in ingredients
            if "cooking".upper() in ing["skills"]
        ]
    else:
        raise ValueError("job incorrect")

def import_recipe_df(path,item):
        dfs = pd.read_excel(path, sheet_name=None)
        if item in ["chestplate",
                    "helmet",
                    "leggings",
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
    elif item == "chestplate" or item == "leggings" or item == "bow" or item == "relik" or item == "dagger" or item == "food":
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


def translate_stat(stat):
    with open("ressources/translation.json", "r") as f:
        stat_map = json.load(f)
    if stat in stat_map.keys():
        return stat_map[stat]
    else:
        raise ValueError("Stat incorrect, la bonne syntaxe est dans stranslation.json")

def get_recipe_id(item,lvl,raw_recipe):
    lvl_raw = raw_recipe[raw_recipe["lvl"] == lvl]["lvl_min"].iloc[0]
    with open("ressources/recipes_clean.json", "r") as f:
        recipes = json.load(f)
    for recipe in recipes["recipes"]:
        if recipe["type"] == item.upper() and recipe["lvl"]["minimum"] == lvl_raw:

            return recipe["id"]
    raise ValueError(f"item or lvl not found in recipes_clean for {item.upper()} lvl {lvl} lvl_raw : {lvl_raw}")

def wb_bits_to_b64(bits):
    # padding jusque multiple de 6
    while len(bits) % 6 != 0:
        bits.append(0)
    out = []
    for i in range(0, len(bits), 6):
        value = 0
        for j in range(6):
            value |= bits[i + j] << j
        out.append(WB_B64_DIGITS[value])
    return "".join(out)

def remove_useless_ingredients(ingredients,stat,item):
    if item in ["chestplate",
                    "helmet",
                    "leggings",
                    "boots",
                    "relik",
                    "wand",
                    "spear",
                    "dagger",
                    "bow",
                    "ring",
                    "necklace",
                    "bracelet"]:
        return [
            ing for ing in ingredients
            if (stat in ing["ids"].keys()) or (ing["itemIDs"]["dura"]>0) or (any(x != 0 for x in (ing["posMods"].values()) ))
        ]
    elif item in ["potion",
                    "scroll",
                    "food"]:
        return [
            ing for ing in ingredients
            if (stat in ing["ids"].keys()) or (ing["consumableIDs"]["dura"]>0) or (any(x > 0 for x in (ing["posMods"].values()) ))
        ]
    



def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # plus précis que time.time()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} exécutée en {end - start:.6f} secondes")
        return result
    return wrapper    

def give_ingredients_list(ingredients):
    rep = []
    for ing in ingredients:
        rep.append(ing["name"])
    return rep    

def get_ingredient_from_string(ingredients,ing_str):
    rep = None
    for ing in ingredients:
        if ing["name"] == ing_str:
            rep = ing
            break
    return rep    

def update_best_archive(archive, population, x, fitness_fn):
    """
    archive : liste actuelle des meilleurs individus [(ind, fitness), ...]
    population : population actuelle
    x : nombre de meilleurs à garder
    fitness_fn : fonction pour calculer la fitness
    """
    # Ajouter population à l'archive
    for ind in population:
        archive.append((ind, fitness_fn(ind)))

    # Trier par fitness décroissante
    archive.sort(key=lambda t: t[1], reverse=True)

    # Garder uniquement les x meilleurs
    archive = archive[:x]

    return archive