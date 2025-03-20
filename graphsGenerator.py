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
from sklearn.linear_model import LinearRegression, RANSACRegressor
from scipy import stats

''' 
# Chargement des variables d'environnement (fichiers .env) afin de récupérer les clés API
load_dotenv()
API_KEY_CENSUS = os.getenv("API_KEY_CENSUS")
# Robustesse
if API_KEY_CENSUS:
    print("Succès de chargement de la clé API Census")
else:
    print("Echec de chargement de la clé API Census")
    exit()
'''

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

# Charger les brevets
connex = sqlite3.connect(dataBase)
df_patents = pd.read_sql("SELECT * FROM patents", connex)

# Fusion avec les données de population
df_both = df_patents.merge(df_population, on=["city", "state"], how="left")

# Sauvegarde de la base de données
df_both.to_sql("patentsPopulation", connex, if_exists="replace", index=False)
connex.close()

# Fusion des deux DataFrames sur 'city' et 'state'
df_merged = pd.merge(df_patentsPerCity, df_population, on=["city", "state"], how="inner")
# Calcul du nombre de brevets par habitant et arrondi
df_merged["PatentsPerCapita"] = df_merged["nbrPatents"] / df_merged["PopMean_2010_2023"]
df_merged["PatentsPerCapita"] = df_merged["PatentsPerCapita"].round(6)
# Sauvegarde des données propres
outputFile = os.path.join(repertoryOutputs, "patentsPerCapitaPerCityUSA_2010_2023.csv")
df_merged.to_csv(outputFile, index=False, encoding="utf-8")

print(f"Fusion terminée. Fichier sauvegardé : {outputFile}")


# Génération du graphique de régression linéaire sans enlever les quantiles extrêmes
# Passage en echélle logarithmique pour améliorer la régression
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
plt.xlabel("Log(Brevets/habitants)")
plt.ylabel("Log(Population)")
plt.title("Relation Brevets par Habitants / Nombre d'Habitants USA")
plt.savefig("outputs/USA-regression-brevets-par-hab-population.png")
print("Graphique généré (fichier 'outputs/USA-regression-brevets-par-hab-population.png')")

# Calcul de la relation des moindres carrés ordinaires entre le nombre d'habitants et la population
formula='LogPop ~ LogPatentsPerCapita'
results = smf.ols(formula, data=df_merged).fit()
print(results.summary())

# Nouveau graphique avec des données nettoyées
df_clean = df_merged.copy()

# Scores Z
z_scores = stats.zscore(df_merged[['LogPatentsPerCapita', 'LogPop']])
abs_z_scores = np.abs(z_scores)
filtered_entries = (abs_z_scores < 2.5).all(axis=1)
df_clean_z = df_merged[filtered_entries]

# Résidus
X = df_merged[['LogPop']].values
y = df_merged['LogPatentsPerCapita'].values
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
residuals = y - y_pred
std_residuals = np.std(residuals)
df_clean_residuals = df_merged[np.abs(residuals) <= 2.5 * std_residuals]

# RANSAC
ransac = RANSACRegressor(random_state=42)
ransac.fit(X, y)
inlier_mask = ransac.inlier_mask_
df_clean_ransac = df_merged[inlier_mask]

# Visualisation de la régression avec données nettoyées
# Définition de la taille de la représentation graphique
plt.figure(figsize=(12, 8))
# Construction des nuages de points
plt.scatter(df_merged['LogPop'], df_merged['LogPatentsPerCapita'], alpha=0.3, label='Données originales')
plt.scatter(df_clean_residuals['LogPop'], df_clean_residuals['LogPatentsPerCapita'], 
            color='green', alpha=0.6, label='Données nettoyées (résidus)')
# Nouvelle régression sur données nettoyées
X_clean = df_clean_residuals[['LogPop']].values
y_clean = df_clean_residuals['LogPatentsPerCapita'].values
model_clean = LinearRegression()
model_clean.fit(X_clean, y_clean)
# Tracer les lignes de régression
x_range = np.linspace(df_merged['LogPop'].min(), df_merged['LogPop'].max(), 100).reshape(-1, 1)
plt.plot(x_range, model.predict(x_range), 'r-', linewidth=2, label='Régression originale')
plt.plot(x_range, model_clean.predict(x_range), 'b-', linewidth=2, label='Régression nettoyée')
# Légende et enregistrement
plt.xlabel('Log(Habitants)')
plt.ylabel('Log(Brevets par habitants)')
plt.title('Régression avec les données nettoyées')
plt.legend()
plt.grid(True)
plt.savefig("outputs/USA-regression-cleaned-brevets-par-hab-population.png")
print("Graphique généré (fichier 'outputs/USA-regression-cleaned-brevets-par-hab-population.png')")

# Calcul de la relation des moindres carrés ordinaires entre le nombre de brevets par habitants et la population
formula='LogPatentsPerCapita ~ LogPop'
results = smf.ols(formula, data=df_clean).fit()
print(results.summary())

# Affichege des statistiques de la régression
print(f"R² original : {model.score(X, y):.4f}")
print(f"R² nettoyé : {model_clean.score(X_clean, y_clean):.4f}")
print(f"Pente originale : {model.coef_[0]:.4f}")
print(f"Pente nettoyée : {model_clean.coef_[0]:.4f}")


# Traitement des domaines des brevets
'''
# Connexion à la base de données
dataBase = "data/patentsUSA.db"
connex = sqlite3.connect(dataBase)
query2 = """
SELECT first_wipo_sector_title, city, state, SUM(patent_count) AS nbrPatents, PopMean_2010_2023
FROM patents
GROUP BY first_wipo_sector_title, city, state, PopMean_2010_2023
ORDER BY first_wipo_sector_title, nbrPatents DESC;
"""
connex.close()
'''

# Chargement des données
df1 = pd.read_csv("data/patentsPerCityUSA.csv")
df2 = pd.read_csv("data/test.csv")

df3 = pd.merge(df1, df2, on=["city", "state"], how="inner")

df = df3[df3['PopMean_2010_2023'] > 0]
df.loc[:,"PatentsPerCapita"] = df["nbrPatents"] / df["PopMean_2010_2023"]

# Enlèvement des valeurs extrêmes
df = df[(df["PatentsPerCapita"] > df["PatentsPerCapita"].quantile(0.01)) &
        (df["PatentsPerCapita"] < df["PatentsPerCapita"].quantile(0.99))]

# Transformation en log pour linéariser la relation
df["LogPop"] = df["PopMean_2010_2023"].apply(lambda x: np.log(x) if x > 0 else 0)
df["LogPatentsPerCapita"] = df["PatentsPerCapita"].apply(lambda x: np.log(x) if x > 0 else 0)

# Régression séparée par secteur
domains = df["first_wipo_sector_title"].unique()
results = {}

for domain in domains:
    df_domain = df[df["first_wipo_sector_title"] == domain]
    
    if df_domain.shape[0] > 30:
        model = smf.ols("LogPop ~ LogPatentsPerCapita", data=df_domain).fit()
        results[domain] = model.pvalues["LogPatentsPerCapita"]
        # Génération d'un graphique
        plt.figure(figsize=(8, 5))
        sns.regplot(x=df_domain["LogPatentsPerCapita"], y=df_domain["LogPop"], scatter_kws={'alpha':0.3}, line_kws={"color": "red"})
        plt.title(f"Relation Brevets/Habitants pour le domaine : {domain}")
        plt.xlabel("Log Brevets par Habitants")
        plt.ylabel("Log Population")
        plt.savefig(f"outputs/USA-regression-{domain}-brevets-par-hab-population.png")
        print(f"Graphique généré (fichier 'outputs/USA-regression-{domain}-cleaned-brevets-par-hab-population.png')")

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