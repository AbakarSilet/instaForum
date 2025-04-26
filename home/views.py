from django.shortcuts import render
from forum.models import Subforum, Thread
from events.models import Event
from news.models import NewsArticle

from django.db.models import Count

from django.db.models import Count, Prefetch
from django.utils import timezone

from django.views.decorators.cache import cache_page

@cache_page(60 * 15) 
def home(request):
    # 1. Événement phare (le prochain événement à venir)
    featured_event = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date').first()

    # 2. Événements à venir (les 3 prochains)
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date')[:3]

    # 3. Threads populaires (les plus actifs)
    hot_threads = Thread.objects.filter(is_closed=False).annotate(
        post_count=Count('posts'),
        
    ).select_related(
        'author',
        'subforum'
    ).prefetch_related(
        'posts'
    ).order_by(
        '-post_count'
    )[:6]  # 6 threads pour la grille 2x3

    # 4. Subforums populaires (avec le plus de threads)
    popular_subforums = Subforum.objects.annotate(
        thread_count=Count('threads'),
        post_count=Count('threads__posts')
    ).order_by(
        '-thread_count'
    )[:4]  # 4 subforums pour la grille

    # 5. Actualités importantes (les plus récentes ou marquées)
    important_news = NewsArticle.objects.filter(
        is_active=True 
    ).order_by(
        '-published_at'
    )[:4]  # 4 articles max

    context = {
        'featured_event': featured_event,
        'upcoming_events': upcoming_events,
        'hot_threads': hot_threads,
        'popular_subforums': popular_subforums,
        'important_news': important_news,
    }

    return render(request, 'home/home.html', context)

def discussions_view(request):
    threads = Thread.objects.prefetch_related('posts').all()
    subforums = Subforum.objects.all()

    # Ajouter les trois premiers posts à chaque thread et filtrer les threads sans slug
    valid_threads = []
    for thread in threads:
        if thread.slug:
            thread.top_posts = thread.posts.all()[:3]
            valid_threads.append(thread)

    return render(request, 'home/discussions.html', {
        'threads': valid_threads,
        'subforums': subforums,
    })



def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_403(request, exception):
    return render(request, '403.html', status=403)

def privacy(request):
    return render(request,'privacy_policies.html')
def faq(request):
    return render(request,'faq.html')
def rules(request):
    return render(request,'rules.html')
def about(request):
    return render(request,'about.html')
def contact(request):
    return render(request,'contact.html')


from django.core.mail import send_mail
from django.shortcuts import render, redirect

def send_email(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Envoi de l'email
        send_mail(
            'Contact depuis InstaForum',
            message,
            user_email,  
            ['instaforum2025@gmail.com'],
        )
        return redirect('home')  
    return render(request, 'contact.html')