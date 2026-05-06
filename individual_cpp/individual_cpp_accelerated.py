
import ctypes
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from utils import get_recipe_id, wb_bits_to_b64

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

CPP_SOURCE_NAME = "individual_cpp_backend.cpp"
DLL_BASENAME = "individual_cpp_backend"
APPLY_POSITION_MODS_TO_TARGET_STAT = False


def _platform_lib_name():
    if os.name == "nt":
        return DLL_BASENAME + ".dll"
    if sys.platform == "darwin":
        return "lib" + DLL_BASENAME + ".dylib"
    return "lib" + DLL_BASENAME + ".so"


def _build_backend_here(base_dir: Path):
    src = base_dir / CPP_SOURCE_NAME
    if not src.exists():
        raise FileNotFoundError(f"Source C++ introuvable: {src}")

    out = base_dir / _platform_lib_name()

    if os.name == "nt":
        # 1) g++ MinGW si dispo
        gpp = shutil.which("g++")
        if gpp:
            cmd = [
                gpp, "-O3", "-std=c++17", "-shared",
                "-static-libgcc", "-static-libstdc++",
                str(src), "-o", str(out),
            ]
            subprocess.check_call(cmd)
            return out
        # 2) cl si dispo
        cl = shutil.which("cl")
        if cl:
            cmd = [
                cl, "/O2", "/EHsc", "/LD", str(src), f"/Fe:{out}"
            ]
            subprocess.check_call(cmd, cwd=str(base_dir), shell=True)
            return out
        raise RuntimeError("Aucun compilateur C++ trouve (g++ ou cl)")

    cmd = ["g++", "-O3", "-std=c++17", "-shared", "-fPIC", str(src), "-o", str(out)]
    subprocess.check_call(cmd)
    return out


def build_cpp_backend(base_dir=None):
    import shutil

    if base_dir is None:
        base_dir = Path(__file__).resolve().parent
    else:
        base_dir = Path(base_dir)
    return _build_backend_here(base_dir)


class _Backend:
    def __init__(self):
        self.lib = None
        self._load()

    def _load(self):
        base_dir = Path(__file__).resolve().parent
        lib_path = base_dir / _platform_lib_name()
        if not lib_path.exists():
            try:
                build_cpp_backend(base_dir)
            except Exception:
                self.lib = None
                return

        self.lib = ctypes.CDLL(str(lib_path))
        dbl_p = ctypes.POINTER(ctypes.c_double)

        self.lib.compute_slot_boosts.argtypes = [dbl_p, dbl_p]
        self.lib.compute_slot_boosts.restype = None

        self.lib.calculate_duration_cpp.argtypes = [ctypes.c_double, dbl_p, ctypes.c_int]
        self.lib.calculate_duration_cpp.restype = ctypes.c_double

        self.lib.fitness_cpp.argtypes = [
            dbl_p, dbl_p, dbl_p,
            ctypes.c_double, ctypes.c_double,
            dbl_p,
            ctypes.c_int, ctypes.c_int,
        ]
        self.lib.fitness_cpp.restype = ctypes.c_double

    @property
    def available(self):
        return self.lib is not None


_BACKEND = _Backend()


class Individual:
    def __init__(self, data, recipes_df, item="scroll", chosen_ingredients=None, lvl_max=120, ingredient_quality_coefficient=1):
        if chosen_ingredients is None:
            chosen_ingredients = random.choices(data, k=6)

        self.ingredient_quality_coefficient = ingredient_quality_coefficient
        self.recipe = np.array([
            [chosen_ingredients[0], chosen_ingredients[1]],
            [chosen_ingredients[2], chosen_ingredients[3]],
            [chosen_ingredients[4], chosen_ingredients[5]],
        ], dtype=object)

        self.item = item
        self.lvl_max = lvl_max
        self.raw_recipe_df = recipes_df

        self._recipe_df_cache = None
        self._base_dura_cache = None
        self._duration_values = None
        self._slot_boosts = None
        self._req_values = None
        self._posmods_values = None
        self._stat_cache = {}

        self.refresh_cache()

    def refresh_cache(self):
        self._stat_cache = {}
        self._recipe_flat = list(self.recipe.flat)
        self._recipe_df_cache = self.raw_recipe_df[self.raw_recipe_df["lvl"] == self.lvl_max]
        if self._recipe_df_cache.empty:
            raise ValueError(f"Aucune ligne raw_recipe_df pour lvl={self.lvl_max}")
        self._base_dura_cache = float(self._recipe_df_cache["dura_min"].iloc[0]) * float(self.ingredient_quality_coefficient)

        if self.item in EQUIPMENT_ITEMS:
            dura_key = ("itemIDs", "dura")
        elif self.item in CONSUMABLE_ITEMS:
            dura_key = ("consumableIDs", "dura")
        else:
            raise ValueError("error item")

        self._duration_values = np.ascontiguousarray(
            [float(ing[dura_key[0]][dura_key[1]]) for ing in self._recipe_flat],
            dtype=np.float64,
        )

        self._req_values = np.ascontiguousarray(
            [
                [
                    float(ing.get("itemIDs", {}).get("strReq", 0.0)),
                    float(ing.get("itemIDs", {}).get("dexReq", 0.0)),
                    float(ing.get("itemIDs", {}).get("intReq", 0.0)),
                    float(ing.get("itemIDs", {}).get("defReq", 0.0)),
                    float(ing.get("itemIDs", {}).get("agiReq", 0.0)),
                ]
                for ing in self._recipe_flat
            ],
            dtype=np.float64,
        )

        self._posmods_values = np.ascontiguousarray(
            [
                [
                    float(ing.get("posMods", {}).get("left", 0.0)),
                    float(ing.get("posMods", {}).get("right", 0.0)),
                    float(ing.get("posMods", {}).get("above", 0.0)),
                    float(ing.get("posMods", {}).get("under", 0.0)),
                    float(ing.get("posMods", {}).get("touching", 0.0)),
                    float(ing.get("posMods", {}).get("notTouching", 0.0)),
                ]
                for ing in self._recipe_flat
            ],
            dtype=np.float64,
        )

        self._slot_boosts = self._compute_slot_boosts()
        self.duration = self.calculate_duration()

    def _compute_slot_boosts(self):
        if _BACKEND.available:
            out = np.zeros(6, dtype=np.float64)
            _BACKEND.lib.compute_slot_boosts(
                self._posmods_values.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                out.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            )
            return out

        # Fallback Python exact
        boost_array = np.zeros((7, 4), dtype=np.float64)
        for i in range(2, 5):
            for j in range(1, 3):
                pm = self.recipe[i - 2][j - 1]["posMods"]
                boost_array[i][j - 1] += pm["left"]
                boost_array[i][j + 1] += pm["right"]
                boost_array[i - 1][j] += pm["above"]
                boost_array[i - 2][j] += pm["above"]
                boost_array[i + 1][j] += pm["under"]
                boost_array[i + 2][j] += pm["under"]
                if pm["touching"] != 0:
                    boost_array[i][j - 1] += pm["touching"]
                    boost_array[i][j + 1] += pm["touching"]
                    boost_array[i + 1][j] += pm["touching"]
                    boost_array[i - 1][j] += pm["touching"]
                if pm["notTouching"] != 0:
                    for ki in range(2, 5):
                        for kj in range(1, 3):
                            if [ki, kj] not in [[i - 1, j], [i + 1, j], [i, j], [i, j - 1], [i, j + 1]]:
                                boost_array[ki, kj] += pm["notTouching"]
        return np.ascontiguousarray(boost_array[2:5, 1:3].reshape(-1), dtype=np.float64)

    def _stat_vector(self, stat, min_max_or_mean):
        cache_key = (stat, min_max_or_mean)
        if cache_key in self._stat_cache:
            return self._stat_cache[cache_key]

        values = []
        for ing in self._recipe_flat:
            ids = ing.get("ids", {})
            if stat not in ids:
                values.append(0.0)
                continue
            info = ids[stat]
            if min_max_or_mean == "mean":
                value = (float(info["minimum"]) + float(info["maximum"])) / 2.0
            elif min_max_or_mean == "min":
                value = float(info["minimum"])
            elif min_max_or_mean == "max":
                value = float(info["maximum"])
            else:
                raise ValueError("MIN MAX OR MEAN incorrect")
            values.append(value)

        arr = np.ascontiguousarray(values, dtype=np.float64)
        self._stat_cache[cache_key] = arr
        return arr

    def fitness(self, stat, duration_min=100, min_max_or_mean="mean", req_stats=[200, 200, 200, 200, 200]):
        stat_values = self._stat_vector(stat, min_max_or_mean)
        req_stats_arr = np.ascontiguousarray(req_stats, dtype=np.float64)
        if _BACKEND.available:
            return float(_BACKEND.lib.fitness_cpp(
                stat_values.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                self._slot_boosts.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                self._req_values.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                float(self.duration),
                float(duration_min),
                req_stats_arr.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                int(self.item in EQUIPMENT_ITEMS),
                int(APPLY_POSITION_MODS_TO_TARGET_STAT),
            ))

        stat_sum = float(stat_values.sum())
        if APPLY_POSITION_MODS_TO_TARGET_STAT:
            stat_sum = float(np.floor(stat_values * (1.0 + self._slot_boosts / 100.0)).sum())

        if self.duration <= 0:
            rep = 0.0
        elif 0 < self.duration < duration_min:
            rep = stat_sum * (self.duration / duration_min)
        else:
            rep = stat_sum

        if self.item in EQUIPMENT_ITEMS:
            req_list = (self._req_values * (1.0 + self._slot_boosts.reshape(6, 1) / 100.0)).sum(axis=0)
            if np.any(req_list > req_stats_arr):
                rep = 0.0
        return float(rep)

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
        print(self._slot_boosts.reshape(3, 2))

    def import_recipe_df(self, path):
        dfs = pd.read_excel(path, sheet_name=None)
        if self.item in ["chestplate", "helmet", "leggings", "boots", "ring", "necklace", "bracelet"]:
            return dfs["armour"]
        if self.item in ["relik", "wand", "bow", "spear", "dagger"]:
            return dfs["weapon"]
        if self.item in ["food"]:
            return dfs["cooking"]
        if self.item in ["potion"]:
            return dfs["alchemism"]
        if self.item in ["scroll"]:
            return dfs["scribing"]
        raise ValueError("Error Item")

    def calculate_duration(self):
        if _BACKEND.available:
            return float(_BACKEND.lib.calculate_duration_cpp(
                float(self._base_dura_cache),
                self._duration_values.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                int(self._duration_values.shape[0]),
            ))
        return float(self._base_dura_cache + self._duration_values.sum())

    def recalculate_duration(self):
        self.duration = self.calculate_duration()

    def show_stats(self):
        stats_dic = {}
        slot_boosts = self._slot_boosts.reshape(3, 2)
        for i in range(3):
            for j in range(2):
                temp_ing = self.recipe[i][j]
                for stat_id, info in temp_ing.get("ids", {}).items():
                    if stat_id not in stats_dic:
                        stats_dic[stat_id] = {"min": 0.0, "max": 0.0}
                    mult = 1.0 + slot_boosts[i, j] / 100.0
                    stats_dic[stat_id]["min"] += np.floor(float(info["minimum"]) * mult)
                    stats_dic[stat_id]["max"] += np.floor(float(info["maximum"]) * mult)
        for stat_id, bounds in stats_dic.items():
            print(f"{stat_id} : {bounds['min']} - {bounds['max']}")

    def wb_append_bits_little(self, bits, value, length):
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
        self.wb_append_bits_little(bits, 0, 1)
        self.wb_append_bits_little(bits, CRAFTER_ENC["CRAFTED_ENCODING_VERSION"], 7)

        if len(self.recipe.flat) != 6:
            raise ValueError(f"Un hash WynnCrafter doit avoir exactement 6 ingrédients, reçu {len(self.recipe.flat)}")

        for ing in self.recipe.flat:
            self.wb_append_bits_little(bits, int(ing["id"]), CRAFTER_ENC["ING_ID_BITLEN"])

        self.wb_append_bits_little(bits, int(get_recipe_id(self.item, self.lvl_max, self.raw_recipe_df)), CRAFTER_ENC["RECIPE_ID_BITLEN"])
        self.wb_append_bits_little(bits, int(material_tiers[0]) - 1, CRAFTER_ENC["MAT_TIER_BITLEN"])
        self.wb_append_bits_little(bits, int(material_tiers[1]) - 1, CRAFTER_ENC["MAT_TIER_BITLEN"])
        if is_weapon:
            self.wb_append_bits_little(bits, CRAFTER_ENC["CRAFTED_ATK_SPD"].get(str(attack_speed).upper(), 0), 4)
        return wb_bits_to_b64(bits)
