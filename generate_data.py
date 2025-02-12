import time
import json
import random
import ollama
import os
import re

# Créer un dossier pour stocker les fichiers générés
os.makedirs("./data", exist_ok=True)
os.makedirs("./description", exist_ok=True)

# Durée de la génération (10 minutes)
DURATION_SECONDS = 600
start_time = time.time()

# Liste pour stocker les descriptions des fichiers générés
description_list = []

model = 'deepseek-r1:14b'

def extract_json_codeblock(text):
    """Retourne le contenu JSON entre ```json et ``` si présent."""
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    return None

def extract_json_string(text):
    """Extrait le premier objet JSON complet depuis la chaîne."""
    start = text.find('{')
    if start == -1:
        raise Exception("Aucune accolade ouvrante trouvée dans la chaîne.")
    brace_count = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        char = text[i]
        if char == '"' and not escape:
            in_string = not in_string
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return text[start:i+1]
        if char == '\\' and not escape:
            escape = True
        else:
            escape = False
    raise Exception("JSON complet non trouvé dans le texte.")

def extract_json(text):
    """
    Tente d'extraire le JSON entre ```json et ```.
    Si non trouvé, utilise l'extraction basique.
    """
    json_content = extract_json_codeblock(text)
    if json_content is not None:
        return json_content.strip()
    return extract_json_string(text)

def generate_random_dataset():
    """Génère un dataset JSON réaliste lié à l'Algérie pour un thème donné."""
    prompt = """
    Génère un objet JSON contenant des données réalistes et détaillées sur l'Algérie pour le thème sélectionné.
    Le format doit être STRICTEMENT un objet JSON (sans texte supplémentaire) avec des clés représentatives et des valeurs plausibles.
    Exemples de thèmes : prix moyens immobiliers par wilaya, taux de chômage par secteur, nombre de naissances par région, etc. PRENez un thème spécifique. et ecrivez les clés en anglais.
    """
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

def generate_description(slug, category, title, path):
    """Génère une description JSON pour le fichier généré."""
    description_prompt = f"""
    Génère un objet JSON de description pour le dataset {title}.
    Ce dataset est stocké sous {path} et fait partie de la catégorie {category}.
    Le format doit suivre cette structure, traduits dans les langues manquantes, change l'objet source  avec des informations réelles.
    {{
        "type": "file",
        "title": {{
            "en": "",
            "ar": "",
            "fr": "{title}"
        }},
        "slug": "{slug}",
        "link": null,
        "path": "{path}",
        "description": {{
            "en": "",
            "ar": "",
            "fr": "Ce fichier contient des informations sur {title}."
        }},
        "descriptionREADME": "# {title}\\n\\nCe dataset fournit des informations détaillées sur {category} en Algérie.",
        "source": {{
            "name": "World Health Organization",
            "pictureUrl": "",
            "website": "https://data.who.int",
            "contact": ""
        }},
        "updatedDate": "10/02/2025",
        "keywords": {{
            "en": [],
            "ar": [],
            "fr": ["{category.lower()}"]
        }},
        "category": {{
            "en": "",
            "ar": "",
            "fr": "{category}"
        }},
        "provider": {{
            "name": "Berachem MARKRIA",
            "pictureUrl": "https://www.berachem.dev/assets/moi_bg-Bb3CctC3.png",
            "website": "https://www.berachem.dev/",
            "contact": "berachem.markria@gmail.com"
        }}
    }}
    """
    response = ollama.chat(model=model, messages=[{"role": "user", "content": description_prompt}])
    return response['message']['content']

# Remplacer la boucle avec une exécution sans limite de temps
while time.time() - start_time < DURATION_SECONDS:
    try:
        # Générer un slug basé sur le timestamp et choisir une catégorie
        categories = ["Économie", "Santé", "Transport", "Géographie", "Climat", "Démographie"]
        category = random.choice(categories)
        slug = f"{category.lower()}-{time.strftime('%Y%m%d_%H%M%S')}"
        title = f"Dataset sur {category} en Algérie"
        path = f"./data/{slug}.json"

        # Générer les données JSON
        print(f"Génération du dataset: {title}")
        data = generate_random_dataset()
        if not data.strip():
            raise Exception("La réponse du dataset est vide")

        # Enlever les balises inutiles et extraire le JSON
        data = re.sub(r'<[^>]*>', '', data)
        json_str = extract_json(data)
        data_obj = json.loads(json_str)

        # Sauvegarder l'objet JSON dans le fichier
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data_obj, file, indent=4, ensure_ascii=False)

        # Générer la description dans un fichier dédié
        description = generate_description(slug, category, title, path)
        description = re.sub(r'<[^>]*>', '', description)
        desc_json_str = extract_json(description)
        description_data = json.loads(desc_json_str)
        
        description_path = f"./description/{slug}.json"
        with open(description_path, "w", encoding="utf-8") as file:
            json.dump(description_data, file, indent=4, ensure_ascii=False)
        
        # Ajouter la description à la liste
        description_list.append(description_data)
        
        print(f"Dataset généré: {path}")
    except Exception as e:
        print(f"Erreur lors de la génération du dataset: {e}")
