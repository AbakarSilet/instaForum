from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from forum.models import Subforum, Thread,Category
from events.models import Event
from modelUser.models import User
from news.models import NewsArticle

from django.db.models import Count

def home(request):
    # Récupérer les subforums et threads
    subforums = Subforum.objects.prefetch_related('threads__posts').all()
    subforums_with_threads = []
    subforums_without_threads = []

    for subforum in subforums:
        # Annoter les threads avec le nombre de posts
        threads = subforum.threads.annotate(post_count=Count('posts')).order_by('-post_count')[:2]
        valid_threads = [thread for thread in threads if thread.slug]  # Filtrer les threads avec un slug valide
        
        if valid_threads:
            for thread in valid_threads:
                thread.top_posts = thread.posts.all()[:2]
            subforums_with_threads.append((subforum, valid_threads))
        else:
            subforums_without_threads.append(subforum)

    events = Event.objects.all().order_by('date')

    articles = NewsArticle.objects.all()[:20]
    
    context = {
        'subforums_with_threads': subforums_with_threads,
        'subforums_without_threads': subforums_without_threads,
        'events': events,
        'articles': articles
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
            'Contact InstaForum',
            message,
            user_email,  
            ['instaforum2025@gmail.com'],
        )
        return redirect('home')  
    return render(request, 'contact.html')