from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'bio', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
