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

def sort_ingredients(ingredients,job):
    if job not in ["armouring",
                "tailoring",
                "woodworking",
                "weaponsmithing",
                "jeweling",
                "alchemism",
                "scribing",
                "cooking"]:
        raise ValueError("Job incorrect")
    return [
        ing for ing in ingredients
        if job in ing["requirements"]["skills"]
    ]