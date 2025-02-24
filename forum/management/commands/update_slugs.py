from django.core.management.base import BaseCommand
from forum.models import Thread
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Met à jour les slugs des threads existants'

    def handle(self, *args, **kwargs):
        threads_without_slug = Thread.objects.filter(slug__isnull=True)
        threads_with_empty_slug = Thread.objects.filter(slug='')

        for thread in threads_without_slug.union(threads_with_empty_slug):
            thread.slug = slugify(thread.title)
            while Thread.objects.filter(slug=thread.slug).exists():
                thread.slug = f"{thread.slug}-{Thread.objects.filter(slug__startswith=thread.slug).count() + 1}"
            thread.save()
            self.stdout.write(self.style.SUCCESS(f'Slug mis à jour pour le thread "{thread.title}"'))
