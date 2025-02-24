from django import views
from django.urls import path
from .views import about, contact, custom_403, custom_404, discussions_view, faq, home, privacy, rules, send_email


urlpatterns = [
    path('',view=home,name='home'),
    path('discussions/', discussions_view, name='discussions'),
    path('404',view=custom_404,name='404'),
    path('403',view=custom_403,name='403'),
    path('faq',view=faq,name='faq'),
    path('privacy',view=privacy,name='privacy'),
    path('rules',view=rules,name='rules'),
    path('about',view=about,name='about'),
    path('contact',view=contact,name='contact'),
    path('send_email',view=send_email,name='send_email'),

]



    