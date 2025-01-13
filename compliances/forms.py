from django import forms
from django.utils.translation import gettext as _

from projects.models import Team
from .models import Target

from crispy_forms.helper import FormHelper

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ["name"]

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]
