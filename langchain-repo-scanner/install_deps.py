#!/usr/bin/env python3
"""
Script pour installer les dépendances correctes
"""

import subprocess
import sys

def install_package(package):
    """Installe un package avec pip"""
    try:
        print(f"📦 Installation de {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation {package}: {e}")
        return False

def main():
    """Installe toutes les dépendances nécessaires"""
    print("🔧 Installation des dépendances pour LangChain BeraMind")
    print("=" * 60)
    
    # Packages essentiels avec versions spécifiques
    packages = [
        "langchain>=0.1.0",
        "langchain-community>=0.0.10", 
        "langchain-ollama>=0.1.0",
        "flask>=2.3.0",
        "gitpython>=3.1.40",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "jinja2>=3.1.2",
        "werkzeug>=2.3.7",
        "click>=8.1.7",
        'reportlab>=3.6.0',
    ]
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n" + "=" * 60)
    
    if failed_packages:
        print(f"❌ Échec d'installation pour: {', '.join(failed_packages)}")
        print("Essayez d'installer manuellement:")
        for pkg in failed_packages:
            print(f"  pip install {pkg}")
        return False
    else:
        print("✅ Toutes les dépendances ont été installées avec succès!")
        print("\nVous pouvez maintenant lancer:")
        print("  python run.py")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
