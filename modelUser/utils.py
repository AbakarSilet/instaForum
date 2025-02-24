from PIL import Image, ImageDraw, ImageFont
import os
import random

def generate_random_color():
    """Génère une couleur aléatoire qui n'est pas blanche."""
    while True:
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if color != (255, 255, 255):
            return color

def generate_profile_image(initials, output_path):
    # Générer une couleur de fond aléatoire
    background_color = generate_random_color()
    # Créer une image carrée de 100x100 pixels avec une couleur de fond
    img = Image.new('RGB', (100, 100), color=background_color)
    # Créer un objet dessin pour ajouter du texte à l'image
    d = ImageDraw.Draw(img)
    # Définir une police et une taille
    font_path = os.path.join('static', 'fonts', 'Roboto-Bold.ttf')  # Chemin vers le fichier de police
    font = ImageFont.truetype(font_path, 50)
    # Trouver la taille du texte pour centrer correctement les lettres
    text_width, text_height = d.textbbox((0, 0), initials, font=font)[2:]
    # Calculer les positions x et y pour centrer le texte
    position = ((100 - text_width) / 2, (100 - text_height) / 2)
    # Ajouter les lettres à l'image
    d.text(position, initials, fill=(255, 255, 255), font=font)
    # Sauvegarder l'image
    img.save(output_path)
