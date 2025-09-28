import csv

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

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
