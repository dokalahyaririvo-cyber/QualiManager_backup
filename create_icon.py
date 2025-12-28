# -*- coding: utf-8 -*-
"""Créer l'icône de l'application"""
from PIL import Image, ImageDraw, ImageFont
import os

# Créer le dossier assets
os.makedirs("assets", exist_ok=True)

# Créer une image 256x256 avec fond transparent
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Couleur bleue principale
blue = (33, 150, 243, 255)

# Dessiner un cercle bleu
draw.ellipse([20, 20, 236, 236], outline=blue, width=8)
draw.ellipse([80, 80, 176, 176], fill=blue)

# Ajouter la lettre Q en blanc
try:
    # Essayer avec une fonte système
    font = ImageFont.truetype("arial.ttf", 100)
except:
    # Fallback sur la fonte par défaut
    font = ImageFont.load_default()

# Dessiner le Q
bbox = draw.textbbox((0, 0), "Q", font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (256 - text_width) // 2
y = (256 - text_height) // 2 - 10

draw.text((x, y), "Q", fill=(255, 255, 255, 255), font=font)

# Sauvegarder comme ICO
img.save("assets/icon.ico", format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

print("✓ Icône créée: assets/icon.ico")
