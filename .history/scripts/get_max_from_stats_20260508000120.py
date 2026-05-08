import json 


with open(f"ressources/stats.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

with open(f"ressources/ingreds_clean.json", "r", encoding="utf-8") as f:
    data = json.load(f)


stats_list = list(stats.values())        

max_stats_dic = {stat : 0 for stat in stats_list}

for ing in data:
    for stat in ing["ids"]:
        if ing["ids"][stat]["maximum"] > max_stats_dic[stat]:
            max_stats_dic[stat] =  stat["maximum"]

with open("ressources/max_stats.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)      