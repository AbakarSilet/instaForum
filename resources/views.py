from django.forms import ValidationError
from django.shortcuts import render, redirect
from .models import Resource
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
import os
from django.utils.translation import gettext_lazy as _
from allauth.account.decorators import verified_email_required

def resource_list(request):
    resource_type = request.GET.get('type')
    if resource_type:
        resources = Resource.objects.filter(resource_type=resource_type).order_by('-date_added')
    else:
        resources = Resource.objects.all().order_by('-date_added')
    return render(request, 'resources/resource_list.html', {'resources': resources})



@teacher_required
@verified_email_required
@login_required
def add_image(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        image = request.FILES['image']
        
        allowed_extensions = ['jpeg', 'jpg', 'png', 'gif', 'bmp', 'tiff', 'webp']
        extension = os.path.splitext(image.name)[1][1:].lower()  # Obtenir l'extension sans le point
        
        if extension not in allowed_extensions:
            return render(request, 'resources/add_image.html', {'errors': [_('Le fichier doit être une image valide.')]})
        
        resource = Resource(user=request.user, title=title, description=description, resource_type='image', image=image)
        try:
            resource.full_clean()
            resource.save()
            return redirect('resources:resource_list')
        except ValidationError as e:
            return render(request, 'resources/add_image.html', {'errors': e.messages})
    
    return render(request, 'resources/add_image.html')

@teacher_required
@verified_email_required
@login_required
def add_link(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        link = request.POST['link']
        resource = Resource(user=request.user, title=title, description=description, resource_type='link', link=link)
        resource.save()
        return redirect('resources:resource_list')
    return render(request, 'resources/add_link.html')

@teacher_required
@verified_email_required
@login_required
def add_document(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        file = request.FILES['file']
        
        allowed_extensions = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt','xlsx','csv','odt','py','js','java','html','scss','css','json', 'xml', 'md', 'yml', 'yaml','sql', 'db', 'sqlite','zip', 'rar', 'tar.gz', '7z']

        extension = os.path.splitext(file.name)[1][1:].lower()  # Obtenir l'extension sans le point
        
        if extension not in allowed_extensions:
            return render(request, 'resources/add_document.html', {'errors': [_('Le fichier doit être un document valide.')]})
        
        resource = Resource(user=request.user, title=title, description=description, resource_type='document', file=file)
        try:
            resource.full_clean()
            resource.save()
            return redirect('resources:resource_list')
        except ValidationError as e:
            return render(request, 'resources/add_document.html', {'errors': e.messages})

    return render(request, 'resources/add_document.html')


@teacher_required
@verified_email_required
@login_required
def add_video(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        video = request.FILES['video']
        
        allowed_extensions = ['mp4', 'avi', 'mov', 'mkv', 'wmv']
        extension = os.path.splitext(video.name)[1][1:].lower()  # Obtenir l'extension sans le point
        
        if extension not in allowed_extensions:
            return render(request, 'resources/add_video.html', {'errors': [_('Le fichier doit être une vidéo valide.')]})
        
        resource = Resource(user=request.user, title=title, description=description, resource_type='video', video=video)
        try:
            resource.full_clean()
            resource.save()
            return redirect('resources:resource_list')
        except ValidationError as e:
            return render(request, 'resources/add_video.html', {'errors': e.messages})
    
    return render(request, 'resources/add_video.html')

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import Resource


@verified_email_required
@login_required
def search_resources(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        # Recherche dans les champs title, description et resource_type
        search_vector = SearchVector('title', 'description', 'resource_type')
        search_query = SearchQuery(query)

        # Utilisation de Q pour des recherches plus inclusives
        q_objects = Q(title__icontains=query) | Q(description__icontains=query) | Q(resource_type__icontains=query)
        
        # Combinaison de la recherche full-text avec la recherche basique
        results = Resource.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(
            Q(rank__gte=0.01) | q_objects
        ).order_by('-rank')

    # Passer les résultats à la template
    return render(request, 'resources/search_results.html', {'results': results, 'query': query})

from django.shortcuts import get_object_or_404, render


def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return render(request, 'resources/resource_detail.html', {'resource': resource})
