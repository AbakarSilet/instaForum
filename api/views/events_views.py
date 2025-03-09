from rest_framework import generics, permissions
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from events.models import Event, Attendee
from events.serializers import EventSerializer, AttendeeSerializer

class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all().order_by('date')  # Trier par date décroissante
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]  # Pas d'authentification requise


class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.groups.filter(name='Moderator').exists():
            raise PermissionDenied
        serializer.save(organizer=self.request.user)

class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DeleteEventAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            if event.organizer == request.user:
                event.delete()
                return Response({'detail': 'Événement supprimé avec succès.'}, status=204)
            else:
                return Response({'error': 'Permission refusée.'}, status=403)
        except Event.DoesNotExist:
            return Response({'error': 'Événement non trouvé.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class ParticipateEventAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            Attendee.objects.create(user=request.user, event=event)
            return Response({'detail': 'Participation réussie.'}, status=201)
        except Event.DoesNotExist:
            return Response({'error': 'Événement non trouvé.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class EventAttendeesAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            attendees = Attendee.objects.filter(event=event)
            serializer = AttendeeSerializer(attendees, many=True)
            return Response(serializer.data, status=200)
        except Event.DoesNotExist:
            return Response({'error': 'Événement non trouvé.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

