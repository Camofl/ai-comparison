import csv

from django.http import Http404
from django.http import HttpResponse

from .forms import EventForm, ParticipantFormSet
from .forms import PostForm
from .models import Event
from .models import Post


def index(request):
    events = Event.objects.order_by("date")
    return render(request, "events/index.html", {"events": events})


def event_detail(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404("Event does not exist")
    return render(request, "events/event_detail.html", {"event": event})


def event_new(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        formset = ParticipantFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            event = form.save()
            formset.instance = event
            formset.save()
            return redirect("events:event_detail", event.id)
    else:
        form = EventForm()
        formset = ParticipantFormSet()

    return render(request, "events/event_form.html", {"form": form, "formset": formset})


def event_edit(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        formset = ParticipantFormSet(request.POST, instance=event)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("events:event_detail", event_id)
    else:
        form = EventForm(instance=event)
        formset = ParticipantFormSet(instance=event)

    return render(request, "events/event_form.html", {
        "form": form,
        "formset": formset,
        "editing": True
    })


def export_event_csv(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename=event_{event_id}_participants.csv"

    writer = csv.writer(response)
    writer.writerow(["name", "email"])

    for participant in event.participant_set.all():
        writer.writerow([participant.name, participant.email])

    return response


from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    ordering = ['-created_at']


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/edit_post.html'
    success_url = reverse_lazy('events:post_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Include all posts in the edit view context
        context['all_posts'] = Post.objects.all().order_by('-created_at')
        return context


from django.db.models import Count


def user_list(request):
    # Single query with annotation - no N+1 problem
    users = User.objects.annotate(
        posts_count=Count('post')
    ).filter(
        is_active=True,
        email__isnull=False,
        email__contains='@',
        email__regex=r'.{6,}'  # At least 6 characters
    ).select_related()  # Optimize if User has foreign keys

    # Get active count efficiently
    active_count = User.objects.filter(is_active=True).count()

    # Prepare user data
    user_data = [
        {
            'user': user,
            'posts_count': user.posts_count,
            'is_active_user': user.posts_count > 0,
        }
        for user in users
    ]

    context = {
        'user_list': user_data,
        'total_active': active_count,
        'user_count': len(user_data)
    }

    return render(request, 'posts/user_list.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserForm, UserProfileForm


def profile_view(request, username):
    """Display a user's profile"""
    user = get_object_or_404(User, username=username)
    profile = user.profile

    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': request.user.is_authenticated and request.user == user
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def profile_edit(request):
    """Edit the logged-in user's profile"""
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_view', username=request.user.username)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profiles/profile_edit.html', context)
