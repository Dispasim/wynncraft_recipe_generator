import requests
import json

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

try:
    # Envoi de la requête POST
    response = requests.post(url, json=payload, headers=headers)

    # Vérifie que la requête a réussi
    response.raise_for_status()

    # Convertit la réponse en JSON
    data = response.json()

    # Sauvegarde dans un fichier
    with open("resultat.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Données enregistrées dans resultat.json")

except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la requête : {e}")
except json.JSONDecodeError:
    print("La réponse n'est pas au format JSON")