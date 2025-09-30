from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, BaseInlineFormSet

from .models import Event, Participant, Post


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


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'bio', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
