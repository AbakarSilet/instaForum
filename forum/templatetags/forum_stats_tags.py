from django import template
from django.db.models import Count
from forum.models import Thread, Post
from modelUser.models import User

register = template.Library()

@register.inclusion_tag('includes/navbar_forum_stats.html')
def show_forum_stats():
    forum_count = Thread.objects.values('subforum_id').distinct().count()
    member_count = User.objects.count()
    post_count = Post.objects.count()
    thread_count = Thread.objects.count()
    online_members_count = 10  # Placeholder: You would replace this with actual online users count logic
    
    return {
        'forum_count': forum_count,
        'member_count': member_count,
        'total_messages_count': post_count + thread_count,
        'online_members_count': online_members_count,
    }
