#c2128e64745045fea6a864c102aba6d7   api key de news api

#app forum
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager



from forum.utils import normalize_tags, remove_accents
USER = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image =models.ImageField(blank=True, null=True)
    description = models.CharField(max_length=999, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # Vérifie l'unicité du slug
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")

    def __str__(self):
        return self.name

class Subforum(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subforums')
    title = models.CharField(max_length=200)  # Unique title within category
    description = models.TextField(blank=False, null=False)
    slug = models.SlugField(max_length=300,unique=True, blank=True)
    view_count = models.IntegerField(default=0)  # Added view count
    image = models.ImageField(verbose_name=_('image du forum'),blank=True, null=True ,upload_to='forums_images/')

    class Meta:
        unique_together = ['category', 'title']  # Enforce unique title per category
        verbose_name = _("Forum")
        verbose_name_plural = _("Forums")

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Gestion des doublons
            while Subforum.objects.filter(slug=self.slug).exists():
                self.slug += str(Subforum.objects.filter(slug__startswith=self.slug).count() + 1)
        super().save(*args, **kwargs)


class Thread(models.Model):
    id = models.AutoField(primary_key=True) 
    subforum = models.ForeignKey(Subforum, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(USER, on_delete=models.CASCADE)
    image =models.ImageField(blank=True, null=True,upload_to='forum/images/',)
    title = models.CharField(max_length=255)
    content = models.TextField()
    slug = models.SlugField(max_length=300, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(USER, related_name='thread_likes', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    tags = TaggableManager(blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Thread")
        verbose_name_plural = _("Threads")
       

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Gestion des doublons
            while Thread.objects.filter(slug=self.slug).exists():
                self.slug += str(Thread.objects.filter(slug__startswith=self.slug).count() + 1)
        super().save(*args, **kwargs)


        # Vérification et normalisation des tags
        if hasattr(self, 'tags'):
            try:
                # Récupérer les tags existants
                existing_tags = list(self.tags.names())
                
                # Normaliser les tags
                normalized_tags = [remove_accents(tag) for tag in existing_tags]
                
                # Réinitialiser les tags
                self.tags.clear()
                self.tags.add(*normalized_tags)
            except Exception as e:
                # Logging de l'erreur
                print(f"Erreur lors de la normalisation des tags : {e}")

    def get_absolute_url(self):
        return reverse('forum:thread', kwargs={'slug': self.slug})

    def total_likes(self):
        return self.likes.count()
    
class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(USER, on_delete=models.CASCADE)
    content = models.TextField()
    likes = models.ManyToManyField(USER, related_name='post_likes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta: 
        ordering = ['created_at'] 
        verbose_name = _("Post") 
        verbose_name_plural = _("Posts") 

    def __str__(self): 
        return self.content[:50]
    
    def save(self, *args, **kwargs):
        # Sauvegarde initiale
        super().save(*args, **kwargs)
        
        
    def total_likes(self):
        return self.likes.count() 
    
           
class Report(models.Model):
    REPORT_CHOICES = [
        ('SPAM', _('Spam')),
        ('OFFENSIVE', _('Offensant')),
        ('PUBLICITY', _('Publicité')),
        ('OTHER', _('Autre')),
    ]
    
    reported_by = models.ForeignKey(USER, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=REPORT_CHOICES)
    report_reason = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    reported_user = models.ForeignKey(USER, on_delete=models.CASCADE, null=True, blank=True, related_name="reported_users")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} by {self.reported_by}"

class Like(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'thread')

class Dislike(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'thread')


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Notification(models.Model):
    user = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f'Notification pour {self.user.username} - {self.message}'


