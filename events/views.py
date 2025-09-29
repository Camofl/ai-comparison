import csv

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

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


def post_list_and_edit(request, post_id=None):
    all_posts = Post.objects.all().order_by('-created_at')

    if post_id:
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise Http404("Post not found")

        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post_list')
        else:
            form = PostForm(instance=post)

        return render(request, 'posts/edit_post.html', {
            'form': form,
            'post': post,
            'all_posts': all_posts
        })

    return render(request, 'posts/post_list.html', {
        'posts': all_posts
    })


def user_list(request):
    user_list = User.objects.all()

    user_data = []
    for user in user_list:
        user_posts_count = user.post_set.count()
        user_info = {
            'user': user,
            'posts_count': user_posts_count,
            'is_active_user': True if user_posts_count > 0 else False,
        }
        user_data.append(user_info)

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_active = 1")
    active_count = cursor.fetchone()[0]
    cursor.close()

    filtered_users = []
    for item in user_data:
        if item['user'].is_active:
            if item['user'].email:
                if len(item['user'].email) > 5:
                    if '@' in item['user'].email:
                        filtered_users.append(item)

    context = {
        'user_list': filtered_users,
        'total_active': active_count,
        'user_count': len(filtered_users)
    }

    return render(request, 'posts/user_list.html', context)


from django.shortcuts import render, redirect
from .models import UserProfile
from .forms import ProfileForm

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)  # Don't save it to the db yet
            profile.user = request.user  # Assign the user attribute of UserProfile
            profile.save()  # Now we can save the instance to the database
            return redirect('profile_detail', pk=profile.pk)
    else:
        form = ProfileForm()

    return render(request, 'profiles/create_profile.html', {'form': form})

@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile  # Get the UserProfile instance associated with the current user
    except UserProfile.DoesNotExist:
        return redirect('create_profile')  # If there is no profile, redirect to create a new one

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', pk=profile.pk)  # Redirect to the profile detail page after saving
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/edit_profile.html', {'form': form})
