import csv

from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .forms import EventForm, ParticipantFormSet
from .models import Event


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


from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView
from .models import Post
from .forms import PostForm


class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    ordering = ["-created_at"]


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/edit_post.html"
    context_object_name = "post"

    def get_success_url(self):
        return reverse_lazy("post_list")

    def get_context_data(self, **kwargs):
        """Include all posts in context to mimic old behavior"""
        context = super().get_context_data(**kwargs)
        context["all_posts"] = Post.objects.all().order_by("-created_at")
        return context


from django.db.models import Count


def user_list(request):
    users = (
        User.objects.annotate(posts_count=Count('post'))
        .filter(is_active=True, email__contains='@')
        .exclude(email__isnull=True)
        .exclude(email__exact='')
    )

    user_data = [
        {
            'user': user,
            'posts_count': user.posts_count,
            'is_active_user': user.posts_count > 0,
        }
        for user in users
        if len(user.email) > 5
    ]

    total_active = User.objects.filter(is_active=True).count()

    context = {
        'users': user_data,
        'total_active': total_active,
        'user_count': len(user_data),
    }
    return render(request, 'posts/user_list.html', context)
