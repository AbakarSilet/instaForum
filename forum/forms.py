from django import forms

from forum.utils import remove_accents
from .models import Report, Subforum, Thread, Post
from taggit.forms import TagWidget
from django.utils.translation import gettext_lazy as _



class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Titre de votre fil de discussion')}),
            'content': forms.Textarea(attrs={'placeholder': _('Contenu de votre fil de discussion')}),
            'tags': TagWidget(attrs={'placeholder': _('Sélectionnez ou ajoutez des tags')}),
        }


class ThreadFormCreate(forms.ModelForm):
    subforum = forms.ModelChoiceField(
        queryset=Subforum.objects.all(),
        required=True,
        label=_('Forum'),
        widget=forms.Select(attrs={'placeholder': _('Sélectionnez un forum')})
    )

    class Meta:
        model = Thread
        fields = ['subforum', 'title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('Titre de votre fil de discussion')}),
            'content': forms.Textarea(attrs={'placeholder': _('Contenu de votre fil de discussion')}),
            'tags': TagWidget(attrs={'placeholder': _('Ajoutez des tags separés par des virgules')}),
        }


    def save(self, commit=True):
        thread = super().save(commit=False)
        if commit:
            thread.save()
            # Normaliser les tags avant de les ajouter
            raw_tags = self.cleaned_data.get('tags')
            normalized_tags = [remove_accents(tag) for tag in raw_tags]
            thread.tags.set(normalized_tags)
        return thread


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {
            'content': _('Message')
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'id': 'comment',
                'class': 'form-control',
                'placeholder': _('Écrivez votre message ici...'),
                'rows': 3
            }),
        }



class SearchForm(forms.Form):
    query = forms.CharField(label='Rechercher', max_length=255, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': _('Rechercher dans le forum...')
    }))

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'report_reason']
        labels = {
            'report_type': _('Type de signalement'),
            'report_reason': _('Raison du signalement'),
        }
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'report_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 
                                                   'placeholder': _('Expliquez la raison du signalement')}),
        }




class ThreadFormUpdate(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content', 'image', 'tags']

class PostFormUpdate(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
