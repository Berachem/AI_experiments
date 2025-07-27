from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import json
from datetime import datetime
from pathlib import Path

class PDFReportGenerator:
    """Générateur de rapports PDF pour les analyses de sécurité"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50')
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            textColor=colors.HexColor('#34495E')
        )
        
    def generate_pdf_report(self, scan_data: dict, output_path: str) -> bool:
        """Génère un rapport PDF complet"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Page de titre
            story.extend(self._create_title_page(scan_data))
            story.append(PageBreak())
            
            # Résumé exécutif
            story.extend(self._create_executive_summary(scan_data))
            story.append(PageBreak())
            
            # Graphiques et statistiques
            story.extend(self._create_charts_section(scan_data))
            story.append(PageBreak())
            
            # Détail des vulnérabilités
            story.extend(self._create_vulnerabilities_section(scan_data))
            
            # Recommandations
            if scan_data.get('recommendations'):
                story.append(PageBreak())
                story.extend(self._create_recommendations_section(scan_data))
            
            # Construire le PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Erreur génération PDF: {str(e)}")
            return False
    
    def _create_title_page(self, scan_data: dict) -> list:
        """Crée la page de titre"""
        story = []
        
        # Titre principal
        story.append(Paragraph("🔍 Security Analysis Report", self.title_style))
        story.append(Spacer(1, 30))
        
        # Informations générales
        summary = scan_data.get('summary', {})
        
        info_data = [
            ['Target', summary.get('target', 'N/A')],
            ['Scan Date', self._format_date(summary.get('scan_date'))],
            ['Security Score', f"{summary.get('security_score', 0)}/100"],
            ['Total Vulnerabilities', str(summary.get('total_vulnerabilities', 0))]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 50))
        
        # Score de sécurité visuel
        score = summary.get('security_score', 0)
        score_color = self._get_score_color(score)
        
        score_style = ParagraphStyle(
            'ScoreStyle',
            fontSize=48,
            alignment=TA_CENTER,
            textColor=score_color
        )
        
        story.append(Paragraph(f"Security Score: {score}/100", score_style))
        story.append(Spacer(1, 20))
        
        # Statut
        status = self._get_security_status(score)
        status_style = ParagraphStyle(
            'StatusStyle',
            fontSize=18,
            alignment=TA_CENTER,
            textColor=score_color
        )
        story.append(Paragraph(status, status_style))
        
        return story
    
    def _create_executive_summary(self, scan_data: dict) -> list:
        """Crée le résumé exécutif"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.heading_style))
        
        summary = scan_data.get('summary', {})
        severity_breakdown = summary.get('severity_breakdown', {})
        
        # Tableau des sévérités
        severity_data = [
            ['Severity Level', 'Count', 'Percentage'],
            ['Critical', str(severity_breakdown.get('critical', 0)), 
             f"{self._calculate_percentage(severity_breakdown.get('critical', 0), summary.get('total_vulnerabilities', 1))}%"],
            ['High', str(severity_breakdown.get('high', 0)),
             f"{self._calculate_percentage(severity_breakdown.get('high', 0), summary.get('total_vulnerabilities', 1))}%"],
            ['Medium', str(severity_breakdown.get('medium', 0)),
             f"{self._calculate_percentage(severity_breakdown.get('medium', 0), summary.get('total_vulnerabilities', 1))}%"],
            ['Low', str(severity_breakdown.get('low', 0)),
             f"{self._calculate_percentage(severity_breakdown.get('low', 0), summary.get('total_vulnerabilities', 1))}%"]
        ]
        
        severity_table = Table(severity_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(severity_table)
        story.append(Spacer(1, 20))
        
        # Analyse textuelle
        analysis_text = self._generate_analysis_text(scan_data)
        story.append(Paragraph(analysis_text, self.styles['Normal']))
        
        return story
    
    def _create_charts_section(self, scan_data: dict) -> list:
        """Crée la section graphiques"""
        story = []
        
        story.append(Paragraph("Visual Analysis", self.heading_style))
        
        summary = scan_data.get('summary', {})
        severity_breakdown = summary.get('severity_breakdown', {})
        
        # Graphique en secteurs des sévérités
        if sum(severity_breakdown.values()) > 0:
            pie_chart = self._create_severity_pie_chart(severity_breakdown)
            story.append(pie_chart)
            story.append(Spacer(1, 30))
        
        return story
    
    def _create_vulnerabilities_section(self, scan_data: dict) -> list:
        """Crée la section détaillée des vulnérabilités"""
        story = []
        
        story.append(Paragraph("Detailed Vulnerabilities", self.heading_style))
        
        vulnerabilities = scan_data.get('vulnerabilities', [])
        
        if not vulnerabilities:
            story.append(Paragraph("✅ No vulnerabilities detected!", self.styles['Normal']))
            return story
        
        # Grouper par sévérité
        grouped_vulns = {}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            if severity not in grouped_vulns:
                grouped_vulns[severity] = []
            grouped_vulns[severity].append(vuln)
        
        # Afficher par ordre de sévérité
        severity_order = ['critical', 'high', 'medium', 'low']
        
        for severity in severity_order:
            if severity not in grouped_vulns:
                continue
                
            # En-tête de sévérité
            severity_title = f"{severity.upper()} Severity ({len(grouped_vulns[severity])} issues)"
            story.append(Paragraph(severity_title, self.heading_style))
            
            # Table des vulnérabilités
            vuln_data = [['Type', 'File', 'Description']]
            
            for vuln in grouped_vulns[severity]:
                vuln_data.append([
                    vuln.get('type', 'Unknown').replace('_', ' ').title(),
                    self._truncate_path(vuln.get('file', 'N/A')),
                    self._truncate_text(vuln.get('description', vuln.get('message', 'No description')), 60)
                ])
            
            vuln_table = Table(vuln_data, colWidths=[1.5*inch, 2*inch, 3*inch])
            vuln_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self._get_severity_color(severity)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(vuln_table)
            story.append(Spacer(1, 20))
        
        return story
    
    def _create_recommendations_section(self, scan_data: dict) -> list:
        """Crée la section des recommandations"""
        story = []
        
        story.append(Paragraph("Security Recommendations", self.heading_style))
        
        recommendations = scan_data.get('recommendations', [])
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
            story.append(Spacer(1, 10))
        
        return story
    
    def _create_severity_pie_chart(self, severity_breakdown: dict) -> Drawing:
        """Crée un graphique en secteurs pour les sévérités"""
        drawing = Drawing(400, 200)
        
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        # Données
        data = []
        labels = []
        colors_list = []
        
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_breakdown.get(severity, 0)
            if count > 0:
                data.append(count)
                labels.append(f"{severity.title()}: {count}")
                colors_list.append(self._get_severity_color(severity))
        
        pie.data = data
        pie.labels = labels
        pie.slices.strokeColor = colors.white
        pie.slices.strokeWidth = 2
        
        for i, color in enumerate(colors_list):
            pie.slices[i].fillColor = color
        
        drawing.add(pie)
        return drawing
    
    def _get_severity_color(self, severity: str) -> colors.Color:
        """Retourne la couleur pour une sévérité donnée"""
        color_map = {
            'critical': colors.HexColor('#DC3545'),
            'high': colors.HexColor('#FD7E14'),
            'medium': colors.HexColor('#FFC107'),
            'low': colors.HexColor('#20C997')
        }
        return color_map.get(severity, colors.gray)
    
    def _get_score_color(self, score: int) -> colors.Color:
        """Retourne la couleur pour un score de sécurité"""
        if score >= 80:
            return colors.HexColor('#28A745')
        elif score >= 60:
            return colors.HexColor('#FFC107')
        elif score >= 40:
            return colors.HexColor('#FD7E14')
        else:
            return colors.HexColor('#DC3545')
    
    def _get_security_status(self, score: int) -> str:
        """Retourne le statut de sécurité basé sur le score"""
        if score >= 80:
            return "🛡️ EXCELLENT SECURITY"
        elif score >= 60:
            return "⚠️ GOOD SECURITY"
        elif score >= 40:
            return "🔶 POOR SECURITY"
        else:
            return "🚨 CRITICAL SECURITY ISSUES"
    
    def _format_date(self, date_str: str) -> str:
        """Formate une date pour l'affichage"""
        try:
            if isinstance(date_str, str):
                # Essayer de parser différents formats
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    dt = datetime.fromtimestamp(float(date_str))
            else:
                dt = datetime.fromtimestamp(float(date_str))
            return dt.strftime("%B %d, %Y at %H:%M")
        except:
            return str(date_str)
    
    def _calculate_percentage(self, count: int, total: int) -> int:
        """Calcule le pourcentage"""
        if total == 0:
            return 0
        return round((count / total) * 100)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Tronque un texte à une longueur maximale"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _truncate_path(self, path: str) -> str:
        """Tronque un chemin de fichier"""
        if len(path) <= 30:
            return path
        return "..." + path[-27:]
    
    def _generate_analysis_text(self, scan_data: dict) -> str:
        """Génère un texte d'analyse automatique"""
        summary = scan_data.get('summary', {})
        total_vulns = summary.get('total_vulnerabilities', 0)
        score = summary.get('security_score', 0)
        severity_breakdown = summary.get('severity_breakdown', {})
        
        if total_vulns == 0:
            return "This security analysis found no vulnerabilities in the scanned code. The target appears to follow security best practices and shows no immediate security concerns."
        
        critical_count = severity_breakdown.get('critical', 0)
        high_count = severity_breakdown.get('high', 0)
        
        analysis = f"This security analysis identified {total_vulns} potential security issue{'s' if total_vulns > 1 else ''} "
        analysis += f"resulting in a security score of {score}/100. "
        
        if critical_count > 0:
            analysis += f"There {'are' if critical_count > 1 else 'is'} {critical_count} critical vulnerability{'ies' if critical_count > 1 else 'y'} that require immediate attention. "
        
        if high_count > 0:
            analysis += f"Additionally, {high_count} high-severity issue{'s' if high_count > 1 else ''} should be addressed as soon as possible. "
        
        if score >= 80:
            analysis += "Overall, the security posture is excellent with minimal risk."
        elif score >= 60:
            analysis += "The security posture is generally good but improvements are recommended."
        elif score >= 40:
            analysis += "The security posture needs improvement to reduce potential risks."
        else:
            analysis += "The security posture requires immediate attention due to significant vulnerabilities."
        
        return analysis
