from django.test import TestCase

from events.models import Event, Participant
from events.forms import ParticipantFormSet


class ParticipantFormSetTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(title="Test Event", date="2025-01-01", description="Test description")
        self.participant = Participant.objects.create(name="Max Mustermann", email="max@a.com", event=self.event)

    def test_empty_participant_form_raises_error(self):
        data = {
            "participant_set-TOTAL_FORMS": "2",
            "participant_set-INITIAL_FORMS": "0",
            "participant_set-MIN_NUM_FORMS": "0",
            "participant_set-MAX_NUM_FORMS": "5",
            "participant_set-0-name": "",
            "participant_set-0-email": "",
            "participant_set-1-name": "",
            "participant_set-1-email": "",
        }
        formset = ParticipantFormSet(data, instance=self.event)
        self.assertFalse(formset.is_valid())
        self.assertIn("Please enter at least one participant.", formset.non_form_errors())

    def test_duplicate_emails_raise_error(self):
        data = {
            "participant_set-TOTAL_FORMS": "2",
            "participant_set-INITIAL_FORMS": "0",
            "participant_set-MIN_NUM_FORMS": "0",
            "participant_set-MAX_NUM_FORMS": "5",
            "participant_set-0-name": "Max",
            "participant_set-0-email": "MAX@a.com",
            "participant_set-1-name": "Maxi",
            "participant_set-1-email": "max@a.com",
        }
        formset = ParticipantFormSet(data, instance=self.event)
        self.assertFalse(formset.is_valid())
        self.assertIn("Duplicate email addresses are not allowed.", formset.non_form_errors())
