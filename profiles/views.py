# profiles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.userprofile
    return render(request, 'profiles/profile_view.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profiles/profile_edit.html', {'form': form})
