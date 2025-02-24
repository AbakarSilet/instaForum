from .models import NewsArticle, NewsSource
import logging

logger = logging.getLogger(__name__)

def save_articles_to_db(articles):
    for article in articles:
        try:
            if not NewsArticle.objects.filter(url=article['url'], published_at=article['published_at']).exists():
                news_source, created = NewsSource.objects.get_or_create(name=article['source']['name'])

                news_article = NewsArticle(
                    title=article['title'],
                    description=article['description'],
                    url=article['url'],
                    image_url=article.get('urlToImage', ''),
                    source=news_source,
                    published_at=article['published_at'],
                    category=article.get('category', 'Général'),
                    views_count=0,
                    is_active=True
                )
                news_article.save()
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'article: {str(e)}")
