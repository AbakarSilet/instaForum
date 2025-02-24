
import datetime
from time import timezone
import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404

from django.core.paginator import Paginator
import requests
from newsapi import NewsApiClient
from .models import NewsArticle, NewsSource
import logging
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import NewsArticle, NewsSource
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from .models import NewsArticle, NewsSource
from .forms import NewsArticleForm

import pytz

import requests


def get_news(request):
    api_key = settings.NEWS_API_KEY  # Assure-toi que cette clé API est correcte
    language = 'en'  # Définit la langue des nouvelles (en pour anglais)
    
    categories = ['technology', 'science', 'health']  # Ajoute les catégories que tu veux récupérer
    all_news = []

    for category in categories:
        url = f'https://newsapi.org/v2/top-headlines?language={language}&category={category}&apiKey={api_key}'
        response = requests.get(url)
        news = response.json()
        
        if 'articles' in news:
            all_news.extend(news['articles'])
    
    return render(request, 'news/news.html', {'news': all_news})


logger = logging.getLogger(__name__)



def collect_news(request):
    source_name = request.GET.get('source')  # Récupération de la source depuis les paramètres GET
    articles = NewsArticle.objects.filter(is_active=True)
    
    if source_name:
        source = get_object_or_404(NewsSource, name=source_name)
        articles = articles.filter(source=source)  # Filtrage par source

    articles = articles.order_by('-published_at')
    
    paginator = Paginator(articles, 20)  # 20 articles par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Récupération des sources distinctes
    sources = NewsSource.objects.all().order_by('name')

    context = {
        'articles': page_obj,
        'error': None if articles.exists() else "Aucun article trouvé.",
        'last_updated': articles.first().created_at if articles.exists() else None,
        'sources_count': articles.values('source').distinct().count(),
        'sources': sources
    }
    
    return render(request, 'news/yahoonews.html', context)



def news_from_source(request, source_name):
    source = get_object_or_404(NewsSource, name=source_name)
    articles = NewsArticle.objects.filter(source=source, is_active=True).order_by('-published_at')
    
    paginator = Paginator(articles, 20)  # 20 articles par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'articles': page_obj,
        'error': None if articles.exists() else "Aucun article trouvé pour cette source.",
        'last_updated': articles.first().created_at if articles.exists() else None,
        'source': source.name,
    }
    
    return render(request, 'news/news_from_source.html', context)



def create_news(request):
    if not request.user.is_moderator:
        return HttpResponse('Unauthorized', status=401)

    # Get or create the "Moderation" source
    moderation_source, created = NewsSource.objects.get_or_create(name='Insta')

    if request.method == 'POST':
        form = NewsArticleForm(request.POST)
        if form.is_valid():
            news_article = form.save(commit=False)
            news_article.source = moderation_source
            news_article.published_at = timezone.now()
            news_article.save()
            return redirect('home')  # Redirection vers la liste d'articles (remplacez par le nom de la vue correcte)
    else:
        form = NewsArticleForm()
    
    return render(request, 'news/create_news.html', {'form': form})

