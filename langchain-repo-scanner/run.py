#!/usr/bin/env python3
"""
Script de lancement pour le BeraMind
"""

import os
import sys
import requests
from pathlib import Path

def check_ollama():
    """Vérifie si Ollama est disponible"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def check_required_models(tags_data):
    """Vérifie si les modèles requis sont disponibles"""
    if not tags_data or 'models' not in tags_data:
        return False, []
    
    available_models = [model['name'] for model in tags_data['models']]
    required_models = ['deepseek-r1:14b', 'llama3.2:latest']
    
    missing_models = []
    for model in required_models:
        if not any(available.startswith(model) for available in available_models):
            missing_models.append(model)
    
    return len(missing_models) == 0, missing_models

def setup_directories():
    """Crée les dossiers nécessaires"""
    directories = ['temp_repos', 'results', 'logs', 'temp']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Dossier {directory} créé/vérifié")

def main():
    """Point d'entrée principal"""
    print("🔍 Démarrage du BeraMind avec DeepSeek-R1...")
    print("=" * 60)
    
    # Vérifier Python
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ requis")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Créer les dossiers
    setup_directories()
    
    # Vérifier Ollama
    ollama_available, tags_data = check_ollama()
    if not ollama_available:
        print("❌ Ollama non disponible. Démarrez Ollama et réessayez.")
        sys.exit(1)
    
    print("✓ Ollama disponible")
    
    # Vérifier les modèles
    models_ok, missing = check_required_models(tags_data)
    if not models_ok:
        print(f"⚠️  Modèles manquants: {', '.join(missing)}")
        print("   Installez-les avec:")
        for model in missing:
            print(f"   ollama pull {model}")
        
        response = input("\nContinuer quand même ? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    else:
        print("✓ Modèles DeepSeek-R1 et Llama3.2 disponibles")
    
    # Afficher les modèles disponibles
    if tags_data and 'models' in tags_data:
        print("\n📋 Modèles Ollama détectés:")
        for model in tags_data['models']:
            size_gb = model.get('size', 0) / (1024**3)
            print(f"   • {model['name']} ({size_gb:.1f} GB)")
    
    # Démarrer Flask
    print(f"\n🚀 Démarrage de l'application...")
    print(f"   URL: http://localhost:5000")
    print(f"   Modèle principal: DeepSeek-R1:14b")
    print(f"   Ctrl+C pour arrêter\n")
    
    from app import app
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Arrêt du scanner...")

if __name__ == '__main__':
    main()
