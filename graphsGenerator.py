# Importation de bibliothèques
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import requests
import time
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement (fichiers .env) afin de récupérer les clés API
load_dotenv()
API_KEY_CENSUS = os.getenv("API_KEY_CENSUS")
# Robustesse
if API_KEY_CENSUS:
    print("Succés de chargement de la clé API Census")
else:
    print("Echec de chargement de la clé API Census")
    exit()

# Connexion à la base de données
dataBase = "data/patentsUSA.db"
connex = sqlite3.connect(dataBase)

# Requête SQL pour compter le nombre de brevets par ville
query = """
SELECT city, state, COUNT(*) AS num_patents
FROM patents
GROUP BY city, state
ORDER BY num_patents DESC
"""

# Stockage de la réponse SQL dans un DataFrame
df_cities = pd.read_sql(query, connex)
connex.close()

# Vérification du DF
# Gros biais IBM avec Armonk (+ Swiss Re et Université)
print(df_cities.head())

# Récupération de la population des villes grâce à Census