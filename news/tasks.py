from celery import shared_task
from datetime import datetime, timedelta
from django.conf import settings
import pytz
from newsapi import NewsApiClient
import logging
from .models import NewsSource, NewsArticle

logger = logging.getLogger(__name__)

@shared_task
def fetch_and_store_news():
    logger.info("Début de l'exécution de fetch_and_store_news")
    NEWS_API_KEY = settings.NEWS_API_KEY 
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)
    paris_timezone = pytz.timezone('Europe/Paris')
    today = datetime.now(paris_timezone)

    all_articles = []

    # Sources générales (peut être élargies ou réduites selon les préférences)
    sources = [
        'google-news-fr',
        'africa',
        'tchad',
        'alwidha',
        'le-monde',
        'les-echos',
        'science-et-vie',
        'futura-sciences',
        'sciences-et-avenir',
    ]

    # Mots-clés avec priorité sur l'Afrique et le Tchad, et exclusion des jeux/techno/téléphones
    keywords = [
        'Chad OR Africa OR Central Africa',  # Priorité Afrique et Tchad
        'Tchad OR Afrique OR Afrique centrale',
        'science OR scientifique OR recherche',
        'technologie OR innovation OR tech -jeu -jeu vidéo -smartphone -téléphone',  # Exclure les jeux et téléphones
        'santé OR médecine OR découverte médicale',
        'environnement OR climat OR écologie',
        'espace OR astronomie',
        'intelligence artificielle OR robotique',
        'Afrique OR Afrique politique',
    ]

    # Récupération par mots-clés
    for query in keywords:
        try:
            keyword_news = newsapi.get_everything(
                q=query,
                language='fr',
                from_param=(today - timedelta(days=7)).strftime('%Y-%m-%d'),
                to=today.strftime('%Y-%m-%d'),
                sort_by='publishedAt',
                page_size=10
            )
            all_articles.extend(keyword_news.get('articles', []))
        except Exception as e:
            logger.error(f"Erreur pour la recherche '{query}': {str(e)}")
            continue

    # Récupération par catégories (on conserve les catégories pertinentes)
    categories = ['science', 'technology', 'health']
    for category in categories:
        try:
            category_news = newsapi.get_top_headlines(
                category=category,
                country='fr',
                language='fr',
                page_size=10
            )
            all_articles.extend(category_news.get('articles', []))
        except Exception as e:
            logger.error(f"Erreur pour la catégorie {category}: {str(e)}")
            continue

    # Recherche spécifique pour les magazines scientifiques
    science_magazines_query = """
        ("Sciences et Avenir" OR "Science et Vie" OR "Pour la Science" OR 
         "Futura Sciences" OR "Science Post" OR "National Geographic" OR
         "Scientific American" OR "Nature" OR "Science") AND (découverte OR recherche OR étude)
    """
    try:
        science_news = newsapi.get_everything(
            q=science_magazines_query,
            language='fr',
            from_param=(today - timedelta(days=30)).strftime('%Y-%m-%d'),
            to=today.strftime('%Y-%m-%d'),
            sort_by='publishedAt',
            page_size=15
        )
        all_articles.extend(science_news.get('articles', []))
    except Exception as e:
        logger.error(f"Erreur pour la recherche science: {str(e)}")

    # Élimination des doublons basée sur l'URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    # Stockage dans la base de données
    for article in unique_articles:
        try:
            if not article.get('title') or not article.get('description'):
                logger.warning(f"Article sans titre ou description: {article.get('url')}")
                continue

            source, created = NewsSource.objects.get_or_create(name=article['source']['name'], defaults={'url': article['source'].get('url')})

            title = article.get('title', '')[:1000]
            description = article.get('description', '')
            image_url = article.get('urlToImage')
            published_at_str = article['publishedAt']
            published_at = datetime.strptime(published_at_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)

            NewsArticle.objects.get_or_create(url=article['url'], defaults={
                'title': title,
                'description': description,
                'image_url': image_url,
                'source': source,
                'published_at': published_at,
                'category': article.get('category', ''),
            })
            logger.info(f"Article ajouté: {article['title']}")

        except Exception as e:
            logger.exception(f"Erreur lors du stockage d'un article: {article.get('url', 'URL inconnue')} - {str(e)}")

    logger.info(f"Récupération et stockage des actualités terminés. {len(unique_articles)} articles traités.")
    logger.info("Fin de l'exécution de fetch_and_store_news")
