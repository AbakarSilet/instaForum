from django import template
from django.db.models import Count
from forum.models import Thread, Post
from modelUser.models import User

register = template.Library()

@register.inclusion_tag('includes/navbar_top_contributors.html')
def show_top_contributors():
    top_thread_authors = Thread.objects.values('author__username', 'author__profile_image', 'author_id') \
                                       .annotate(count=Count('id')) \
                                       .order_by('-count')[:2]
    top_post_authors = Post.objects.values('author__username', 'author__profile_image', 'author_id') \
                                   .annotate(count=Count('id')) \
                                   .order_by('-count')[:2]

    # Ajouter les objets User complets avec les images de profil et les comptes
    top_thread_authors = [{
        'user': User.objects.get(id=author['author_id']),
        'count': author['count']
    } for author in top_thread_authors]
    top_post_authors = [{
        'user': User.objects.get(id=author['author_id']),
        'count': author['count']
    } for author in top_post_authors]

    return {
        'top_thread_authors': top_thread_authors,
        'top_post_authors': top_post_authors
    }
