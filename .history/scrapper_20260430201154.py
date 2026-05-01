!pip install bs4
import requests
from bs4 import BeautifulSoup

url = "https://example.com"

# 1. Récupérer la page
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 2. Trouver le tableau (le premier ici)
table = soup.find("table")

# 3. Extraire les lignes
data = []
for row in table.find_all("tr"):
    cols = row.find_all(["td", "th"])
    cols = [col.text.strip() for col in cols]
    data.append(cols)

# 4. Afficher
for line in data:
    print(line)