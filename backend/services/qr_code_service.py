"""
Service pour la génération de QR codes pour les contribuables
"""

import qrcode
import io
import uuid
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from database.models import Contribuable


def generate_qr_code_string(contribuable_id: int) -> str:
    """
    Génère une chaîne unique pour le QR code d'un contribuable
    Format: CONT-{contribuable_id}-{uuid}
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"CONT-{contribuable_id}-{unique_id}"


def generate_qr_code_image(
    qr_data: str,
    size: int = 300,
    border: int = 4,
    include_logo: bool = False,
    logo_path: Optional[Path] = None
) -> io.BytesIO:
    """
    Génère une image QR code à partir des données
    
    Args:
        qr_data: Données à encoder dans le QR code
        size: Taille de l'image (pixels)
        border: Taille de la bordure
        include_logo: Inclure un logo au centre
        logo_path: Chemin vers le logo
    
    Returns:
        BytesIO contenant l'image PNG
    """
    # Configuration du QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Haute correction d'erreur
        box_size=10,
        border=border,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Créer l'image du QR code
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Redimensionner si nécessaire
    if size != 300:
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Ajouter un logo au centre si demandé
    if include_logo and logo_path and logo_path.exists():
        try:
            logo = Image.open(logo_path)
            # Redimensionner le logo (20% de la taille du QR code)
            logo_size = int(size * 0.2)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Calculer la position pour centrer le logo
            qr_width, qr_height = qr_img.size
            logo_x = (qr_width - logo_size) // 2
            logo_y = (qr_height - logo_size) // 2
            
            # Créer un fond blanc pour le logo
            logo_bg = Image.new('RGB', (logo_size + 10, logo_size + 10), 'white')
            logo_bg.paste(logo, (5, 5))
            
            # Coller le logo sur le QR code
            qr_img.paste(logo_bg, (logo_x - 5, logo_y - 5))
        except Exception as e:
            print(f"Erreur lors de l'ajout du logo: {e}")
    
    # Convertir en BytesIO
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def generate_qr_code_with_info(
    contribuable: Contribuable,
    size: int = 400,
    include_details: bool = True
) -> io.BytesIO:
    """
    Génère un QR code avec les informations du contribuable affichées en dessous
    
    Args:
        contribuable: Objet Contribuable
        size: Taille du QR code
        include_details: Inclure les détails du contribuable sous le QR code
    
    Returns:
        BytesIO contenant l'image PNG
    """
    # Générer le QR code
    qr_data = contribuable.qr_code or generate_qr_code_string(contribuable.id)
    qr_buffer = generate_qr_code_image(qr_data, size=size)
    qr_img = Image.open(qr_buffer)
    
    if not include_details:
        return qr_buffer
    
    # Créer une image plus grande pour inclure les détails
    padding = 40
    text_height = 120 if include_details else 0
    total_height = size + padding * 2 + text_height
    
    # Créer une nouvelle image blanche
    final_img = Image.new('RGB', (size + padding * 2, total_height), 'white')
    
    # Coller le QR code
    final_img.paste(qr_img, (padding, padding))
    
    if include_details:
        # Ajouter les informations du contribuable
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Essayer de charger une police (peut échouer si pas disponible)
            font_large = ImageFont.truetype("arial.ttf", 20) if Path("arial.ttf").exists() else ImageFont.load_default()
            font_small = ImageFont.truetype("arial.ttf", 14) if Path("arial.ttf").exists() else ImageFont.load_default()
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        y_offset = size + padding + 20
        
        # Nom du contribuable
        nom_complet = f"{contribuable.nom} {contribuable.prenom or ''}".strip()
        draw.text((padding, y_offset), nom_complet, fill='black', font=font_large)
        
        # Téléphone
        if contribuable.telephone:
            draw.text((padding, y_offset + 30), f"Tél: {contribuable.telephone}", fill='gray', font=font_small)
        
        # Numéro d'identification
        if contribuable.numero_identification:
            draw.text((padding, y_offset + 50), f"ID: {contribuable.numero_identification}", fill='gray', font=font_small)
        
        # QR Code
        draw.text((padding, y_offset + 70), f"QR: {qr_data}", fill='darkblue', font=font_small)
    
    # Convertir en BytesIO
    final_buffer = io.BytesIO()
    final_img.save(final_buffer, format='PNG')
    final_buffer.seek(0)
    
    return final_buffer

