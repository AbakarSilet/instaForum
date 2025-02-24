from django import template

register = template.Library()

@register.filter
def youtube_id_resource(url):
    if 'youtube' in url:
        # Cas 1: URL standard avec v=
        if 'v=' in url:
            parts = url.split('v=')
            if len(parts) > 1:
                return parts[1].split('&')[0]  # Prendre l'ID avant un éventuel '&'
        
        # Cas 2: URL courte (ex: https://youtu.be/VIDEO_ID)
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]  # Prendre l'ID vidéo

        # Cas 3: URL qui contient d'autres paramètres
        if 'youtube.com/watch' in url:
            from urllib.parse import parse_qs, urlparse
            parsed_url = urlparse(url)
            video_id = parse_qs(parsed_url.query).get('v')
            if video_id:
                return video_id[0]  # Prendre le premier ID vidéo trouvé

    return None

@register.filter
def google_drive_preview_resource(url):
    if 'drive.google.com' in url:
        return url.replace('view', 'preview')
    return url


@register.filter(name='endswith')
def endswith(value, suffix):
    return value.endswith(suffix)
