import requests
import os

# Définition de la plage d'années à traiter
# Nous choisissons ici de travailler entre 2010 et 2023 (inclus)
# Il s'agit des années de publication / délivrance des brevets et pas des années de dépôt de demande de brevets souvent un peu antérieures
years = range(2010, 2024)

# Modèle d'URL des fichiers à télécharger
urlInputs = "https://annualized-gender-data-uspto.s3.amazonaws.com/{year}.csv"

# Répertoire de destination
repertoryDestination = "inputs/"
# Création du répertoire si nécessaire
os.makedirs(repertoryDestination, exist_ok=True)


def download_csv(url, repertoryDestination):
    # Gestion du nom du fichier
    filename = url.split("/")[-1]
    filepath = os.path.join(repertoryDestination, filename)

    # Robustesse
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print(f"{filename} téléchargé")

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement de {url}: {e}")

# Téléchargement des fichiers CSV en générant les URL
for year in years:
    urlDef = urlInputs.format(year=year)
    download_csv(urlDef, repertoryDestination)

'''
# Liste des fichiers de données à télécharger
urlInputs = [
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2023.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2022.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2021.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2020.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2019.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2018.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2017.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2016.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2015.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2014.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2013.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2012.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2011.csv",
    "https://annualized-gender-data-uspto.s3.amazonaws.com/2010.csv"
]
'''