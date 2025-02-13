from django import forms
from django.utils.translation import gettext as _

from projects.models import Team
from .models import Target, Definition

from crispy_forms.helper import FormHelper

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ["name"]

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]

class DefinitionCreateOrUpdate(forms.ModelForm):
    class Meta:
        model = Definition
        fields = ["term", "definition", "ref_entity_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
