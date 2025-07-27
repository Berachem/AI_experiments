"""
Ce script permet de générer des réponses à une question donnée en utilisant un modèle de base, puis de les corriger et les améliorer en utilisant un modèle plus puissant.
@author: Berachem MARKRIA
"""

import json
import ollama
import time  # Utilisé pour la pause

# 📌 Configuration des modèles
MODEL_GENERATEUR = "llama3.2"   # Modèle de base à fine-tuner
MODEL_CORRECTEUR = "deepseek-r1:14b"    # Modèle plus puissant pour améliorer les réponses
N_EXEMPLES = 1            # Nombre de réponses générées
QUESTION = "Comment collecter légalement des informations OSINT sur une entreprise ?"  # Sujet

def main():
    # 📁 Liste pour stocker les données de fine-tuning
    dataset = []

    for i in range(N_EXEMPLES):
        print(f"\n📝 Génération de l'exemple {i+1}/{N_EXEMPLES}...")

        # 🔹 Étape 1 : Génération par le modèle à fine-tuner (streaming)
        stream_gen = ollama.chat(
            model=MODEL_GENERATEUR,
            messages=[{"role": "user", "content": QUESTION}],
            stream=True,
        )
        generated_text = ""
        print("🔰 Réponse générée par le modèle générateur "+MODEL_GENERATEUR)
        for chunk in stream_gen:
            generated_text += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)
        print()  # Nouvelle ligne après le streaming

        # 🔹 Étape 2 : Correction et amélioration par le modèle correcteur (streaming)
        prompt_correcteur = f"""
        Tu es un expert en OSINT. Une IA plus basique a généré la réponse suivante :
        
        {generated_text}

        Corrige et améliore cette réponse en la rendant plus détaillée, précise, et conforme aux bonnes pratiques OSINT.
        """
        print("✨ Correction et amélioration par le modèle correcteur "+MODEL_CORRECTEUR)
        stream_corr = ollama.chat(
            model=MODEL_CORRECTEUR,
            messages=[{"role": "user", "content": prompt_correcteur}],
            stream=True,
        )
        corrected_text = ""
        for chunk in stream_corr:
            corrected_text += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)
        print()

        # 🔹 Étape 3 : Ajout des données au dataset de fine-tuning
        dataset.append({
            "instruction": QUESTION,
            "generated_response": generated_text,
            "corrected_response": corrected_text
        })

        # Pause pour éviter de surcharger Ollama
        time.sleep(1)

    # 🔹 Étape 4 : Sauvegarde du dataset pour le fine-tuning
    dataset_file = "osint_dataset.json"
    with open(dataset_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)

    print(f"\n📁 Dataset de fine-tuning sauvegardé dans {dataset_file} ✅")

if __name__ == "__main__":
    main()

