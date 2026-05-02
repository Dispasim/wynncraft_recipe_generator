import requests
import json

def look_for_id(ings_wynnbuilder,name):
    for ing in ings_wynnbuilder:
        if ing["name"] == name:
            return ing["id"]
    raise ValueError(f"problem with {name}. COuldn't be found in wynnbuilder ingredients")    

# URL de l'API
url = "https://api.wynncraft.com/v3/item/search?fullResult="

# Données à envoyer dans la requête POST
payload = {
    "type": "ingredient"
}

# Headers (optionnel)
headers = {
    "Content-Type": "application/json"
}

with open("ingreds_clean.json", "r") as f:
    ingreds_wynnbuilder = json.load(f)

try:
    # Envoi de la requête POST
    response = requests.post(url, json=payload, headers=headers)

    # Vérifie que la requête a réussi
    response.raise_for_status()

    # Convertit la réponse en JSON
    data = response.json()

    for i in range(len(data)):
        try:
            data[i]["idWynnbuilder"] = look_for_id(ingreds_wynnbuilder,data[i]["displayName"])
        except:
            print(f"Problem with {data[i]['displayName']}")


    # Sauvegarde dans un fichier
    with open("ingredients.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Données enregistrées dans ingredients.json")

except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la requête : {e}")
except json.JSONDecodeError:
    print("La réponse n'est pas au format JSON")