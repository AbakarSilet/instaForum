import requests
from django.conf import settings

def get_news():
    api_key = settings.NEWS_API_KEY
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['articles']
    return []
