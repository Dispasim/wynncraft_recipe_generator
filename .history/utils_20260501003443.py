import random
import json
import numpy as np

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
    