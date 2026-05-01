import json

JOB_FILTER = "scribing"

with open("resultat.json", "r", encoding="utf-8") as f:
    data = json.load(f)

rep = []

for ingredient in data:
    if JOB_FILTER in ingredient["requirements"]["skills"]:
        rep.append(ingredient)

with open(f"resultat_{JOB_FILTER}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)        
