from django.db import models
from django.utils import timezone

from modelUser.models import User

class NewsSource(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    url = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Source d'actualité"
        verbose_name_plural = "Sources d'actualités"
    
    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    title = models.CharField(max_length=2000, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    url = models.URLField(verbose_name="URL de l'article",max_length=500)
    image_url = models.URLField(blank=True, null=True, verbose_name="URL de l'image")
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, verbose_name="Source")
    published_at = models.DateTimeField(verbose_name="Date de publication")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    # Champs optionnels pour plus de fonctionnalités
    category = models.CharField(max_length=1000, blank=True, verbose_name="Catégorie")
    views_count = models.IntegerField(default=0, verbose_name="Nombre de vues")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['category']),
        ]
        # Éviter les doublons
        constraints = [
            models.UniqueConstraint(
                fields=['url', 'published_at'], 
                name='unique_article'
            )
        ]
    
    def __str__(self):
        return self.title
