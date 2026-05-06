"""import pandas as pd

url = "https://wynncraft.fandom.com/wiki/Scribing"
tables = pd.read_html(url)

df = tables[0]  # premier tableau
print(df)"""

import requests

url = "https://wynncraft.fandom.com/wiki/Scribing"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
print(response.text)