# signals.py
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.shortcuts import redirect


# @receiver(user_signed_up)
# def user_signed_up_handler(request, user, **kwargs):
#     # Redirection vers la page de confirmation d'email
#     return redirect('/accounts/confirm-email/')  # Assurez-vous que cela correspond à l'URL correcte

# from allauth.account.signals import user_logged_in
# from django.dispatch import receiver
# from django.contrib.auth.models import User

# @receiver(user_logged_in)
# def save_google_profile(sender, request, user, **kwargs):
#     social_account = user.socialaccount_set.filter(provider='google').first()
#     if social_account:
#         user.profile.picture = social_account.extra_data['picture']
#         user.profile.save()
