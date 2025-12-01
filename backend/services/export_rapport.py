"""
Service pour l'export des rapports en CSV et PDF
"""

import csv
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def format_decimal(value: Decimal) -> str:
    """Formate un Decimal en string avec séparateur de milliers"""
    if value is None:
        return "0,00"
    # Convertir en float pour le formatage
    val = float(value)
    # Formater avec séparateur de milliers (espace) et virgule pour les décimales
    formatted = f"{val:,.2f}"
    # Remplacer la virgule des milliers par un espace et le point décimal par une virgule
    parts = formatted.split('.')
    integer_part = parts[0].replace(',', ' ')
    decimal_part = parts[1] if len(parts) > 1 else '00'
    return f"{integer_part},{decimal_part}"


def generate_csv_rapport(rapport_data: Dict[str, Any], filename: Optional[str] = None) -> io.BytesIO:
    """
    Génère un fichier CSV à partir des données du rapport
    """
    # Utiliser StringIO pour écrire le texte, puis convertir en BytesIO
    text_output = io.StringIO()
    
    # Écrire le BOM UTF-8 pour Excel
    text_output.write('\ufeff')
    
    writer = csv.writer(text_output, delimiter=';', lineterminator='\n')
    
    # En-tête avec informations de l'application
    writer.writerow(['=' * 80])
    writer.writerow(['RAPPORT DE COLLECTE - MAIRIE DE LIBREVILLE'])
    writer.writerow(['Système de Gestion des Taxes Municipales'])
    writer.writerow(['=' * 80])
    writer.writerow(['Généré le', datetime.now().strftime('%d/%m/%Y à %H:%M:%S')])
    
    # Ajouter la période si disponible
    if rapport_data.get('date_debut') or rapport_data.get('date_fin'):
        date_debut = rapport_data.get('date_debut', 'N/A')
        date_fin = rapport_data.get('date_fin', 'N/A')
        writer.writerow(['Période', f"Du {date_debut} au {date_fin}"])
    
    writer.writerow([])
    writer.writerow(['-' * 80])
    writer.writerow([])
    
    # Statistiques générales
    stats = rapport_data.get('statistiques_generales', {})
    writer.writerow(['STATISTIQUES GÉNÉRALES'])
    writer.writerow(['Total collecté', format_decimal(stats.get('total_collecte', Decimal('0')))])
    writer.writerow(['Nombre de transactions', stats.get('nombre_transactions', 0)])
    writer.writerow(['Moyenne par transaction', format_decimal(stats.get('moyenne_par_transaction', Decimal('0')))])
    writer.writerow(['Collecteurs actifs', stats.get('nombre_collecteurs_actifs', 0)])
    writer.writerow(['Taxes actives', stats.get('nombre_taxes_actives', 0)])
    writer.writerow(['Transactions aujourd\'hui', stats.get('transactions_aujourd_hui', 0)])
    writer.writerow(['Collecte aujourd\'hui', format_decimal(stats.get('collecte_aujourd_hui', Decimal('0')))])
    writer.writerow(['Transactions ce mois', stats.get('transactions_ce_mois', 0)])
    writer.writerow(['Collecte ce mois', format_decimal(stats.get('collecte_ce_mois', Decimal('0')))])
    writer.writerow([])
    
    # Collecte par moyen de paiement
    collecte_moyen = rapport_data.get('collecte_par_moyen', [])
    if collecte_moyen:
        writer.writerow(['COLLECTE PAR MOYEN DE PAIEMENT'])
        writer.writerow(['Moyen de paiement', 'Montant total', 'Nombre de transactions', 'Pourcentage (%)'])
        for item in collecte_moyen:
            writer.writerow([
                item.get('moyen_paiement', ''),
                format_decimal(item.get('montant_total', Decimal('0'))),
                item.get('nombre_transactions', 0),
                f"{item.get('pourcentage', 0):.2f}"
            ])
        writer.writerow([])
    
    # Top collecteurs
    top_collecteurs = rapport_data.get('top_collecteurs', [])
    if top_collecteurs:
        writer.writerow(['TOP COLLECTEURS'])
        writer.writerow(['Nom', 'Prénom', 'Montant total', 'Nombre de transactions'])
        for item in top_collecteurs:
            writer.writerow([
                item.get('collecteur_nom', ''),
                item.get('collecteur_prenom', ''),
                format_decimal(item.get('montant_total', Decimal('0'))),
                item.get('nombre_transactions', 0)
            ])
        writer.writerow([])
    
    # Top taxes
    top_taxes = rapport_data.get('top_taxes', [])
    if top_taxes:
        writer.writerow(['TOP TAXES'])
        writer.writerow(['Nom', 'Code', 'Montant total', 'Nombre de transactions'])
        for item in top_taxes:
            writer.writerow([
                item.get('taxe_nom', ''),
                item.get('taxe_code', ''),
                format_decimal(item.get('montant_total', Decimal('0'))),
                item.get('nombre_transactions', 0)
            ])
        writer.writerow([])
    
    # Évolution temporelle
    evolution = rapport_data.get('evolution_temporelle', [])
    if evolution:
        writer.writerow(['ÉVOLUTION TEMPORELLE'])
        writer.writerow(['Période', 'Montant total', 'Nombre de transactions'])
        for item in evolution:
            writer.writerow([
                item.get('periode', ''),
                format_decimal(item.get('montant_total', Decimal('0'))),
                item.get('nombre_transactions', 0)
            ])
    
    # Pied de page
    writer.writerow([])
    writer.writerow(['-' * 80])
    writer.writerow(['Mairie de Libreville - Gabon'])
    writer.writerow(['Système de Gestion des Taxes Municipales'])
    writer.writerow(['=' * 80])
    
    # Convertir StringIO en BytesIO
    text_content = text_output.getvalue()
    output = io.BytesIO()
    output.write(text_content.encode('utf-8-sig'))  # utf-8-sig inclut le BOM
    output.seek(0)
    return output


def get_logo_path() -> Optional[Path]:
    """
    Retourne le chemin du logo s'il existe
    """
    import os
    # Chercher le logo dans différents emplacements possibles
    base_dir = Path(__file__).parent.parent  # Remonter au dossier backend
    
    # Chemins relatifs depuis le dossier backend
    possible_paths = [
        Path("static/logo_app.png"),
        Path("static/logo.png"),
        Path("uploads/logo_app.png"),
        Path("uploads/logo.png"),
        # Chemins absolus depuis le dossier backend
        base_dir / "static" / "logo_app.png",
        base_dir / "static" / "logo.png",
        base_dir / "uploads" / "logo_app.png",
        base_dir / "uploads" / "logo.png",
        # Chemin depuis le frontend (si accessible)
        base_dir.parent / "e_taxe_back_office" / "public" / "assets" / "logo" / "logo_app.png",
        base_dir.parent / "e_taxe_back_office" / "public" / "assets" / "logo" / "logo.png",
        # Chemin alternatif
        Path(__file__).parent.parent.parent / "e_taxe_back_office" / "public" / "assets" / "logo" / "logo_app.png",
    ]
    
    for path in possible_paths:
        try:
            # Si le chemin est relatif, le rendre relatif au dossier backend
            if not path.is_absolute():
                abs_path = (base_dir / path).resolve()
            else:
                abs_path = path.resolve()
            
            if abs_path.exists() and abs_path.is_file():
                print(f"✅ Logo trouvé à: {abs_path}")
                return abs_path
        except Exception as e:
            continue
    
    # Si aucun logo n'est trouvé, afficher les chemins testés
    print("⚠️ Aucun logo trouvé. Chemins testés:")
    for path in possible_paths[:5]:  # Limiter l'affichage
        try:
            if not path.is_absolute():
                abs_path = (base_dir / path).resolve()
            else:
                abs_path = path.resolve()
            print(f"  - {abs_path} (existe: {abs_path.exists()})")
        except:
            pass
    
    return None


def generate_pdf_rapport(rapport_data: Dict[str, Any], filename: Optional[str] = None) -> io.BytesIO:
    """
    Génère un fichier PDF à partir des données du rapport avec logo
    """
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c5282'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Contenu du document
    story = []
    
    # En-tête avec logo et titre
    logo_path = get_logo_path()
    
    # Créer une table pour l'en-tête avec logo et texte côte à côte
    if logo_path and logo_path.exists():
        try:
            # Obtenir le chemin absolu du logo
            if hasattr(logo_path, 'resolve'):
                logo_str = str(logo_path.resolve())
            else:
                logo_str = str(logo_path)
            
            print(f"📷 Tentative de chargement du logo depuis: {logo_str}")
            
            # Charger l'image avec gestion d'erreur
            try:
                logo = Image(logo_str, width=1.5*inch, height=1.5*inch, preserveAspectRatio=True)
                print(f"✅ Logo chargé avec succès: {logo_str}")
                
                # Créer un tableau pour aligner le logo et le texte
                header_cell = [
                    [logo, Paragraph("RAPPORT DE COLLECTE<br/><span style='font-size:14pt; color:#2c5282;'>Mairie de Libreville</span>", title_style)]
                ]
                header_table = Table(header_cell, colWidths=[2*inch, 4.5*inch])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                story.append(header_table)
                print("✅ Logo ajouté avec succès dans l'en-tête")
            except Exception as img_error:
                print(f"❌ Erreur lors du chargement de l'image: {img_error}")
                import traceback
                traceback.print_exc()
                raise img_error
        except Exception as e:
            import traceback
            print(f"❌ Erreur lors du chargement du logo: {e}")
            traceback.print_exc()
            # Fallback sans logo
            title = Paragraph("RAPPORT DE COLLECTE", title_style)
            story.append(title)
            story.append(Paragraph("Mairie de Libreville", styles['Heading2']))
    else:
        # Pas de logo, afficher juste le titre
        print("⚠️ Logo non trouvé, utilisation du titre sans logo")
        title = Paragraph("RAPPORT DE COLLECTE", title_style)
        story.append(title)
        story.append(Paragraph("Mairie de Libreville", styles['Heading2']))
    
    story.append(Spacer(1, 0.1*inch))
    
    # Informations de génération
    info_text = f"<b>Généré le:</b> {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
    if rapport_data.get('date_debut') or rapport_data.get('date_fin'):
        date_debut = rapport_data.get('date_debut', 'N/A')
        date_fin = rapport_data.get('date_fin', 'N/A')
        info_text += f"<br/><b>Période:</b> Du {date_debut} au {date_fin}"
    story.append(Paragraph(info_text, normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Statistiques générales
    stats = rapport_data.get('statistiques_generales', {})
    story.append(Paragraph("STATISTIQUES GÉNÉRALES", heading_style))
    
    stats_data = [
        ['Indicateur', 'Valeur'],
        ['Total collecté', format_decimal(stats.get('total_collecte', Decimal('0'))) + ' FCFA'],
        ['Nombre de transactions', str(stats.get('nombre_transactions', 0))],
        ['Moyenne par transaction', format_decimal(stats.get('moyenne_par_transaction', Decimal('0'))) + ' FCFA'],
        ['Collecteurs actifs', str(stats.get('nombre_collecteurs_actifs', 0))],
        ['Taxes actives', str(stats.get('nombre_taxes_actives', 0))],
        ['Transactions aujourd\'hui', str(stats.get('transactions_aujourd_hui', 0))],
        ['Collecte aujourd\'hui', format_decimal(stats.get('collecte_aujourd_hui', Decimal('0'))) + ' FCFA'],
        ['Transactions ce mois', str(stats.get('transactions_ce_mois', 0))],
        ['Collecte ce mois', format_decimal(stats.get('collecte_ce_mois', Decimal('0'))) + ' FCFA'],
    ]
    
    stats_table = Table(stats_data, colWidths=[4*inch, 3*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Collecte par moyen de paiement
    collecte_moyen = rapport_data.get('collecte_par_moyen', [])
    if collecte_moyen:
        story.append(Paragraph("COLLECTE PAR MOYEN DE PAIEMENT", heading_style))
        
        moyen_data = [['Moyen de paiement', 'Montant total', 'Transactions', 'Pourcentage (%)']]
        for item in collecte_moyen:
            moyen_data.append([
                item.get('moyen_paiement', ''),
                format_decimal(item.get('montant_total', Decimal('0'))) + ' FCFA',
                str(item.get('nombre_transactions', 0)),
                f"{item.get('pourcentage', 0):.2f}%"
            ])
        
        moyen_table = Table(moyen_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
        moyen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c529c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(moyen_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Top collecteurs
    top_collecteurs = rapport_data.get('top_collecteurs', [])
    if top_collecteurs:
        story.append(PageBreak())
        story.append(Paragraph("TOP COLLECTEURS", heading_style))
        
        collecteurs_data = [['Nom', 'Prénom', 'Montant total', 'Transactions']]
        for item in top_collecteurs:
            collecteurs_data.append([
                item.get('collecteur_nom', ''),
                item.get('collecteur_prenom', ''),
                format_decimal(item.get('montant_total', Decimal('0'))) + ' FCFA',
                str(item.get('nombre_transactions', 0))
            ])
        
        collecteurs_table = Table(collecteurs_data, colWidths=[2*inch, 2*inch, 2*inch, 1*inch])
        collecteurs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c529c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(collecteurs_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Top taxes
    top_taxes = rapport_data.get('top_taxes', [])
    if top_taxes:
        story.append(Paragraph("TOP TAXES", heading_style))
        
        taxes_data = [['Nom', 'Code', 'Montant total', 'Transactions']]
        for item in top_taxes:
            taxes_data.append([
                item.get('taxe_nom', ''),
                item.get('taxe_code', ''),
                format_decimal(item.get('montant_total', Decimal('0'))) + ' FCFA',
                str(item.get('nombre_transactions', 0))
            ])
        
        taxes_table = Table(taxes_data, colWidths=[2.5*inch, 1.5*inch, 2*inch, 1*inch])
        taxes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c529c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(taxes_table)
        story.append(Spacer(1, 0.3*inch))
    
    # Évolution temporelle
    evolution = rapport_data.get('evolution_temporelle', [])
    if evolution:
        story.append(PageBreak())
        story.append(Paragraph("ÉVOLUTION TEMPORELLE", heading_style))
        
        evolution_data = [['Période', 'Montant total', 'Transactions']]
        for item in evolution[:30]:  # Limiter à 30 pour éviter les pages trop longues
            evolution_data.append([
                item.get('periode', ''),
                format_decimal(item.get('montant_total', Decimal('0'))) + ' FCFA',
                str(item.get('nombre_transactions', 0))
            ])
        
        evolution_table = Table(evolution_data, colWidths=[2*inch, 3*inch, 2*inch])
        evolution_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c529c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(evolution_table)
    
    # Pied de page avec logo
    story.append(Spacer(1, 0.5*inch))
    
    # Ligne de séparation
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 0.2*inch))
    
    # Pied de page avec informations
    footer_text = f"""
    <b>Mairie de Libreville - Gabon</b><br/>
    Système de Gestion des Taxes Municipales<br/>
    Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
    """
    
    if logo_path and logo_path.exists():
        try:
            # Obtenir le chemin absolu du logo
            if hasattr(logo_path, 'resolve'):
                logo_str = str(logo_path.resolve())
            else:
                logo_str = str(logo_path)
            
            footer_logo = Image(logo_str, width=0.8*inch, height=0.8*inch, preserveAspectRatio=True)
            footer_cell = [
                [footer_logo, Paragraph(footer_text, ParagraphStyle(
                    'FooterStyle',
                    parent=normal_style,
                    fontSize=8,
                    textColor=colors.HexColor('#64748b'),
                    alignment=TA_LEFT
                ))]
            ]
            footer_table = Table(footer_cell, colWidths=[1*inch, 5.5*inch])
            footer_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(footer_table)
        except Exception as e:
            print(f"Erreur lors du chargement du logo pour le pied de page: {e}")
            story.append(Paragraph(footer_text, ParagraphStyle(
                'FooterStyle',
                parent=normal_style,
                fontSize=8,
                textColor=colors.HexColor('#64748b'),
                alignment=TA_CENTER
            )))
    else:
        story.append(Paragraph(footer_text, ParagraphStyle(
            'FooterStyle',
            parent=normal_style,
            fontSize=8,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER
        )))
    
    # Construire le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

