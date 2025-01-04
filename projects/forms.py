from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Project

class ProjectCreateOrUpdate(ModelForm):

    class Meta:
        model = Project
        fields = ['name', 'prefix', 'start_date', 'sprint_length_in_days', 'release_length_in_days', 'epics_per_release', 'storypoints_in_sprint']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))
