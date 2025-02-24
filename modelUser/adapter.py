from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        return '/' # Rediriger vers la page d'accueil après la connexion

    def get_signup_redirect_url(self, request):
        return '/accounts/confirm-email/' # Rediriger vers la page de confirmation d'email après l'inscription
