from django.test import TestCase
from events.models import Event, Participant


class ModelTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(title="Test Event", date="2025-01-01", description="Test description")
        self.participant = Participant.objects.create(name="Max Mustermann", email="max@a.com", event=self.event)

    def test_event_creation(self):
        self.assertEqual(str(self.event), self.event.title, "Test Event")
        self.assertEqual(self.event.date, "2025-01-01")

    def test_participant_creation(self):
        self.assertEqual(str(self.participant), self.participant.name, "Max Mustermann")
        self.assertEqual(self.participant.email, "max@a.com")
        self.assertEqual(self.participant.event, self.event)

    def test_event_has_participant(self):
        participants = self.event.participant_set.all()
        self.assertEqual(participants.count(), 1)
        self.assertEqual(participants[0].name, "Max Mustermann")
