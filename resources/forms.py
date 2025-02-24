from django import forms
from .models import Resource
from django.utils.translation import gettext_lazy as _

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'resource_type', 'image', 'link', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file', None)
        if file and file.size > 25 * 1024 * 1024:  # 25 MB
            raise forms.ValidationError ("File size must be under 50MB")
        return file
