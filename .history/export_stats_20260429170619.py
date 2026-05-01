import json

with open("resultat.json", "r", encoding="utf-8") as f:
    data = json.load(f)

stats = set()

for ing in data:
    if "identifications" in ing:
        stats.update(ing["identifications"].keys())

with open("stats.json", "w") as f:
    json.dump(list(stats), f)

