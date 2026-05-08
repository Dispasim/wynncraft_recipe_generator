import json 


with open(f"ressources/stats.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

with open(f"ressources/ingreds_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)


stats_list = list(stats.values())        
