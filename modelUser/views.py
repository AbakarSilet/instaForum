from allauth.account.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm, EditUserProfileForm

def messageshome(request):
    context = {
        'user_profile_image': request.user.profile_image if request.user.is_authenticated and request.user.profile_image else 'default_profile.png'
    }
    return render(request, 'base.html', context)


@login_required
def profile_view(request):
    user = request.user
    form = UserProfileForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user': user})

@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('account_profile')
    else:
        form = EditUserProfileForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})


class CustomPasswordChangeView(PasswordChangeView):
    def get_success_url(self):
        messages.success(self.request, "Votre mot de passe a été changé avec succès!")
        return reverse_lazy('account_profile') 