# Importation de bibliothèques
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import requests
import time
import os
from dotenv import load_dotenv
import seaborn as sns
import statsmodels.formula.api as smf
 
# Chargement des variables d'environnement (fichiers .env) afin de récupérer les clés API
load_dotenv()
API_KEY_CENSUS = os.getenv("API_KEY_CENSUS")
# Robustesse
if API_KEY_CENSUS:
    print("Succès de chargement de la clé API Census")
else:
    print("Echec de chargement de la clé API Census")
    exit()

# Adresse des répertoires
repertoryData = "data"
repertoryOutputs = "outputs"

# Connexion à la base de données
dataBase = "data/patentsUSA.db"
connex = sqlite3.connect(dataBase)

# Requête SQL pour compter le nombre de brevets par ville
query = """
SELECT city, state, COUNT(*) AS nbrPatents
FROM patents
GROUP BY city, state
ORDER BY nbrPatents DESC
"""

# Stockage de la réponse SQL dans un DataFrame
df_patentsPerCity = pd.read_sql(query, connex)
connex.close()

# Gros biais IBM avec Armonk (+ Swiss Re et Université)
print(df_patentsPerCity.head())
outputFile = "data/patentsPerCityUSA.csv"
df_patentsPerCity.to_csv(outputFile, index=False, encoding="utf-8")
print(f"Fichier sauvegardé : {outputFile}")

# Chargement du fichier CSV de la population
file_population = os.path.join(repertoryData, "popByCitiesUSA_2010_2023.csv")
df_population = pd.read_csv(file_population)
# Fusion des deux DataFrames sur 'city' et 'state'
df_merged = pd.merge(df_patentsPerCity, df_population, on=["city", "state"], how="inner")
# Calcul du nombre de brevets par habitant et arrondi
df_merged["PatentsPerCapita"] = df_merged["nbrPatents"] / df_merged["PopMean_2010_2023"]
df_merged["PatentsPerCapita"] = df_merged["PatentsPerCapita"].round(6)
# Sauvegarde des données propres
outputFile = os.path.join(repertoryOutputs, "patentsPerCapitaPerCityUSA_2010_2023.csv")
df_merged.to_csv(outputFile, index=False, encoding="utf-8")

print(f"Fusion terminée. Fichier sauvegardé : {outputFile}")


# Génération du graphique de régression linéaire

#
df_merged["LogPop"] = np.log(df_merged["PopMean_2010_2023"])
df_merged["LogPatentsPerCapita"] = np.log(df_merged["PatentsPerCapita"])

print("\nGraphique relation nombre de brevets par habitants / nombre d'habitants de chaque ville")
# Nuage de points nombre de brevets par habitants / nombre d'habitants de chaque ville
# Définition de la taille de la représentation graphique
plt.figure(figsize=(16, 10))
# Construction du nuage de points
plt.scatter(df_merged["LogPatentsPerCapita"], df_merged["LogPop"])
# Ajout de la droite de régression
sns.regplot(x=df_merged["LogPatentsPerCapita"], y=df_merged["LogPop"], line_kws={"color":"red"})
# Légende et enregistrement
plt.xlabel("Brevets/habitants")
plt.ylabel("Population")
plt.title("Relation Brevets par Habitants / Nombre d'Habitants USA")
plt.savefig("outputs/USA-regression-brevets-par-hab-population.png")
print("Graphique généré (fichier 'outputs/USA-regression-brevets-par-hab-population.png')")

# Calcul de la relation des moindres carrés ordinaires entre le nombre d'habitants et la population
formula='LogPop ~ LogPatentsPerCapita'
results = smf.ols(formula, data=df_merged).fit()
print(results.summary())

'''
# Calcul du nombre de brevets par habitants
def calculatePatentsPerCapita(row):
    if row["population"] and row["population"] > 0:
        return row["nbrPatents"] / row["population"]
    else:
        return None
df_patentsPerCity["patentsPerCapita"] = df_patentsPerCity.apply(calculatePatentsPerCapita, axis=1)

# Vérification du DF
print(df_patentsPerCity[["city", "state", "nbrPatents", "population", "patentsPerCapita"]].head())

# Sauvegarde des données
# Dans un CSV
outputFile = "outputs/patentsPerCapitaUSA.csv"
df_patentsPerCity.to_csv(outputFile, index=False, encoding="utf-8")
print(f"Fichier des brevets par habitants par villes aux USA sauvegardé : {outputFile}")

# Dans la base de données
connex = sqlite3.connect(dataBase)
# Sauvegarde des données dans une table 'patentsPerCapita'
df_patentsPerCity.to_sql("patentsPerCapita", connex, if_exists="replace", index=False)
connex.close()
'''