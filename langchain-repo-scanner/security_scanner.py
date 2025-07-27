import os
import ast
import re
import json
import git
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Import mis à jour pour éviter la dépréciation
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    # Fallback pour les anciennes versions
    from langchain.llms import Ollama as OllamaLLM

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from prompts import SecurityPrompts

class SecurityScanner:
    def __init__(self, progress_callback=None):
        try:
            # Utiliser les variables d'environnement
            ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            primary_model = os.getenv('OLLAMA_MODEL_PRIMARY', 'deepseek-r1:14b')
            max_workers = int(os.getenv('MAX_CONCURRENT_SCANS', '2'))
            max_file_size = int(os.getenv('MAX_FILE_SIZE', '1048576'))
            
            print(f"🔧 Configuration:")
            print(f"   - URL Ollama: {ollama_base_url}")
            print(f"   - Modèle principal: {primary_model}")
            print(f"   - Workers max: {max_workers}")
            print(f"   - Taille fichier max: {max_file_size} bytes")
            
            # Initialiser le modèle avec la configuration
            self.llm = OllamaLLM(model=primary_model, base_url=ollama_base_url)
            self.prompts = SecurityPrompts()
            self.vulnerabilities = []
            self.max_workers = max_workers
            self.max_file_size = max_file_size
            self.supported_extensions = {'.py', '.js', '.java', '.php', '.rb', '.go', '.cpp', '.c', '.cs'}
            self.progress_callback = progress_callback
            
            print(f"✓ Scanner initialisé avec {primary_model}")
        except Exception as e:
            print(f"❌ Erreur initialisation du scanner: {str(e)}")
            raise
    
    def _update_progress(self, step: str, progress: int, details: dict = None):
        """Met à jour le progrès si un callback est défini"""
        if self.progress_callback:
            self.progress_callback(step, progress, details or {})
        
    def scan_github_repo(self, repo_url: str) -> Dict[str, Any]:
        """Analyse un dépôt GitHub public"""
        try:
            print(f"🔄 Clonage du dépôt: {repo_url}")
            
            # Cloner le dépôt
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            local_path = f"temp_repos/{repo_name}"
            
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            
            git.Repo.clone_from(repo_url, local_path)
            print(f"✓ Dépôt cloné dans: {local_path}")
            
            # Analyser le dépôt local
            results = self.scan_local_directory(local_path)
            results['source'] = {'type': 'github', 'url': repo_url}
            
            # Nettoyer
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
                print("✓ Dossier temporaire nettoyé")
            
            return results
            
        except git.exc.GitError as e:
            return {'error': f'Erreur Git: {str(e)}. Vérifiez que l\'URL est correcte et que le dépôt est public.'}
        except Exception as e:
            return {'error': f'Erreur scan GitHub: {str(e)}'}
    
    def scan_local_directory(self, directory_path: str) -> Dict[str, Any]:
        """Analyse un dossier local avec suivi de progression"""
        try:
            print(f"🔄 Analyse du dossier: {directory_path}")
            self._update_progress('collecting', 15, {'target': directory_path})
            
            directory_path = Path(directory_path)
            if not directory_path.exists():
                return {'error': f'Dossier non trouvé: {directory_path}'}
            
            # Collecter les fichiers
            code_files = self._collect_code_files(directory_path)
            files_count = len(code_files)
            print(f"📁 {files_count} fichiers de code trouvés")
            
            self._update_progress('file_collection', 25, {
                'files_found': files_count,
                'target': str(directory_path)
            })
            
            if not code_files:
                return {'error': 'Aucun fichier de code supporté trouvé'}
            
            # Analyser les fichiers
            vulnerabilities = []
            print("🔍 Analyse des fichiers en cours...")
            
            self._update_progress('static_analysis', 35, {
                'files_found': files_count
            })
            
            # Analyse séquentielle pour éviter les problèmes de threading
            for i, file_path in enumerate(code_files):
                try:
                    print(f"📄 Analyse de {file_path.name} ({i+1}/{files_count})")
                    
                    # Mettre à jour le progrès pour ce fichier
                    files_analyzed = i + 1
                    progress = 35 + int((files_analyzed / files_count) * 30)  # 35-65%
                    
                    self._update_progress('ai_analysis', progress, {
                        'files_analyzed': files_analyzed,
                        'total_files': files_count,
                        'current_file': file_path.name,
                        'vulnerabilities_found': len(vulnerabilities)
                    })
                    
                    # Analyser le fichier
                    file_vulns = self._analyze_file_with_progress(file_path, i, files_count)
                    vulnerabilities.extend(file_vulns)
                    
                    print(f"✓ Fichier {files_analyzed}/{files_count} analysé - {len(file_vulns)} vulnérabilités trouvées")
                    
                except Exception as e:
                    print(f"⚠️ Erreur analyse fichier {file_path.name}: {str(e)}")
                    vulnerabilities.append({
                        'type': 'analysis_error',
                        'file': str(file_path),
                        'message': f'Erreur lors de l\'analyse: {str(e)}',
                        'severity': 'low'
                    })
            
            # Analyser les dépendances
            print("📦 Analyse des dépendances...")
            self._update_progress('dependency_check', 75, {
                'vulnerabilities_found': len(vulnerabilities)
            })
            
            dependency_vulns = self._analyze_dependencies(directory_path)
            vulnerabilities.extend(dependency_vulns)
            
            # Générer le rapport
            print("📊 Génération du rapport...")
            self._update_progress('generating_report', 90, {
                'vulnerabilities_found': len(vulnerabilities)
            })
            
            report = self._generate_report(vulnerabilities, directory_path)
            
            self._update_progress('complete', 100, {
                'vulnerabilities_found': len(vulnerabilities),
                'security_score': report.get('summary', {}).get('security_score', 0)
            })
            
            return report
            
        except Exception as e:
            error_msg = f'Erreur scan local: {str(e)}'
            print(f"❌ {error_msg}")
            self._update_progress('error', 0, {'error': error_msg})
            return {'error': error_msg}
    
    def _collect_code_files(self, directory: Path) -> List[Path]:
        """Collecte tous les fichiers de code à analyser"""
        code_files = []
        
        for file_path in directory.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in self.supported_extensions and
                not self._is_excluded_path(file_path)):
                code_files.append(file_path)
        
        return code_files
    
    def _is_excluded_path(self, file_path: Path) -> bool:
        """Vérifie si le chemin doit être exclu"""
        excluded_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'build', 'dist'}
        
        for part in file_path.parts:
            if part in excluded_dirs:
                return True
        
        return False
    
    def _analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyse un fichier pour détecter les vulnérabilités"""
        vulnerabilities = []
        
        try:
            # Vérifier la taille du fichier
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                print(f"⚠️ Fichier {file_path.name} trop volumineux ({file_size} bytes), ignoré")
                return [{
                    'type': 'file_too_large',
                    'file': str(file_path),
                    'message': f'Fichier trop volumineux ({file_size} bytes)',
                    'severity': 'low'
                }]
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Analyse par règles statiques
            static_vulns = self._static_analysis(file_path, content)
            vulnerabilities.extend(static_vulns)
            
            # Analyse par IA
            ai_vulns = self._ai_analysis(file_path, content)
            vulnerabilities.extend(ai_vulns)
            
        except Exception as e:
            vulnerabilities.append({
                'type': 'error',
                'file': str(file_path),
                'message': f'Erreur lecture fichier: {str(e)}',
                'severity': 'low'
            })
        
        return vulnerabilities
    
    def _analyze_file_with_progress(self, file_path: Path, file_index: int, total_files: int) -> List[Dict[str, Any]]:
        """Analyse un fichier avec mise à jour du progrès"""
        vulnerabilities = []
        
        try:
            # Vérifier la taille du fichier
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                print(f"⚠️ Fichier {file_path.name} trop volumineux ({file_size} bytes), ignoré")
                return [{
                    'type': 'file_too_large',
                    'file': str(file_path),
                    'message': f'Fichier trop volumineux ({file_size} bytes)',
                    'severity': 'low'
                }]
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Analyse par règles statiques (rapide)
            print(f"  🔍 Analyse statique de {file_path.name}")
            static_vulns = self._static_analysis(file_path, content)
            vulnerabilities.extend(static_vulns)
            
            # Analyse par IA (plus lente)
            print(f"  🤖 Analyse IA de {file_path.name}")
            ai_vulns = self._ai_analysis(file_path, content)
            vulnerabilities.extend(ai_vulns)
            
            # Ajouter le contexte de code pour les vulnérabilités
            for vuln in vulnerabilities:
                if 'line' in vuln and vuln['line']:
                    vuln['code_context'] = self._get_code_context(content, vuln['line'])
            
            print(f"  ✅ {file_path.name}: {len(vulnerabilities)} vulnérabilités trouvées")
            
        except Exception as e:
            error_msg = f'Erreur lecture fichier: {str(e)}'
            print(f"  ❌ Erreur {file_path.name}: {error_msg}")
            vulnerabilities.append({
                'type': 'file_error',
                'file': str(file_path),
                'message': error_msg,
                'severity': 'low'
            })
        
        return vulnerabilities
    
    def _get_code_context(self, content: str, line_number: int, context_lines: int = 2) -> str:
        """Récupère le contexte de code autour d'une ligne"""
        lines = content.split('\n')
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)
        
        context_lines_list = []
        for i in range(start_line, end_line):
            line_content = lines[i]
            # Marquer la ligne problématique
            if i == line_number - 1:
                context_lines_list.append(f">>> {line_content}")
            else:
                context_lines_list.append(f"    {line_content}")
        
        return '\n'.join(context_lines_list)
    
    def _static_analysis(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Analyse statique avec des règles prédéfinies"""
        vulnerabilities = []
        lines = content.split('\n')
        
        # Patterns de vulnérabilités communes
        patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*\%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'WHERE.*=.*\+',
            ],
            'xss': [
                r'innerHTML\s*=.*\+',
                r'document\.write\s*\(.*\+',
                r'eval\s*\(',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][^"\']{10,}["\']',
                r'secret\s*=\s*["\'][^"\']{8,}["\']',
            ],
            'insecure_crypto': [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES\s*\(',
            ]
        }
        
        for vuln_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            'type': vuln_type,
                            'file': str(file_path),
                            'line': line_num,
                            'code': line.strip(),
                            'severity': self._get_severity(vuln_type),
                            'description': self._get_description(vuln_type)
                        })
        
        return vulnerabilities
    
    def _ai_analysis(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Analyse par IA avec LangChain - version robuste"""
        try:
            # Limiter la taille du contenu pour éviter les timeouts
            max_content_size = min(1000, self.max_file_size // 4)  # Réduire encore plus
            if len(content) > max_content_size:
                content = content[:max_content_size] + "\n... (truncated for analysis)"
            
            print(f"    🤖 Analyse IA de {file_path.name} ({len(content)} chars)")
            
            # Créer le prompt
            prompt = PromptTemplate(
                input_variables=["code", "filename"],
                template=self.prompts.get_security_analysis_prompt()
            )
            
            # Créer la chaîne LangChain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Analyser avec gestion d'erreur robuste
            try:
                response = chain.run(code=content, filename=file_path.name)
                print(f"    ✅ Analyse IA terminée pour {file_path.name}")
                
                # Parser la réponse
                return self._parse_ai_response(response, file_path)
                
            except Exception as llm_error:
                print(f"    ⚠️ Erreur LLM pour {file_path.name}: {str(llm_error)}")
                # Retourner une analyse vide plutôt qu'une erreur pour ne pas bloquer
                return []
            
        except Exception as e:
            print(f"    ❌ Erreur analyse IA pour {file_path.name}: {str(e)}")
            return []
    
    def _parse_ai_response(self, response: str, file_path: Path) -> List[Dict[str, Any]]:
        """Parse la réponse de l'IA"""
        vulnerabilities = []
        
        try:
            # Gestion de la réponse "pas de vulnérabilités"
            if "NO_VULNERABILITIES_FOUND" in response.upper():
                return []
            
            # Parser les vulnérabilités trouvées
            lines = response.split('\n')
            current_vuln = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('TYPE:'):
                    current_vuln['type'] = line.replace('TYPE:', '').strip()
                elif line.startswith('SEVERITY:'):
                    current_vuln['severity'] = line.replace('SEVERITY:', '').strip().lower()
                elif line.startswith('DESCRIPTION:'):
                    current_vuln['description'] = line.replace('DESCRIPTION:', '').strip()
                elif line.startswith('LINE:'):
                    try:
                        current_vuln['line'] = int(line.replace('LINE:', '').strip())
                    except:
                        pass
                elif line == '---' and current_vuln:
                    current_vuln['file'] = str(file_path)
                    vulnerabilities.append(current_vuln)
                    current_vuln = {}
            
            # Ajouter la dernière vulnérabilité si pas de séparateur final
            if current_vuln and 'type' in current_vuln:
                current_vuln['file'] = str(file_path)
                vulnerabilities.append(current_vuln)
                
        except Exception as e:
            print(f"⚠️ Erreur parsing réponse IA: {str(e)}")
        
        return vulnerabilities
    
    def _analyze_dependencies(self, directory: Path) -> List[Dict[str, Any]]:
        """Analyse les dépendances pour des vulnérabilités connues"""
        vulnerabilities = []
        
        # Fichiers de dépendances à analyser
        dep_files = {
            'requirements.txt': 'python',
            'package.json': 'npm',
            'pom.xml': 'maven',
            'Gemfile': 'ruby'
        }
        
        for dep_file, ecosystem in dep_files.items():
            dep_path = directory / dep_file
            if dep_path.exists():
                try:
                    with open(dep_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Analyse simple des versions
                    if ecosystem == 'python':
                        vulns = self._analyze_python_deps(content)
                        vulnerabilities.extend(vulns)
                        
                except Exception as e:
                    vulnerabilities.append({
                        'type': 'dependency_error',
                        'file': str(dep_path),
                        'message': f'Erreur analyse dépendances: {str(e)}',
                        'severity': 'low'
                    })
        
        return vulnerabilities
    
    def _analyze_python_deps(self, content: str) -> List[Dict[str, Any]]:
        """Analyse les dépendances Python"""
        vulnerabilities = []
        
        # Packages Python connus pour avoir des vulnérabilités
        vulnerable_packages = {
            'django': ['<3.2.13', '<4.0.4'],
            'flask': ['<2.2.0'],
            'requests': ['<2.28.0'],
            'urllib3': ['<1.26.5']
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if '==' in line:
                package, version = line.split('==')
                package = package.strip()
                version = version.strip()
                
                if package in vulnerable_packages:
                    vulnerabilities.append({
                        'type': 'vulnerable_dependency',
                        'package': package,
                        'version': version,
                        'severity': 'medium',
                        'description': f'Package {package} version {version} peut avoir des vulnérabilités'
                    })
        
        return vulnerabilities
    
    def _generate_report(self, vulnerabilities: List[Dict[str, Any]], directory: Path) -> Dict[str, Any]:
        """Génère le rapport final avec gestion d'erreur robuste"""
        try:
            # Compter par sévérité
            severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            
            for vuln in vulnerabilities:
                severity = vuln.get('severity', 'low')
                if severity in severity_counts:
                    severity_counts[severity] += 1
                else:
                    # Gérer les sévérités inconnues
                    severity_counts['low'] += 1
            
            # Calculer le score de sécurité
            total_vulns = len(vulnerabilities)
            critical_weight = severity_counts['critical'] * 10
            high_weight = severity_counts['high'] * 5
            medium_weight = severity_counts['medium'] * 2
            low_weight = severity_counts['low'] * 1
            
            total_weight = critical_weight + high_weight + medium_weight + low_weight
            security_score = max(0, min(100, 100 - total_weight))  # S'assurer que le score est entre 0 et 100
            
            # S'assurer que tous les champs requis sont présents
            try:
                scan_date = datetime.now().isoformat()
            except Exception as date_error:
                print(f"Erreur date: {str(date_error)}")
                scan_date = str(datetime.now())
            
            # Nettoyer les vulnérabilités pour éviter les problèmes de sérialisation
            cleaned_vulnerabilities = []
            for vuln in vulnerabilities:
                cleaned_vuln = {
                    'type': str(vuln.get('type', 'unknown')),
                    'severity': str(vuln.get('severity', 'low')),
                    'description': str(vuln.get('description', vuln.get('message', 'No description'))),
                    'file': str(vuln.get('file', 'unknown')),
                }
                
                # Ajouter les champs optionnels s'ils existent
                if 'line' in vuln:
                    try:
                        cleaned_vuln['line'] = int(vuln['line'])
                    except (ValueError, TypeError):
                        pass
                
                if 'code' in vuln:
                    cleaned_vuln['code'] = str(vuln['code'])[:500]  # Limiter la taille
                
                if 'code_context' in vuln:
                    cleaned_vuln['code_context'] = str(vuln['code_context'])[:1000]  # Limiter la taille
                
                cleaned_vulnerabilities.append(cleaned_vuln)
            
            report = {
                'summary': {
                    'total_vulnerabilities': total_vulns,
                    'security_score': security_score,
                    'severity_breakdown': severity_counts,
                    'scan_date': scan_date,
                    'target': str(directory)
                },
                'vulnerabilities': cleaned_vulnerabilities,
                'recommendations': self._generate_recommendations(vulnerabilities),
                'success': True
            }
            
            print(f"✅ Rapport généré: {total_vulns} vulnérabilités, score {security_score}/100")
            return report
            
        except Exception as e:
            error_msg = f'Erreur lors de la génération du rapport: {str(e)}'
            print(f"❌ {error_msg}")
            print(f"Stack trace: {traceback.format_exc()}")
            return {
                'summary': {
                    'total_vulnerabilities': 0,
                    'security_score': 0,
                    'severity_breakdown': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
                    'scan_date': datetime.now().isoformat(),
                    'target': str(directory)
                },
                'vulnerabilities': [],
                'recommendations': [],
                'error': error_msg,
                'success': False
            }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Génère des recommandations basées sur les vulnérabilités trouvées"""
        recommendations = []
        
        vuln_types = set(vuln.get('type', '') for vuln in vulnerabilities)
        
        if 'sql_injection' in vuln_types:
            recommendations.append("Utilisez des requêtes préparées pour éviter les injections SQL")
        
        if 'xss' in vuln_types:
            recommendations.append("Validez et échappez toutes les entrées utilisateur")
        
        if 'hardcoded_secrets' in vuln_types:
            recommendations.append("Déplacez les secrets vers des variables d'environnement")
        
        if 'insecure_crypto' in vuln_types:
            recommendations.append("Utilisez des algorithmes de chiffrement sécurisés (SHA-256, AES)")
        
        return recommendations
    
    def _get_severity(self, vuln_type: str) -> str:
        """Retourne la sévérité pour un type de vulnérabilité"""
        severity_map = {
            'sql_injection': 'critical',
            'xss': 'high',
            'hardcoded_secrets': 'high',
            'insecure_crypto': 'medium',
            'vulnerable_dependency': 'medium'
        }
        
        return severity_map.get(vuln_type, 'low')
    
    def _get_description(self, vuln_type: str) -> str:
        """Retourne la description pour un type de vulnérabilité"""
        descriptions = {
            'sql_injection': 'Injection SQL potentielle détectée',
            'xss': 'Vulnérabilité XSS potentielle détectée',
            'hardcoded_secrets': 'Secret en dur détecté dans le code',
            'insecure_crypto': 'Algorithme de chiffrement non sécurisé',
            'vulnerable_dependency': 'Dépendance avec vulnérabilités connues'
        }
        
        return descriptions.get(vuln_type, 'Vulnérabilité détectée')
