
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from taggit.models import Tag
from django.contrib import messages
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from forum.utils import remove_accents
from modelUser.models import User
from .models import Category, Notification, Report, Subforum, Thread, Post, Like, Dislike, UserBadge
from .forms import ThreadFormCreate, ThreadForm,ReportForm,PostForm, SearchForm,ThreadFormUpdate,PostFormUpdate
from django.utils.translation import gettext as _


from django.core.exceptions import PermissionDenied
from allauth.account.decorators import verified_email_required



def subforum_view(request, slug):
    subforum = get_object_or_404(Subforum, slug=slug)
    threads = subforum.threads.all()
    active_user = request.user.is_active
    return render(request, 'forum/subforum.html', {'subforum': subforum, 'threads': threads, 'active_user': active_user})



@login_required
def add_post_view(request, thread_id):
    if request.method == 'POST':
        thread = get_object_or_404(Thread, id=thread_id)
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.thread = thread
            
            # Normalisation du contenu
            content = form.cleaned_data['content']
            quoted_text = request.POST.get('quoted_text', '')
            translated_string = str(_('Réponse à @'))  # Convertit l'objet __proxy__ en chaîne de caractères
            if not content.startswith(translated_string):
                if quoted_text:
                    post.content = f"{quoted_text}\n\n{content}"
                else:
                    post.content = content
            
            post.save()
            
            # Normaliser les tags
            raw_tags = form.cleaned_data.get('tags')
            normalized_tags = [remove_accents(tag) for tag in raw_tags]
            post.tags.set(normalized_tags)
            
            if post.author and thread.author != request.user:
                Notification.objects.create(
                    user=thread.author,
                    message=f'{request.user.username} a commente votre thread {thread.title}.',
                    link =reverse('forum:thread', kwargs={'slug':thread.slug} ))
                
            return redirect('forum:thread', slug=thread.slug)
        else:
            return render(request, 'forum/thread.html', {'thread': thread, 'form': form})
    return redirect('forum:thread', slug=thread.slug)


@login_required
@permission_required('forum.delete_thread', raise_exception=True)
def delete_thread_view(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    subforum_slug = thread.subforum.slug
    thread.delete()
    return redirect('forum:subforum', slug=subforum_slug)


@login_required
def first_thread_congrats(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    return render(request, 'forum/first_thread_congrats.html', {'thread': thread})

@verified_email_required
@login_required
def create_thread(request):
    if request.method == 'POST':
        form = ThreadFormCreate(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()

            # Normaliser les tags avant de les ajouter
            raw_tags = form.cleaned_data.get('tags')
            normalized_tags = [remove_accents(tag) for tag in raw_tags]
            thread.tags.set(normalized_tags)

            # Vérifier si c'est le premier thread de l'utilisateur
            if Thread.objects.filter(author=request.user).count() == 1:
                return redirect('forum:first_thread_congrats', slug=thread.slug)
            else:
                return redirect('forum:thread', slug=thread.slug)
        else:
            messages.error(request, 'Veuillez remplir tous les champs requis.')

    else:
        form = ThreadFormCreate()
        
    return render(request, 'forum/create.html', {'form': form})


@verified_email_required
@login_required
def create_thread_view(request, slug):
    subforum = get_object_or_404(Subforum, slug=slug)

    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.subforum = subforum
            thread.author = request.user
            if request.user.is_active:
                thread.save()
            else:
                messages.error(request, 'Vous n\'etes plus active ')
            
            # Normaliser les tags avant de les ajouter
            raw_tags = form.cleaned_data.get('tags')
            normalized_tags = [remove_accents(tag) for tag in raw_tags]
            thread.tags.set(normalized_tags)
            
            if Thread.objects.filter(author=request.user).count() == 1:
                return redirect('forum:first_thread_congrats', slug=thread.slug)
            else:
                return redirect('forum:thread', slug=thread.slug)
    else:
        form = ThreadForm()
    return render(request, 'forum/create_thread.html', {'form': form, 'subforum': subforum})



def forum_home_view(request):
    form = SearchForm(request.GET or None)
    query = None
    results = []
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        search_vector = SearchVector('title', 'description') + SearchVector('threads__title', 'threads__content') + SearchVector('threads__posts__content', 'threads__posts__author__username')
        search_query = SearchQuery(query)

        results = Category.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')

    categories = Category.objects.prefetch_related('subforums__threads__posts').all()

    subforums_data = []
    category_authors = {category.id: set() for category in categories}  # Dictionnaire pour stocker les auteurs uniques par catégorie

    for category in categories:
        for subforum in category.subforums.all():
            threads_count = subforum.threads.count()
            subforum_views = 0
            for thread in subforum.threads.all():
                subforum_views += thread.view_count
                for thread in subforum.threads.all():
                    category_authors[category.id].add(thread.author)  # Ajouter l'auteur au set de la catégorie
            view_count = subforum_views
            posts_count = sum(thread.posts.count() for thread in subforum.threads.all())
            subforums_data.append({
                'subforum': subforum,
                'threads_count': threads_count,
                'view_count': view_count,
                'posts_count': posts_count,
            })

    return render(request, 'forum/home.html', {
        'categories': categories,
        'subforums_data': subforums_data,
        'form': form,
        'query': query,
        'results': results,
        'category_authors': category_authors,  # Passer les auteurs uniques par catégorie
    })


@login_required
def search_view(request):
    query = request.GET.get('query')
    search_results = []

    if query:
        thread_vector = SearchVector('title', 'slug', 'subforum__title', 'author__username', weight='A')
        post_vector = SearchVector('content', 'author__username', weight='A')
        search_query = SearchQuery(query)
        
        thread_results = (
            Thread.objects.annotate(rank=SearchRank(thread_vector, search_query))
            .filter(rank__gte=0.3)
            .order_by('-rank')
        )
        post_results = (
            Post.objects.annotate(rank=SearchRank(post_vector, search_query))
            .filter(rank__gte=0.3)
            .order_by('-rank')
        )

        subforum_results = Subforum.objects.filter(title__icontains=query)
        user_results = User.objects.filter(username__icontains=query)

        search_results += [{'type': 'thread', 'object': result} for result in thread_results]
        search_results += [{'type': 'post', 'object': result} for result in post_results]
        search_results += [{'type': 'subforum', 'object': result} for result in subforum_results]
        search_results += [{'type': 'user', 'object': result} for result in user_results]

    # Pagination des résultats de recherche
    paginator = Paginator(search_results, 5)  # 10 résultats par page
    page = request.GET.get('page')

    try:
        paginated_results = paginator.page(page)
    except PageNotAnInteger:
        paginated_results = paginator.page(1)
    except EmptyPage:
        paginated_results = paginator.page(paginator.num_pages)

    categories = Category.objects.prefetch_related('subforums__threads__posts').all()
    subforums_data = []
    for category in categories:
        for subforum in category.subforums.all():
            threads_count = subforum.threads.count()
            subforum_Views = 0
            for thread in subforum.threads.all():
                subforum_Views += thread.view_count
            view_count = subforum_Views
            posts_count = sum(thread.posts.count() for thread in subforum.threads.all())
            subforums_data.append({
                'subforum': subforum,
                'threads_count': threads_count,
                'view_count': view_count,
                'posts_count': posts_count,
            })

    return render(request, 'forum/home.html', {
        'query': query,
        'search_results': paginated_results,
        'categories': categories,
        'subforums_data': subforums_data
    })


@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    threads = Thread.objects.filter(author=user)
    # posts = Post.objects.filter(author=user)
    user_badges = UserBadge.objects.filter(user=user)
    
    return render(request, 'forum/profile.html', {
        'profile_user': user,
        'threads': threads,
        # 'posts': posts,
        'user_badges': user_badges,
    })

def tagged(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    threads = Thread.objects.filter(tags__in=[tag])
    posts = Post.objects.filter(tags__in=[tag])

    return render(request, 'forum/tagged.html', {
        'tag': tag,
        'threads': threads,
        'posts': posts,
    })

from django.db.models import Count

@login_required
def thread_view(request, slug):
    thread = get_object_or_404(Thread, slug=slug)
    thread.view_count += 1
    thread.save()
    posts_list = thread.posts.all().order_by('-created_at')
    user_liked = False
    
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, thread=thread).exists()

    # Pagination reste identique
    paginator = Paginator(posts_list, 4)
    page = request.GET.get('page', 1)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Déterminer le numéro de page pour chaque post
    for index, post in enumerate(posts_list):
        post.page_number = (index // paginator.per_page) + 1

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            form.save_m2m()  # Sauvegarder les tags
            
            # Ajouter un message de confirmation
            messages.success(request, _('Votre message a été publié avec succès !'))
            
            # Rediriger vers la dernière page pour voir le nouveau post
            last_page = paginator.num_pages + 1  # +1 car on vient d'ajouter un post
            return redirect(f'{reverse("forum:thread", kwargs={"slug": thread.slug})}?page={last_page}#post-{post.id}')
    else:
        form = PostForm()

    # Reste du code inchangé
    threads_tag_ids = thread.tags.values_list('id', flat=True)
    similar_threads = Thread.objects.filter(
        tags__in=threads_tag_ids,
        subforum=thread.subforum
    ).exclude(id=thread.id)
    similar_threads = similar_threads.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags')[:5]


    return render(request, 'forum/thread.html', {
        'thread': thread,
        'posts': posts,
        'user_liked': user_liked,
        'form': form,
        'similar_threads': similar_threads,
    })



@login_required
@csrf_exempt
def like_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    liked = False
    
    # Vérifier si le like existe déjà
    like = Like.objects.filter(user=request.user, thread=thread).first()
    
    if like:
        # Si le like existe, le supprimer
        like.delete()
    else:
        # Sinon, créer un nouveau like
        Like.objects.create(user=request.user, thread=thread)
        liked = True
        
        # Créer une notification pour le like
        if thread.author != request.user:
            Notification.objects.create(
                user=thread.author,
                message=f'{request.user.username} a aimé votre thread "{thread.title}".',
                link=reverse('forum:thread', kwargs={'slug': thread.slug})
            )
    
    return JsonResponse({
        'liked': liked,
        'total_likes': thread.like_set.count()
    })

@login_required
@csrf_exempt
def dislike_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    disliked = False
    
    # Vérifier si le dislike existe déjà
    dislike = Dislike.objects.filter(user=request.user, thread=thread).first()
    
    if dislike:
        # Si le dislike existe, le supprimer
        dislike.delete()
    else:
        # Sinon, créer un nouveau dislike
        Dislike.objects.create(user=request.user, thread=thread)
        disliked = True
    
    return JsonResponse({
        'disliked': disliked,
        'total_dislikes': thread.dislike_set.count()
    })


@login_required
@permission_required('forum.delete_post', raise_exception=True)
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('forum:moderation_dashboard')

@login_required
@permission_required('forum.delete_thread', raise_exception=True)
def delete_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    thread.delete()
    return redirect('forum:moderation_dashboard')

@login_required
def report_view(request, report_type, item_id):
    if report_type == 'thread':
        item = get_object_or_404(Thread, id=item_id)
        reported_username = None
    elif report_type == 'post':
        item = get_object_or_404(Post, id=item_id)
        reported_username = None
    elif report_type == 'reported_user':
        item = get_object_or_404(User, id=item_id)
        reported_username = f"{item.first_name} {item.last_name}"
    else:
        return redirect('forum:home')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            if report_type == 'thread':
                report.thread = item
            elif report_type == 'reported_user':
                report.reported_user = item
            else:
                report.post = item
            report.save()
            
            # Création de notifications pour les modérateurs
            moderator_group = Group.objects.get(name='Moderator')
            moderators = User.objects.filter(groups=moderator_group)
            
            if report_type == 'thread':
                message = f"Nouveau signalement d'un sujet: {item.title}"
                link = reverse('forum:thread', args=[item.slug])
            elif report_type == 'post':
                message = f"Nouveau signalement d'un message dans le sujet: {item.thread.title}"
                link = reverse('forum:thread', args=[item.thread.slug])
            elif report_type == 'reported_user':
                message = f"Nouveau signalement d'un utilisateur: {item.username}"
                link = reverse('forum:moderation_dashboard')
            
            # Créer une notification pour chaque modérateur
            for moderator in moderators:
                Notification.objects.create(
                    user=moderator,
                    message=message,
                    link=link
                )

            if report_type == 'reported_user':
                return redirect('forum:profile', username=report.reported_user.username)
            else:
                return redirect('forum:thread', slug=item.thread.slug if report_type == 'post' else item.slug)
    else:
        form = ReportForm()
    
    return render(request, 'forum/report.html', {'form': form, 'item': item, 'report_type': report_type, 'reported_username':reported_username})


@login_required
def suspend_user(request, user_id):
    # Vérifier si l'utilisateur est connecté
    if not request.user.is_authenticated:
        return HttpResponseForbidden("Vous devez être connecté.")
    
    # Récupérer l'utilisateur à suspendre
    user_to_suspend = get_object_or_404(User, id=user_id)
    
    # Récupérer le groupe Moderator
    try:
        moderator_group = Group.objects.get(name='Moderator')
    except Group.DoesNotExist:
        return HttpResponseForbidden("Le groupe Modérateur n'existe pas.")
    
    # Vérifications des permissions
    if (
        # Vérifier si l'utilisateur est un superutilisateur
        request.user.is_superuser or 
        # Vérifier si l'utilisateur appartient au groupe Moderator
        moderator_group in request.user.groups.all()
    ):
        # Vérifier qu'un modérateur ne peut pas se suspendre lui-même
        if request.user.id == user_to_suspend.id:
            return HttpResponseForbidden("Vous ne pouvez pas vous suspendre vous-même.")
        
        # Suspension de l'utilisateur
        user_to_suspend.is_active = False
        user_to_suspend.save()
        
        # Créer une notification pour l'utilisateur suspendu
        Notification.objects.create(
            user=user_to_suspend,
            message="Votre compte a été suspendu par un modérateur. Veuillez contacter l'administration pour plus d'informations.",
            link=reverse('forum:home')
        )
        
        return redirect('forum:moderation_dashboard')
    else:
        # Accès non autorisé
        return HttpResponseForbidden("Vous n'avez pas la permission de suspendre des utilisateurs.")
    
@verified_email_required
@login_required
def moderation_dashboard(request):
    if not request.user.is_moderator():
        raise PermissionDenied("Vous n'avez pas les droits nécessaires pour accéder à cette page.")
    reported_threads = Thread.objects.filter(report__isnull=False).annotate(report_count=Count('report'))
    reported_posts = Post.objects.filter(report__isnull=False).annotate(report_count=Count('report'))
    reported_users = User.objects.filter(report__isnull=False).annotate(report_count=Count('report'))
    
    inactive_users_count = reported_users.filter(is_active=False).count()
    reports = Report.objects.all()  # Récupérer tous les signalements

    return render(request, 'forum/moderation_dashboard.html', {
        'reported_threads': reported_threads,
        'reported_posts': reported_posts,
        'reported_users': reported_users,
        'inactive_users_count': inactive_users_count,
        'reports': reports,
    })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    return render(request, 'forum/notifications.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('forum:notifications')

@login_required
def get_notification_count(request):
    notification_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {'notification_count': notification_count}

@login_required
def update_thread(request, slug):
    thread = get_object_or_404(Thread, slug=slug)

    # Vérifier que l'utilisateur est l'auteur du thread
    if thread.author != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier ce thread.")

    if request.method == 'POST':
        form = ThreadFormUpdate(request.POST, request.FILES, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('forum:thread', slug=thread.slug)
    else:
        form = ThreadFormUpdate(instance=thread)

    return render(request, 'forum/update_thread.html', {'form': form, 'thread': thread})

@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    thread = post.thread  # Récupérer le thread associé

    # Vérifier que l'utilisateur est l'auteur du post
    if post.author != request.user:
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier ce post.")

    if request.method == 'POST':
        form = PostFormUpdate(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('forum:thread', slug=thread.slug)
    else:
        form = PostFormUpdate(instance=post)

    return render(request, 'forum/update_post.html', {'form': form, 'post': post, 'thread': thread})



