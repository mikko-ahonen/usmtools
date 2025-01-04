from django import forms
from django.utils.translation import gettext as _

from .models import Target, Team

from crispy_forms.helper import FormHelper

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        fields = ["name"]

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]

class RoadmapCreateForm(forms.Form):
    start_date = forms.DateField(label=_('Start date'), help_text=_("Start of the first release"))
    release_length_in_days = forms.IntegerField(label=_("Release length"), help_text=_("In days"))
    epics_in_release = forms.IntegerField(label=_("Epics per release"), help_text=_("Maximum number of epics in release"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
