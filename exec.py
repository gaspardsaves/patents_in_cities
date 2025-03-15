import subprocess

# Liste des codes à exécuter
scripts = ["downloadData.py", "extraction.py", "graphsGenerator.py", "mapGenerator.py"]

# Exécution des fichiers de code dans le bon ordre
for script in scripts:
    subprocess.run(["python", script])