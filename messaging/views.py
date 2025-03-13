# messaging/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
from modelUser.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from .models import Message
from .forms import MessageForm
from allauth.account.decorators import verified_email_required


@verified_email_required
@login_required
def user_messages(request):
    user = request.user

    # Récupérer tous les utilisateurs actifs
    allUsers = User.objects.filter(is_active=True).order_by('first_name')

    messages = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by('-created_at')

    conversations = {}
    
    for message in messages:
        other_user = message.receiver if message.sender == user else message.sender
        if other_user in allUsers and other_user not in conversations:
            conversations[other_user] = message

    conversations = sorted(conversations.items(), key=lambda x: x[1].created_at, reverse=True)
    
    context = {
        'conversations': conversations, 
        'allUsers': allUsers,
        }
    return render(request, 'messaging/user_messages.html', context)



@csrf_exempt
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ).order_by('first_name')
    
    results = [
        {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image_url': user.profile_image.url,  # Récupération directe de l'URL de l'image
            'username': user.username
        }
        for user in users
    ]

    return JsonResponse(results, safe=False)


@verified_email_required
@login_required
def thread_detail(request, username):
    # Récupérer l'utilisateur de la conversation
    user = get_object_or_404(User, username=username)
    
    # Récupérer tous les messages de la conversation en une seule requête
    messages = Message.objects.select_related('sender', 'receiver').filter(
        Q(sender=request.user, receiver=user) | 
        Q(sender=user, receiver=request.user)
    ).order_by('created_at')
    
    # Récupérer toutes les conversations de l'utilisateur connecté
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values('sender', 'receiver').annotate(
        last_message_date=Max('created_at')
    ).order_by('-last_message_date')
    
    # Utiliser un dictionnaire pour stocker les conversations uniques
    conversation_users = {}
    for conv in conversations:
        # Déterminer l'autre utilisateur
        other_user_id = conv['receiver'] if conv['sender'] == request.user.id else conv['sender']
        
        # Vérifier si la conversation est déjà enregistrée
        if other_user_id not in conversation_users:
            other_user = User.objects.get(id=other_user_id)
            # Récupérer le dernier message de la conversation
            last_message = Message.objects.filter(
                Q(sender=request.user, receiver=other_user) |
                Q(sender=other_user, receiver=request.user)
            ).latest('created_at')
            
            conversation_users[other_user_id] = {
                'user': other_user,
                'last_message': last_message,
                'last_message_date': conv['last_message_date'],
                'unread_count': Message.objects.filter(
                    sender=other_user,
                    receiver=request.user,
                    is_read=False
                ).count()
            }
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            Message.objects.create(
                sender=request.user,
                receiver=user,
                content=content
            )
            return redirect('messaging:thread_detail', username=username)
    else:
        form = MessageForm()
    
    # Marquer tous les messages non lus comme lus
    Message.objects.filter(
        sender=user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    context = {
        'messages': messages,
        'form': form,
        'user': user,
        'conversations': list(conversation_users.values()),  # Convertir le dict en liste
    }
    
    return render(request, 'messaging/thread_detail.html', context)
