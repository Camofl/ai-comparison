from django.test import TestCase
from django.contrib import admin
from events.models import Event, Participant
from events.admin import EventAdmin, ParticipantInline


class EventAdminTest(TestCase):

    def setUp(self):
        self.event = Event.objects.create(title="Test Event", date="2025-01-01", description="Test description")
        self.event_admin = EventAdmin(Event, admin.site)

    def test_participant_names_three_participants(self):
        for i in range(1, 4):
            Participant.objects.create(
                name=f"Participant {i}",
                email=f"p{i}@example.com",
                event=self.event
            )

        result = self.event_admin.participant_names(self.event)
        expected = "Participant 1, Participant 2, Participant 3"
        self.assertEqual(result, expected)

    def test_participant_names_more_than_three_participants(self):
        for i in range(1, 5):
            Participant.objects.create(
                name=f"Participant {i}",
                email=f"p{i}@example.com",
                event=self.event
            )

        result = self.event_admin.participant_names(self.event)
        expected = "Participant 1, Participant 2, Participant 3, ..."
        self.assertEqual(result, expected)
