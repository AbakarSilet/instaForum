from django import template
from forum.models import Category
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('includes/popular_categories.html')
def show_popular_categories():
    categories = Category.objects.annotate(
        num_threads=Count('subforums__threads'),
        num_posts=Count('subforums__threads__posts')
    ).order_by('-num_threads', '-num_posts')[:4]

    return {'categories': categories}
