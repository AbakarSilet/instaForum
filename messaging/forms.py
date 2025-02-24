from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Message

class MessageForm(forms.ModelForm):
    content = forms.CharField(
        required=True, 
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': _('Écrire votre message ici')})
    )
    
    class Meta:
        model = Message
        fields = ['content']
        labels = {
            'content': _('Message'),
        }
