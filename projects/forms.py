from django.forms import ModelForm, HiddenInput, CharField
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Project, Story, Team

class ProjectCreateOrUpdate(ModelForm):

    next_url = CharField(required=False, widget=HiddenInput())

    class Meta:
        model = Project
        fields = ['name', 'prefix', 'start_date', 'sprint_length_in_days', 'release_length_in_days', 'epics_per_release', 'story_points_in_sprint', 'ideal_story_points_per_day', 'next_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class StoryForm(ModelForm):

    class Meta:
        model = Story
        fields = ['name', 'description', 'story_points', 'team', 'priority', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team'].queryset = Team.objects.all()
        self.helper = FormHelper()
        self.helper.form_tag = False

