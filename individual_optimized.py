import random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from utils import get_recipe_id, wb_bits_to_b64


# Si les hash ne fonctionnent pas, aller vérifier sur
# https://github.com/wynnbuilder/wynnbuilder.github.io/blob/master/js/craft.js
# si ce dictionnaire a changé.
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

EQUIPMENT_ITEMS = {
    "chestplate", "helmet", "leggings", "boots",
    "relik", "wand", "spear", "dagger", "bow",
    "ring", "necklace", "bracelet",
}
CONSUMABLE_ITEMS = {"potion", "scroll", "food"}
REQ_KEYS = ("strReq", "dexReq", "intReq", "defReq", "agiReq")
POS_KEYS = ("left", "right", "above", "under", "touching", "notTouching")
MODE_TO_INDEX = {"min": 0, "mean": 1, "max": 2}

# Pour rester 100% compatible avec le comportement actuel du fichier d'origine,
# fitness() n'applique PAS les posMods à la stat recherchée.
# Si tu veux basculer sur le calcul gameplay pur, passe ce flag à True.
APPLY_POSITION_MODS_TO_TARGET_STAT = False

# Mapping des 6 slots sur une grille 3x2.
SLOT_COORDS = ((0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1))


def _safe_number(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _build_position_targets() -> Dict[int, Dict[str, Tuple[int, ...]]]:
    targets: Dict[int, Dict[str, Tuple[int, ...]]] = {}
    all_slots = range(6)
    for slot, (row, col) in enumerate(SLOT_COORDS):
        left = []
        right = []
        above = []
        under = []
        touching = []
        not_touching = []
        for other, (orow, ocol) in enumerate(SLOT_COORDS):
            if other == slot:
                continue
            if orow == row and ocol == col - 1:
                left.append(other)
            if orow == row and ocol == col + 1:
                right.append(other)
            if ocol == col and orow < row:
                above.append(other)
            if ocol == col and orow > row:
                under.append(other)
            if abs(orow - row) + abs(ocol - col) == 1:
                touching.append(other)
        touching_set = set(touching)
        direct_set = touching_set | {slot}
        for other in all_slots:
            if other not in direct_set:
                not_touching.append(other)
        targets[slot] = {
            "left": tuple(left),
            "right": tuple(right),
            "above": tuple(above),
            "under": tuple(under),
            "touching": tuple(touching),
            "notTouching": tuple(not_touching),
        }
    return targets


POSITION_TARGETS = _build_position_targets()


class Individual:
    """
    Version optimisée de la classe d'origine.

    Gains principaux :
      - boost_array calculé une seule fois par recette
      - req_list calculé une seule fois par recette
      - base_dura récupéré une seule fois au lieu de filtrer le DataFrame à chaque appel
      - cache des stats par (stat, min/max/mean)
      - moins d'allocations NumPy dans fitness() et calculate_duration()

    Important : si tu modifies self.recipe à la main, appelle refresh_cache().
    """

    def __init__(
        self,
        data,
        recipes_df,
        item="scroll",
        chosen_ingredients=None,
        lvl_max=120,
        ingredient_quality_coefficient=1,
    ):
        if chosen_ingredients is None:
            chosen_ingredients = random.choices(data, k=6)
        if len(chosen_ingredients) != 6:
            raise ValueError("chosen_ingredients doit contenir exactement 6 ingrédients")

        self.ingredient_quality_coefficient = ingredient_quality_coefficient
        self.recipe = np.array(
            [
                [chosen_ingredients[0], chosen_ingredients[1]],
                [chosen_ingredients[2], chosen_ingredients[3]],
                [chosen_ingredients[4], chosen_ingredients[5]],
            ],
            dtype=object,
        )
        self.item = item
        self.lvl_max = lvl_max
        self.raw_recipe_df = recipes_df

        self._flat_recipe: Tuple[dict, ...] = tuple()
        self._ids_list: List[dict] = []
        self._posmods_list: List[dict] = []
        self._item_ids_list: List[dict] = []
        self._consumable_ids_list: List[dict] = []
        self._boost_pct_flat = np.zeros(6, dtype=np.float64)
        self._boost_multiplier_flat = np.ones(6, dtype=np.float64)
        self._boost_pct_grid = np.zeros((3, 2), dtype=np.float64)
        self._req_list = np.zeros(5, dtype=np.float64)
        self._duration_delta_equipment = 0.0
        self._duration_delta_consumable = 0.0
        self._base_duration = 0.0
        self._stat_total_cache: Dict[Tuple[str, str], float] = {}
        self._stat_slot_cache: Dict[Tuple[str, str], np.ndarray] = {}

        self.refresh_cache()

    # ------------------------------------------------------------------
    # Cache / compilation
    # ------------------------------------------------------------------
    def refresh_cache(self):
        self._flat_recipe = tuple(self.recipe.flat)
        self._ids_list = [ing.get("ids", {}) for ing in self._flat_recipe]
        self._posmods_list = [ing.get("posMods", {}) for ing in self._flat_recipe]
        self._item_ids_list = [ing.get("itemIDs", {}) for ing in self._flat_recipe]
        self._consumable_ids_list = [ing.get("consumableIDs", {}) for ing in self._flat_recipe]

        self._base_duration = self._lookup_base_duration() * float(self.ingredient_quality_coefficient)
        self._duration_delta_equipment = sum(_safe_number(item_ids.get("dura", 0.0)) for item_ids in self._item_ids_list)
        self._duration_delta_consumable = sum(_safe_number(cons_ids.get("dura", 0.0)) for cons_ids in self._consumable_ids_list)

        self._build_boost_cache()
        self._build_requirement_cache()
        self._stat_total_cache.clear()
        self._stat_slot_cache.clear()
        self.duration = self.calculate_duration()

    def _lookup_base_duration(self) -> float:
        series = self.raw_recipe_df.loc[self.raw_recipe_df["lvl"] == self.lvl_max, "dura_min"]
        if series.empty:
            raise ValueError(f"Aucune ligne trouvée pour lvl={self.lvl_max} dans recipes_df")
        return _safe_number(series.iloc[0])

    def _build_boost_cache(self):
        boost_pct = np.zeros(6, dtype=np.float64)
        for src_slot, posmods in enumerate(self._posmods_list):
            for relation in POS_KEYS:
                value = _safe_number(posmods.get(relation, 0.0))
                if value == 0.0:
                    continue
                for tgt_slot in POSITION_TARGETS[src_slot][relation]:
                    boost_pct[tgt_slot] += value
        self._boost_pct_flat = boost_pct
        self._boost_multiplier_flat = 1.0 + (boost_pct / 100.0)
        self._boost_pct_grid = boost_pct.reshape((3, 2)).copy()

    def _build_requirement_cache(self):
        req = np.zeros(5, dtype=np.float64)
        if self.item not in EQUIPMENT_ITEMS:
            self._req_list = req
            return
        for idx, item_ids in enumerate(self._item_ids_list):
            mult = self._boost_multiplier_flat[idx]
            req[0] += _safe_number(item_ids.get("strReq", 0.0)) * mult
            req[1] += _safe_number(item_ids.get("dexReq", 0.0)) * mult
            req[2] += _safe_number(item_ids.get("intReq", 0.0)) * mult
            req[3] += _safe_number(item_ids.get("defReq", 0.0)) * mult
            req[4] += _safe_number(item_ids.get("agiReq", 0.0)) * mult
        self._req_list = req

    def _stat_slot_values(self, stat: str, min_max_or_mean: str) -> np.ndarray:
        key = (stat, min_max_or_mean)
        cached = self._stat_slot_cache.get(key)
        if cached is not None:
            return cached

        if min_max_or_mean not in MODE_TO_INDEX:
            raise ValueError("MIN MAX OR MEAN incorrect")

        values = np.zeros(6, dtype=np.float64)
        mode_index = MODE_TO_INDEX[min_max_or_mean]
        for idx, ids in enumerate(self._ids_list):
            entry = ids.get(stat)
            if not entry:
                continue
            minimum = _safe_number(entry.get("minimum", 0.0))
            maximum = _safe_number(entry.get("maximum", minimum))
            if mode_index == 0:
                values[idx] = minimum
            elif mode_index == 1:
                values[idx] = (minimum + maximum) / 2.0
            else:
                values[idx] = maximum

        self._stat_slot_cache[key] = values
        return values

    def _stat_total(self, stat: str, min_max_or_mean: str) -> float:
        key = (stat, min_max_or_mean)
        cached = self._stat_total_cache.get(key)
        if cached is not None:
            return cached

        values = self._stat_slot_values(stat, min_max_or_mean)
        if APPLY_POSITION_MODS_TO_TARGET_STAT:
            total = float(np.floor(values * self._boost_multiplier_flat).sum())
        else:
            total = float(values.sum())
        self._stat_total_cache[key] = total
        return total

    # ------------------------------------------------------------------
    # Hot paths
    # ------------------------------------------------------------------
    def fitness(self, stat, duration_min=100, min_max_or_mean="mean", req_stats=None):
        if req_stats is None:
            req_stats = (200, 200, 200, 200, 200)

        stat_total = self._stat_total(stat, min_max_or_mean)
        duration = self.duration

        if duration <= 0:
            rep = 0.0
        elif duration < duration_min:
            rep = stat_total * (duration / duration_min)
        else:
            rep = stat_total

        if rep <= 0.0:
            return 0.0

        if self.item in EQUIPMENT_ITEMS:
            for current_req, allowed_req in zip(self._req_list, req_stats):
                if current_req > allowed_req:
                    return 0.0
        return rep

    def calculate_duration(self):
        base_dura = self._base_duration
        if self.item in EQUIPMENT_ITEMS:
            return base_dura + self._duration_delta_equipment
        if self.item in CONSUMABLE_ITEMS:
            return base_dura + self._duration_delta_consumable
        raise ValueError("error item")

    def recalculate_duration(self):
        # Si la recette a changé, on reconstruit les caches.
        self.refresh_cache()
        return self.duration

    # ------------------------------------------------------------------
    # Debug / display helpers
    # ------------------------------------------------------------------
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
        print(self._boost_pct_grid)

    def import_recipe_df(self, path):
        dfs = pd.read_excel(path, sheet_name=None)
        if self.item in {"chestplate", "helmet", "leggings", "boots", "ring", "necklace", "bracelet"}:
            return dfs["armour"]
        if self.item in {"relik", "wand", "bow", "spear", "dagger"}:
            return dfs["weapon"]
        if self.item == "food":
            return dfs["cooking"]
        if self.item == "potion":
            return dfs["alchemism"]
        if self.item == "scroll":
            return dfs["scribing"]
        raise ValueError("Error Item")

    def show_stats(self):
        stats_dic = {}
        multipliers = self._boost_multiplier_flat
        for idx, temp_ing in enumerate(self._flat_recipe):
            ids = temp_ing.get("ids", {})
            for stat_name, stat_range in ids.items():
                entry = stats_dic.setdefault(stat_name, {"min": 0.0, "max": 0.0})
                minimum = _safe_number(stat_range.get("minimum", 0.0))
                maximum = _safe_number(stat_range.get("maximum", minimum))
                entry["min"] += np.floor(minimum * multipliers[idx])
                entry["max"] += np.floor(maximum * multipliers[idx])
        for stat_name, values in stats_dic.items():
            print(f"{stat_name} : {int(values['min'])} - {int(values['max'])}")

    # ------------------------------------------------------------------
    # Hash helpers
    # ------------------------------------------------------------------
    def wb_append_bits_little(self, bits, value, length):
        """Même orientation que BitVector.append de WynnBuilder : LSB first."""
        value = int(value)
        for i in range(length):
            bits.append((value >> i) & 1)

    def wb_bits_to_b64(self, bits):
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

        flat_recipe = tuple(self.recipe.flat)
        if len(flat_recipe) != 6:
            raise ValueError(f"Un hash WynnCrafter doit avoir exactement 6 ingrédients, reçu {len(flat_recipe)}")

        for ing in flat_recipe:
            self.wb_append_bits_little(bits, int(ing["id"]), CRAFTER_ENC["ING_ID_BITLEN"])

        self.wb_append_bits_little(bits, int(get_recipe_id(self.item, self.lvl_max, self.raw_recipe_df)), CRAFTER_ENC["RECIPE_ID_BITLEN"])
        self.wb_append_bits_little(bits, int(material_tiers[0]) - 1, CRAFTER_ENC["MAT_TIER_BITLEN"])
        self.wb_append_bits_little(bits, int(material_tiers[1]) - 1, CRAFTER_ENC["MAT_TIER_BITLEN"])
        if is_weapon:
            atk_code = CRAFTER_ENC["CRAFTED_ATK_SPD"].get(str(attack_speed).upper(), 0)
            self.wb_append_bits_little(bits, atk_code, CRAFTER_ENC["CRAFTED_ATK_SPD"]["BITLEN"])
        return wb_bits_to_b64(bits)
