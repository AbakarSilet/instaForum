from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Event
from django.utils import timezone

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'date', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Titre de l\'événement')}),
            'description': forms.Textarea(attrs={'placeholder': _('Description de l\'événement')}),
            'location': forms.TextInput(attrs={'placeholder': _('Lieu de l\'événement')}),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'placeholder': _('Date de l\'événement')}),
            'image': forms.FileInput(attrs={'placeholder': _('Image de l\'événement')}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now():
            raise forms.ValidationError(_("La date de l'événement ne peut pas être dans le passé."))
        return date
