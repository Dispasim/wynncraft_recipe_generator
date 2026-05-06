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
            if "armouring".upper() in ing["skills"]
        ]
    elif item in ["leggins",
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


class Base64:
    CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    @staticmethod
    def to_int(c):
        return Base64.CHARS.index(c)

    @staticmethod
    def from_int(n):
        return Base64.CHARS[n & 63]


class BitVector:
    def __init__(self, data, length=None):
        bit_vec = []

        if isinstance(data, str):
            int_val = 0
            bv_idx = 0
            length = len(data) * 6

            for i, c in enumerate(data):
                char = Base64.to_int(c)
                pre_pos = bv_idx % 32

                int_val |= (char << bv_idx)
                bv_idx += 6
                post_pos = bv_idx % 32

                if post_pos < pre_pos:
                    bit_vec.append(int_val & 0xFFFFFFFF)
                    int_val = (char >> (6 - post_pos))

                if i == len(data) - 1 and post_pos != 0:
                    bit_vec.append(int_val & 0xFFFFFFFF)

        elif isinstance(data, int):
            if length is None or length < 0:
                raise ValueError("Length must be non-negative")

            if data > 2**32 - 1 or data < -(2**32 - 1):
                raise ValueError("Data must fit in 32 bits")

            bit_vec.append(data & 0xFFFFFFFF)

        else:
            raise TypeError("BitVector must be int or base64 string")

        self.length = length
        self.tail_idx = len(bit_vec) if bit_vec else 1
        self.bits = bit_vec + [0] * (self.tail_idx - len(bit_vec))

    # -------------------------
    # BASIC OPERATIONS
    # -------------------------
    def read_bit(self, idx):
        if idx < 0 or idx >= self.length:
            raise IndexError("Out of range")

        return (self.bits[idx // 32] >> (idx % 32)) & 1

    def set_bit(self, idx):
        if idx < 0 or idx >= self.length:
            raise IndexError("Out of range")

        self.bits[idx // 32] |= (1 << (idx % 32))

    def clear_bit(self, idx):
        if idx < 0 or idx >= self.length:
            raise IndexError("Out of range")

        self.bits[idx // 32] &= ~(1 << (idx % 32))

    # -------------------------
    # SLICE
    # -------------------------
    def slice(self, start, end):
        if end < start:
            raise ValueError("Invalid range")
        if end - start > 32:
            raise ValueError("Max 32 bits")

        res = 0
        for i in range(start, end):
            res |= self.read_bit(i) << (i - start)

        return res

    def slice_b64(self, start, end):
        if end < start or end > self.length:
            raise ValueError("Invalid range")

        out = ""
        for i in range(start, end, 6):
            out += Base64.from_int(self.slice(i, min(i + 6, end)))

        return out

    # -------------------------
    # STRING / EXPORT
    # -------------------------
    def to_b64(self):
        if self.length == 0:
            return ""

        out = ""
        i = 0
        while i < self.length:
            out += Base64.from_int(self.slice(i, i + 6))
            i += 6

        return out

    def __str__(self):
        return "".join(str(self.read_bit(i)) for i in reversed(range(self.length)))

    def to_string_r(self):
        return "".join(str(self.read_bit(i)) for i in range(self.length))

    # -------------------------
    # APPEND
    # -------------------------
    def check_resize(self, length):
        needed = (self.length + length) // 32 + 1
        if needed >= len(self.bits):
            self.bits.extend([0] * len(self.bits))

    def update_tail_int(self, v, v_len):
        pre_pos = self.length % 32

        if self.tail_idx > len(self.bits):
            self.bits.append(0)

        self.bits[self.tail_idx - 1] |= (v << pre_pos) & 0xFFFFFFFF

        post_pos = pre_pos + v_len

        if post_pos >= 32:
            self.bits.append((v >> (32 - pre_pos)) & 0xFFFFFFFF)
            self.tail_idx += 1

        self.length += v_len

    def append(self, data, length):
        if not isinstance(data, int):
            raise TypeError("append expects int")

        if length < 0:
            raise ValueError("length must be positive")

        self.check_resize(length)
        self.update_tail_int(data, length)

    def append_b64(self, data):
        if not isinstance(data, str):
            raise TypeError("append_b64 expects string")

        self.check_resize(len(data) * 6)

        for c in data:
            self.update_tail_int(Base64.to_int(c), 6)

    # -------------------------
    # MERGE
    # -------------------------
    def merge(self, bitvecs):
        for bv in bitvecs:
            remaining = bv.length

            for i in range(bv.tail_idx):
                if i == bv.tail_idx - 1:
                    self.append(bv.bits[i], remaining)
                else:
                    self.append(bv.bits[i], 32)
                    remaining -= 32

class EncodingBitVector(BitVector):
    def __init__(self, data, length=None, bitcode_map=None):
        super().__init__(data, length)
        self.bitcode_map = bitcode_map or {}

    def append_flag(self, field, flag):
        if field not in self.bitcode_map:
            raise KeyError(f"Field '{field}' not found in bitcode_map")

        if flag not in self.bitcode_map[field]:
            raise KeyError(f"Flag '{flag}' not found in field '{field}'")

        value = self.bitcode_map[field][flag]
        bitlen = self.bitcode_map[field]["BITLEN"]

        self.append(value, bitlen)             

def encode_craft(craft, CRAFTER_ENC):
    craft_vec = EncodingBitVector(0, 0, CRAFTER_ENC)

    if craft is None:
        return craft_vec

    # Legacy flag (1 bit à 0)
    craft_vec.append(0, 1)

    # Version
    craft_vec.append(
        CRAFTER_ENC["CRAFTED_ENCODING_VERSION"],
        CRAFTER_ENC["CRAFTED_VERSION_BITLEN"]
    )

    # Ingredients
    for ing in craft["ingreds"]:
        craft_vec.append(
            ing["id"],
            CRAFTER_ENC["ING_ID_BITLEN"]
        )

    # Recipe
    craft_vec.append(
        craft["recipe"]["id"],
        CRAFTER_ENC["RECIPE_ID_BITLEN"]
    )

    # Material tiers
    for mat_tier in craft["mat_tiers"]:
        craft_vec.append(
            mat_tier - 1,
            CRAFTER_ENC["MAT_TIER_BITLEN"]
        )

    # Attack speed (si weapon)
    if craft["statMap"]["category"] == "weapon":
        craft_vec.append(
            CRAFTER_ENC["CRAFTED_ATK_SPD"][craft["atkSpd"]],
            CRAFTER_ENC["CRAFTED_ATK_SPD"]["BITLEN"]
        )

    # Padding pour aligner en Base64 (multiple de 6 bits)
    remainder = craft_vec.length % 6
    if remainder != 0:
        craft_vec.append(0, 6 - remainder)

    return craft_vec               


def translate_stat(stat):
    with open("translation.json", "r") as f:
        stat_map = json.load(f)
    if stat in stat_map.keys():
        return stat_map[stat]
    else:
        raise ValueError("Stat incorrect, la bonne syntaxe est dans stranslation.json")

