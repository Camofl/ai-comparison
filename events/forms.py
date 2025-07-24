from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import Event, Participant


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }


class BaseParticipantFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(
                form.cleaned_data
                and not form.cleaned_data.get("DELETE", False)
                and (form.cleaned_data.get("name") or form.cleaned_data.get("email"))
                for form in self.forms
        ):
            raise ValidationError("Please enter at least one participant.")

        emails = [
            form.cleaned_data["email"].lower()
            for form in self.forms
            if (form.cleaned_data
                and not form.cleaned_data.get("DELETE", False)
                and form.cleaned_data.get("email"))
        ]

        if len(set(emails)) != len(emails):
            raise ValidationError("Duplicate email addresses are not allowed.")


ParticipantFormSet = inlineformset_factory(
    Event,
    Participant,
    formset=BaseParticipantFormSet,
    fields=("name", "email"),
    extra=5,
    can_delete=True
)
