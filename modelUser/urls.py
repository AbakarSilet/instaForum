from django.urls import path
from .views import CustomPasswordChangeView, edit_profile_view, profile_view

urlpatterns = [
    path('profile/', profile_view, name='account_profile'),
    path('profile/edit/', edit_profile_view, name='account_edit'),
    path('accounts/password/change/', 
         CustomPasswordChangeView.as_view(), 
         name='account_change_password'),

]