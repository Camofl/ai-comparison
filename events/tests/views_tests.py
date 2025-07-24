from django.test import TestCase
from django.urls import reverse
from events.models import Event, Participant


class ViewsTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(title="Test Event", date="2025-01-01", description="Test description")
        self.participant = Participant.objects.create(name="Max Mustermann", email="max@a.com", event=self.event)

    def test_index_view(self):
        response = self.client.get(reverse("events:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/index.html")

    def test_event_detail_view_valid(self):
        response = self.client.get(reverse("events:event_detail", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_detail.html")

    def test_event_detail_view_invalid(self):
        response = self.client.get(reverse("events:event_detail", args=[99999]))
        self.assertEqual(response.status_code, 404)

    def test_event_new_view_get(self):
        response = self.client.get(reverse("events:event_new"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_form.html")

    def test_event_new_view_post(self):
        url = reverse("events:event_new")
        data = {
            "title": "Test Event2",
            "date": "2025-01-01",
            "description": "Test description",

            "participant_set-TOTAL_FORMS": "5",
            "participant_set-INITIAL_FORMS": "0",
            "participant_set-MIN_NUM_FORMS": "0",
            "participant_set-MAX_NUM_FORMS": "1000",

            "participant_set-0-name": "Max Mustermann",
            "participant_set-0-email": "max@a.com",
            "participant_set-0-DELETE": "",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title="Test Event2").exists())

    def test_event_edit_view_get(self):
        response = self.client.get(reverse("events:event_edit", args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "events/event_form.html")

    def test_event_edit_view_post(self):
        url = reverse("events:event_edit", args=[self.event.id])
        data = {
            "title": "Edited Event",
            "date": "2025-01-02",
            "description": "Edited description",

            "participant_set-TOTAL_FORMS": "5",
            "participant_set-INITIAL_FORMS": "0",
            "participant_set-MIN_NUM_FORMS": "0",
            "participant_set-MAX_NUM_FORMS": "1000",

            "participant_set-0-name": "Max Mustermann",
            "participant_set-0-email": "max.mustermann@example.com",
            "participant_set-0-DELETE": "",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)

        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Edited Event")
        print(self.event.date)
        self.assertNotEquals(str(self.event.date), "2025-01-01")

    def test_csv_export(self):
        response = self.client.get(reverse("events:export_event_csv", args=[self.event.id]))

        self.assertEqual(response.status_code, 200)

        expected_header = f"attachment; filename=event_{self.event.id}_participants.csv"
        self.assertEqual(response.get("Content-Disposition"), expected_header)

        content = response.content.decode("utf-8")

        self.assertIn("name,email", content)
        self.assertIn("Max Mustermann,max@a.com", content)
