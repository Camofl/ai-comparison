from django.contrib import admin

from .models import Participant, Post, Event


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [ParticipantInline]
    search_fields = ["title"]
    list_display = ["title", "date", "participant_names"]

    def participant_names(self, obj):
        participants = obj.participant_set.all()
        names = [participant.name for participant in participants[:3]]
        result = ", ".join(names)
        if participants.count() > 3:
            result += ", ..."
        return result

    participant_names.short_description = "Participants"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "event"]
    list_filter = ["event"]
    search_fields = ["name"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']
