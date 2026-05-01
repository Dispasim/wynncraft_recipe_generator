import pandas as pd

url = "https://wynncraft.fandom.com/wiki/Scribing"
tables = pd.read_html(url)

df = tables[0]  # premier tableau
print(df)