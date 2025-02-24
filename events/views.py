
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import EventForm
from .models import Event
from resources.decorators import *
from forum.models import Notification  # Assurez-vous que le chemin est correct

from modelUser.models import User
from .models import Event, Attendee



def event_list(request):
    today = timezone.now().date()
    next_week = today + timedelta(weeks=1)
    next_month = today + timedelta(weeks=4)

    events = Event.objects.all()
    events_this_week = events.filter(date__gte=today, date__lt=next_week).order_by('date')
    events_next_week = events.filter(date__gte=next_week, date__lt=next_month).order_by('date')
    events_next_month = events.filter(date__gte=next_month, date__lt=next_month + timedelta(weeks=4)).order_by('date')
    upcoming_events = events.filter(date__gte=next_month + timedelta(weeks=4)).order_by('date')

    return render(request, 'events/event_list.html', {
        'events_this_week': events_this_week,
        'events_next_week': events_next_week,
        'events_next_month': events_next_month,
        'upcoming_events': upcoming_events,
    })

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendees = Attendee.objects.filter(event=event)
    user_is_attending = attendees.filter(user=request.user).exists()
    return render(request, 'events/event_detail.html', {
        'event': event,
        'attendees': attendees,
        'user_is_attending': user_is_attending,
    })

@login_required
def participate(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    attendee_exists = Attendee.objects.filter(event=event, user=request.user).exists()
    
    if not attendee_exists:
        Attendee.objects.create(event=event, user=request.user)
    
    # Créer une notification pour l'organisateur de l'evenment
    user = event.organizer
    event_url = reverse('event_detail', kwargs={'event_id': event.id})

    Notification.objects.create(
        user=user,
        message=f"{request.user.first_name} {request.user.last_name} sera à votre événement",
        link=event_url
        )

    return redirect('event_detail', event_id=event.id)



@login_required
@moderator_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            # Ajouter le créateur comme participant
            Attendee.objects.create(event=event, user=request.user)
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})


