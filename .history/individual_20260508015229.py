import random
import numpy as np
import pandas as pd
from utils import get_recipe_id,wb_bits_to_b64


# Si les hash ne fonctionnent pas, aller vérifier sur https://github.com/wynnbuilder/wynnbuilder.github.io/blob/master/js/craft.js si ce dictionnaire a changé
CRAFTER_ENC = {
    "CRAFTED_ATK_SPD": {
        "SLOW": 0, 
        "NORMAL": 1, 
        "FAST": 2,
        "BITLEN": 4,
    },
    "MAT_TIERS": 3,
    "MAT_TIER_BITLEN": 3,
    "NUM_MATS": 2,
    "NUM_INGS": 6,
    "ING_ID_BITLEN": 12,
    "RECIPE_ID_BITLEN": 12,
    "CRAFTED_VERSION_BITLEN": 7,
    "CRAFTED_ENCODING_VERSION": 2,
}

WB_B64_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+-"
SCALE = 600

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

    def fitness(self,stat,duration_min = 100,min_max_or_mean = "mean",req_stats = [200,200,200,200,200]):   
        #dans un premier temps, fitness ne vise qu'un seule stat
        #je pars du principe qu'il n'y a pas d'ingredient qui ont a la fois "left","rigth","above" ou "under" and touching 
        stat_array = np.zeros((3, 2))
        boost_array = np.zeros((7, 4))
        for i in range(3):
            for j in range(2):
                #if "ids" in self.recipe[i][j]:
                if stat in self.recipe[i][j]["ids"]:
                    if min_max_or_mean == "mean":
                        stat_array[i][j] = (self.recipe[i][j]["ids"][stat]["minimum"] + self.recipe[i][j]["ids"][stat]["maximum"])/2
                    elif min_max_or_mean == "min":  
                        stat_array[i][j] = self.recipe[i][j]["ids"][stat]["minimum"] 
                    elif min_max_or_mean == "max":       
                        stat_array[i][j] = self.recipe[i][j]["ids"][stat]["maximum"]  
                    else:
                        raise ValueError("MIN MAX OR MEAN incorrect")       
        #je calcule les boosts sur un grille 7X4 pour plus simplement éviter les out of bound
        for i in range(2,5):
            for j in range(1,3): 
                boost_array[i][j-1] += self.recipe[i-2][j-1]["posMods"]["left"]
                boost_array[i][j+1] += self.recipe[i-2][j-1]["posMods"]["right"]
                boost_array[i-1][j] += self.recipe[i-2][j-1]["posMods"]["above"]
                boost_array[i-2][j] += self.recipe[i-2][j-1]["posMods"]["above"]

                boost_array[i+1][j] += self.recipe[i-2][j-1]["posMods"]["under"]
                boost_array[i+2][j] += self.recipe[i-2][j-1]["posMods"]["under"]
                if self.recipe[i-2][j-1]["posMods"]["touching"] != 0:
                    boost_array[i][j-1] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-2][j-1]["posMods"]["touching"]
                if self.recipe[i-2][j-1]["posMods"]["notTouching"] != 0:   
                    for ki in range(2,5):
                        for kj in range(1,3):
                            if [ki,kj] not in [[i-1,j],[i+1,j],[i,j],[i,j-1],[i,j+1]]:
                                boost_array[ki,kj] += self.recipe[i-2][j-1]["posMods"]["notTouching"]
        temp_boost_array = boost_array[2:5,1:3]                       
        #cette étape est combinable avec la première 
        if self.item in ["chestplate",
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
            req_list = [0,0,0,0,0]
            for i in range(3):
                for j in range(2):
                    req_list[0] = req_list[0] + (self.recipe[i][j]["itemIDs"]["strReq"]* ((temp_boost_array[i][j]/100) + 1))
                    req_list[1] = req_list[1] + (self.recipe[i][j]["itemIDs"]["dexReq"]* ((temp_boost_array[i][j]/100) + 1))
                    req_list[2] = req_list[2] + (self.recipe[i][j]["itemIDs"]["intReq"]* ((temp_boost_array[i][j]/100) + 1))
                    req_list[3] = req_list[3] + (self.recipe[i][j]["itemIDs"]["defReq"]* ((temp_boost_array[i][j]/100) + 1))
                    req_list[4] = req_list[4] + (self.recipe[i][j]["itemIDs"]["agiReq"]* ((temp_boost_array[i][j]/100) + 1))
        for i in range(3):
            for j in range(2):
                stat_array[i][j] = np.floor(stat_array[i][j] * ((temp_boost_array[i][j]/100) + 1))  
                #stat_array[i][j] = stat_array[i][j] * ((temp_boost_array[i][j]/100) + 1)
                #stat_array[i][j] = np.floor(stat_array[i][j] * ((1 + (temp_boost_array[i,j]/100)) if temp_boost_array[i,j]>0 else (-1 + (temp_boost_array[i,j]/100)))
                #stat_array[i][j] = stat_array[i][j] * ((-1 + (temp_boost_array[i,j]/100)) if temp_boost_array[i,j]<0 else (1 + (temp_boost_array[i,j]/100)))


        
                     
        
        
        """if self.duration < duration_min:
            rep = sum(stat_array.flat)*(2/(1 + np.exp(-(self.duration - duration_min)/SCALE)))"""
        
        """if self.duration <= 0:
            rep = 0             
        elif 0 < self.duration < duration_min:
            rep = sum(stat_array.flat) * (2/(1 + np.exp(-(self.duration - duration_min)/SCALE)))   """
        if self.duration <= 0:
            rep = 0             
        elif 0 < self.duration < duration_min:
            rep = sum(stat_array.flat) * (self.duration/duration_min)
        
        else:
            rep = sum(stat_array.flat)
        if self.item in ["chestplate",
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
            for i in range(len(req_list)):
                if req_list[i] > req_stats[i]:
                    rep = 0    
          
        return rep    
    
    def display_recipe(self):
        print(f"duration : {self.duration}")
        print("===============================\n")
        print(f"|   {self.recipe[0,0]['name']:10}   |    {self.recipe[0,1]['name']:10}  |\n")
        print("===============================\n")
        print(f"|   {self.recipe[1,0]['name']:10}   |    {self.recipe[1,1]['name']:10}  |\n")
        print("===============================\n")
        print(f"|   {self.recipe[2,0]['name']:10}   |    {self.recipe[2,1]['name']:10}  |\n")
        print("===============================\n")

    def give_boost_array(self):
        boost_array = np.zeros((7, 4))
        #je calcule les boosts sur un grille 7X4 pour plus simplement éviter les out of bound
        for i in range(2,5):
            for j in range(1,3): 
                boost_array[i][j-1] += self.recipe[i-2][j-1]["posMods"]["left"]
                boost_array[i][j+1] += self.recipe[i-2][j-1]["posMods"]["right"]
                boost_array[i-1][j] += self.recipe[i-2][j-1]["posMods"]["above"]
                boost_array[i-2][j] += self.recipe[i-2][j-1]["posMods"]["above"]

                boost_array[i+1][j] += self.recipe[i-2][j-1]["posMods"]["under"]
                boost_array[i+2][j] += self.recipe[i-2][j-1]["posMods"]["under"]
                if self.recipe[i-2][j-1]["posMods"]["touching"] != 0:
                    boost_array[i][j-1] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-2][j-1]["posMods"]["touching"]
                if self.recipe[i-2][j-1]["posMods"]["notTouching"] != 0:   
                    #temp_coord = ([k for k in range(5) if k not in [i-1,i,i+1]],[k for k in range(4) if k not in [j-1,j,j+1]])
                    for ki in range(2,5):
                        for kj in range(1,3):
                            if [ki,kj] not in [[i-1,j],[i+1,j],[i,j],[i,j-1],[i,j+1]]:
                            #if (ki not in [i-1,i,i+1]) and (kj not in [j-1,j,j+1]):
                                boost_array[ki,kj] += self.recipe[i-2][j-1]["posMods"]["notTouching"]

        print(boost_array[2:5,1:3])

    def multi_fitness(self, stats, weights=None, duration_min=100, req_stats=[200,200,200,200,200]):
    
        if weights is None:
            weights = {stat: 1 for stat in stats}
        
        total_score = 0
        stat_scores = {}

        # --- Calcul de chaque stat ---
        for stat in stats:
            stat_value = self.fitness(stat, duration_min=duration_min)
            
            # Normalisation douce (log pour éviter explosion)
            stat_value = np.log1p(max(stat_value, 0))
            
            stat_scores[stat] = stat_value

        # --- Combinaison pondérée ---
        for stat in stats:
            total_score += weights[stat] * stat_scores[stat]

        # --- Bonus d'équilibre (TRÈS IMPORTANT) ---
        # pénalise les builds déséquilibrés
        values = np.array(list(stat_scores.values()))
        if len(values) > 1:
            balance_bonus = np.mean(values) / (np.std(values) + 1e-6)
            total_score *= balance_bonus

        # --- Pénalité requirements (déjà dans ton code mais renforcée ici) ---
        if hasattr(self, "req_list"):
            for i in range(len(req_stats)):
                if self.req_list[i] > req_stats[i]:
                    return 0

        return total_score

    def import_recipe_df(self,path):
        dfs = pd.read_excel(path, sheet_name=None)
        if self.item in ["chestplate",
                    "helmet",
                    "leggings",
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
            rep = base_dura + sum(ing["itemIDs"]["dura"] for ing in self.recipe.flat)
        elif self.item in ["potion",
                    "scroll",
                    "food"]:
            rep = base_dura + sum(ing["consumableIDs"]["dura"] for ing in self.recipe.flat)  
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
                boost_array[i][j-1] += self.recipe[i-2][j-1]["posMods"]["left"]
                boost_array[i][j+1] += self.recipe[i-2][j-1]["posMods"]["right"]
                boost_array[i-1][j] += self.recipe[i-2][j-1]["posMods"]["above"]
                boost_array[i-2][j] += self.recipe[i-2][j-1]["posMods"]["above"]

                boost_array[i+1][j] += self.recipe[i-2][j-1]["posMods"]["under"]
                boost_array[i+2][j] += self.recipe[i-2][j-1]["posMods"]["under"]
                if self.recipe[i-2][j-1]["posMods"]["touching"] != 0:
                    boost_array[i][j-1] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i][j+1] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i+1][j] += self.recipe[i-2][j-1]["posMods"]["touching"]
                    boost_array[i-1][j] += self.recipe[i-2][j-1]["posMods"]["touching"]
                if self.recipe[i-2][j-1]["posMods"]["notTouching"] != 0:   
                    for ki in range(2,5):
                        for kj in range(1,3):
                            if [ki,kj] not in [[i-1,j],[i+1,j],[i,j],[i,j-1],[i,j+1]]:
                                boost_array[ki,kj] += self.recipe[i-2][j-1]["posMods"]["notTouching"]
        temp_boost_array = boost_array[2:5,1:3]   
        for i in range(3):
            for j in range(2):
                temp_ing = self.recipe[i][j]

                #if "identifications" in temp_ing.keys():
                for id in temp_ing["ids"].keys():
                    if id not in stats_dic.keys():
                        stats_dic[id] = {"min":0,"max":0}
                    stats_dic[id]["min"] = stats_dic[id]["min"] + (np.floor(temp_ing["ids"][id]["minimum"] * (1 + (temp_boost_array[i,j]/100))))  
                    stats_dic[id]["max"] = stats_dic[id]["max"] + (np.floor(temp_ing["ids"][id]["maximum"] * (1 + (temp_boost_array[i,j]/100))))
                    """if temp_boost_array[i,j]>=0:
                        stats_dic[id]["min"] = stats_dic[id]["min"] + (np.floor(temp_ing["ids"][id]["minimum"] * (1 + (temp_boost_array[i,j]/100))))
                        stats_dic[id]["max"] = stats_dic[id]["max"] + (np.floor(temp_ing["ids"][id]["maximum"] * (1 + (temp_boost_array[i,j]/100)))) 
                    else:   
                        stats_dic[id]["min"] = stats_dic[id]["min"] + (np.floor(temp_ing["ids"][id]["minimum"] * (1 + (temp_boost_array[i,j]/100))))
                        stats_dic[id]["max"] = stats_dic[id]["max"] + (np.floor(temp_ing["ids"][id]["maximum"] * (1 + (temp_boost_array[i,j]/100)))) """
        for id in stats_dic.keys():
            print(f"{id} : {stats_dic[id]['min']} - {stats_dic[id]['max']}")         

    
    def wb_append_bits_little(self,bits, value, length):
        """Même orientation que BitVector.append de WynnBuilder : LSB first."""
        value = int(value)
        for i in range(length):
            bits.append((value >> i) & 1)


    def wb_bits_to_b64(self,bits):
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


    def encode_wynn_craft_hash(self, material_tiers, attack_speed="SLOW", is_weapon=False):
        bits = []
        self.wb_append_bits_little(bits, 0, 1)  # binary / non legacy
        self.wb_append_bits_little(bits, CRAFTER_ENC["CRAFTED_ENCODING_VERSION"], 7)

        # IMPORTANT : l'ordre officiel est exactement Ing 1, Ing 2, Ing 3, Ing 4, Ing 5, Ing 6.
        # Chaque ingrédient prend 12 bits.
        if len(self.recipe.flat) != 6:
            raise ValueError(f"Un hash WynnCrafter doit avoir exactement 6 ingrédients, reçu {len(self.recipe.flat)}")

        for ing in self.recipe.flat:
            self.wb_append_bits_little(bits, int(ing["id"]), CRAFTER_ENC["ING_ID_BITLEN"])

        self.wb_append_bits_little(bits, int(get_recipe_id(self.item,self.lvl_max,self.raw_recipe_df)), CRAFTER_ENC["RECIPE_ID_BITLEN"])
        self.wb_append_bits_little(bits, int(material_tiers[0]) - 1, CRAFTER_ENC["MAT_TIER_BITLEN"])
        self.wb_append_bits_little(bits, int(material_tiers[1]) - 1, CRAFTER_ENC["MAT_TIER_BITLEN"])
        if is_weapon:
            self.wb_append_bits_little(bits, CRAFTER_ENC["CRAFTED_ATK_SPD"]["BITLEN"].get(str(attack_speed).upper(), 0), 4)
        return wb_bits_to_b64(bits)
    
    def become_offspring(self,crossover_ingredients):
        self.recipe = np.array([[crossover_ingredients[0],crossover_ingredients[1]],
                                 [crossover_ingredients[2],crossover_ingredients[3]],
                                 [crossover_ingredients[4],crossover_ingredients[5]]])

        self.recalculate_duration()
        return self


