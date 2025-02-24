from django import forms
from allauth.account.forms import LoginForm, SignupForm, ResetPasswordForm, SetPasswordForm,ChangePasswordForm
from django.utils.translation import gettext_lazy as _

from modelUser.models import User

class CustomLoginForm(LoginForm):
    remember = forms.BooleanField(required=False, label=_("Se souvenir de moi"))

    def login(self, *args, **kwargs):
        # Si la case "Se souvenir de moi" est cochée, prolonger la session
        remember = self.cleaned_data.get('remember')
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 jours
        else:
            self.request.session.set_expiry(0)  # La session expire à la fermeture du navigateur
        return super().login(*args, **kwargs)

class CustomSignupForm(SignupForm):
    username = forms.CharField(
        max_length=150,
        required=False,
        label=_("Nom d'utilisateur"),
        widget=forms.TextInput(attrs={'placeholder': _("Nom d'utilisateur")})
    )
    email = forms.EmailField(
        required=True,
        label=_("Adresse e-mail"),
        widget=forms.EmailInput(attrs={'placeholder': _("Adresse e-mail")})
    )
    first_name = forms.CharField(
        max_length=100,
        label=_("Prénom"),
        widget=forms.TextInput(attrs={'placeholder': _("Prénom")})
    )
    last_name = forms.CharField(
        max_length=100,
        label=_("Nom"),
        widget=forms.TextInput(attrs={'placeholder': _("Nom")})
    )
    profile_image = forms.ImageField(
        label=_("Image de profil"),
        required=False,
        widget=forms.FileInput()
    )
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={'placeholder': _("Mot de passe")})
    )
    password2 = forms.CharField(
        label=_("Confirmer le mot de passe"),
        widget=forms.PasswordInput(attrs={'placeholder': _("Confirmer le mot de passe")})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = _("Adresse e-mail")

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        if user.username:
            user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if 'profile_image' in self.cleaned_data:
            user.profile_image = self.cleaned_data['profile_image']
        user.role = 'User'  # Assigner le rôle "Utilisateur" par défaut
        user.save()
        return user

class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Entrez votre adresse e-mail')
        })


# Nouveau formulaire pour le changement de mot de passe (quand l'utilisateur est connecté)
class CustomChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oldpassword'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ancien mot de passe'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmez le nouveau mot de passe'
        })

# Nouveau formulaire pour définir un nouveau mot de passe (après réinitialisation)
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmez le mot de passe'
        })

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_image']
        labels = {
            'username': _('Nom d\'utilisateur'),
            'email': _('Adresse e-mail'),
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'profile_image': _('Image de profil'),
            
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        
        }

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'profile_image',]
        labels = {
            'username': _('Nom d\'utilisateur'),
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'profile_image': _('Image de profil'),
            
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control input-container'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control input-container'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control input-container'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            
        }
