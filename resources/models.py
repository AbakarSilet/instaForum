from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('image', 'Image'),
        ('link', 'Link'),
        ('document', 'Document'),
        ('video', 'Video'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    image = models.ImageField(upload_to='resources/images/', blank=True, null=True,validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'])])
    link = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='resources/documents/', blank=True, null=True)
    video = models.FileField(upload_to='resources/videos/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)



    def clean(self):
        max_file_size = 20 * 1024 * 1024  # 20 Mo
        if self.image and self.image.size > max_file_size:
            raise ValidationError( _("La taille de l'image ne doit pas dépasser 20 Mo. Vous pouvez partager le lien vers la ressource"))
        if self.file and self.file.size > max_file_size:
            raise ValidationError (_("La taille du fichier ne doit pas dépasser 20 Mo. Vous pouvez partager le lien vers la ressource"))
        if self.video and self.video.size > max_file_size:
            raise ValidationError (_("La taille de la vidéo ne doit pas dépasser 20 Mo. Vous pouvez partager le lien vers la ressource"))

    