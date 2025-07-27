# 🔍 LangChain Repository BeraMind

## 📋 Objectif du Projet

Ce projet vise à développer un outil d'analyse de sécurité automatisé qui utilise l'intelligence artificielle pour identifier les vulnérabilités de sécurité dans les dépôts de code. L'outil combine la puissance de **LangChain** avec **Ollama** pour analyser le code source et détecter les failles de sécurité potentielles.

### Fonctionnalités Principales

- 🔗 **Analyse de dépôts GitHub publics** via URL
- 📁 **Scan de dossiers locaux**
- 🤖 **Intelligence artificielle** avec LangChain + Ollama
- 🌐 **Interface web intuitive** avec Flask
- 📊 **Rapports détaillés** des vulnérabilités trouvées
- 🏷️ **Catégorisation** des failles par niveau de criticité

## 🎯 Objectifs Spécifiques

1. **Détection automatique** des vulnérabilités communes (OWASP Top 10)
2. **Analyse statique** du code source
3. **Identification** des dépendances vulnérables
4. **Évaluation** des pratiques de sécurité
5. **Génération** de rapports exploitables

## 🛠️ Stack Technique

- **Backend** : Python 3.9+
- **Framework Web** : Flask
- **IA/ML** : LangChain + Ollama
- **Analyse de Code** : AST, Regex patterns
- **Interface** : HTML/CSS/JavaScript
- **Gestion Git** : GitPython

## 📦 Requirements

### Dépendances Python

```
langchain>=0.1.0
flask>=2.3.0
ollama>=0.1.0
gitpython>=3.1.0
requests>=2.31.0
python-dotenv>=1.0.0
jinja2>=3.1.0
werkzeug>=2.3.0
click>=8.1.0
```

### Modèles Ollama Disponibles

- `deepseek-r1:14b` - Modèle principal pour l'analyse de sécurité
- `llama3.2:latest` - Modèle secondaire pour analyses complémentaires
- `llama3.2-vision:latest` - Pour l'analyse d'images/diagrammes (futur)

### Prérequis Système

- **Python** 3.9 ou supérieur
- **Ollama** installé avec les modèles ci-dessus
- **Git** pour cloner les dépôts
- **8GB RAM** minimum pour DeepSeek-R1:14b

## 🎯 Livrables Attendus

### 1. Interface Utilisateur

- ✅ Page d'accueil avec formulaire de saisie
- ✅ Support URL GitHub et chemin local
- ✅ Barre de progression pour le scan
- ✅ Page de résultats avec visualisations

### 2. Moteur d'Analyse

- ✅ Parser de code multi-langages
- ✅ Prompts LangChain optimisés
- ✅ Détection de patterns de sécurité
- ✅ Intégration Ollama

### 3. Détection de Vulnérabilités

#### Failles Ciblées

- **Injection SQL** - Requêtes non sécurisées
- **XSS** - Cross-Site Scripting
- **CSRF** - Cross-Site Request Forgery
- **Authentification faible** - Mots de passe faibles
- **Gestion des erreurs** - Information disclosure
- **Validation d'entrée** - Input sanitization
- **Dépendances** - Packages vulnérables
- **Secrets exposés** - API keys, tokens
- **Permissions** - Contrôles d'accès
- **Chiffrement** - Données sensibles

### 4. Rapports

- 📊 **Dashboard** avec métriques
- 📝 **Rapport détaillé** par vulnérabilité
- 🎯 **Recommandations** de correction
- 📈 **Score de sécurité** global
- 💾 **Export** JSON/PDF

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone <repo-url>
cd langchain-repo-scanner
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Vérifier les modèles Ollama

```bash
ollama list
# Vous devriez voir:
# deepseek-r1:14b
# llama3.2:latest
# llama3.2-vision:latest
```

### 4. Lancer l'application

```bash
python run.py
```

## 💡 Utilisation

1. **Accéder** à http://localhost:5000
2. **Saisir** l'URL du dépôt GitHub ou le chemin local
3. **Lancer** l'analyse (DeepSeek-R1 analysera le code)
4. **Consulter** les résultats et recommandations

## 📈 Métriques de Succès

- ✅ Détection de 90%+ des vulnérabilités OWASP Top 10
- ✅ Temps d'analyse < 5 minutes pour repo moyen
- ✅ Interface utilisateur intuitive
- ✅ Rapports exploitables et précis
- ✅ Support multi-langages (Python, JS, Java, etc.)

## 🤖 Modèles IA Utilisés

### DeepSeek-R1:14b (Principal)

- **Usage:** Analyse principale de sécurité
- **Avantages:** Excellent raisonnement, précision élevée
- **Taille:** 9.0 GB

### Llama3.2:latest (Secondaire)

- **Usage:** Analyses complémentaires et validation
- **Avantages:** Rapide, efficace pour les tâches simples
- **Taille:** 2.0 GB

## 🔄 Roadmap

- **Phase 1** : Core engine + Interface basique
- **Phase 2** : Détection avancée + Rapports
- **Phase 3** : Optimisations + Features avancées
- **Phase 4** : Déploiement + Documentation

## 📝 Notes Techniques

### Prompts Optimisés pour DeepSeek-R1

Les prompts utilisent la balise `<thinking>` pour améliorer le raisonnement du modèle DeepSeek-R1.

### Architecture Modulaire

Code organisé en modules réutilisables pour faciliter la maintenance.

### Performance

- DeepSeek-R1 offre une précision supérieure pour la détection de vulnérabilités
- Temps d'analyse: 2-8 minutes selon la taille du projet
- Consommation mémoire: ~8-12GB pendant l'analyse
- Utilisation de techniques de caching et de parallélisation pour optimiser les performances.
