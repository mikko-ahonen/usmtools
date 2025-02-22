from django import forms
from django.utils.translation import gettext as _

from projects.models import Team
from .models import Target, Definition

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Column, Row, HTML, Div

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
        fields = ["term", "term_plural", "definition", "ref_plural", "ref_plural_tag", "ref_entity_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        if self.instance and self.instance.ref_plural:
            plural_collapse_class = 'collapse show'
            plural_aria_expanded = 'true'
        else:
            plural_collapse_class = 'collapse'
            plural_aria_expanded = 'false'

        self.helper.layout = Layout(
            Div(
                Field('term'),
                Field(
                  'ref_plural', 
                  data_bs_toggle='collapse',
                  data_bs_target='#plural_collapse',
                  aria_controls='plural_collapse',
                  aria_expanded=plural_aria_expanded),
                Div(
                    Field('term_plural'),
                    Field('ref_plural_tag'),
                    css_class=plural_collapse_class, css_id='plural_collapse',
                ),
                Field('definition'),
                Field('ref_entity_type'),
            )
        )
