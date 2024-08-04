from django.utils.translation import gettext_lazy as _
from django.forms import Form, ModelForm, ModelChoiceField, Select, BooleanField, CharField, ValidationError, formset_factory, ChoiceField, EmailField
from django.forms.widgets import Textarea, RadioSelect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Column, Row, HTML, Div

from .models import USMSurvey, Lead

class USMGenerateInvitationForm(Form):
    invitee_name = CharField(required=True, label=_('Invitee name'))
    invitee_email = EmailField(required=True, label=_('Invitee email'))
    invitee_org = CharField(required=True, label=_('Invitee organization'))
    invitation_group = CharField(required=True, label=_('Invitation group'), help_text=_('Will be visible to the invitee'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Generate link'), css_class='btn btn-primary'))

class USMQualifyForm(ModelForm):

    class Meta:
        model = Lead
        fields = ('name', 'email', 'organization', 'title', 'rationale',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Send'), css_class='btn btn-primary'))

class USMSurveyForm(ModelForm):

    class Meta:
        model = USMSurvey
        fields = ('proactive', 'documentation', 'tooling', 'internal_reporting', 'responsibilities', 'request',
                  'reporting', 'compliance', 'employee', 'supplier', 'services', 'planning', 'glossary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Send'), css_class='btn btn-primary'))

class USMSurveyBackgroundForm(ModelForm):

    class Meta:
        model = USMSurvey
        fields = ('countries', 'lang', 'industry', 'size', 'name', 'email', 'report_ok', 'sales_ok')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Send'), css_class='btn btn-primary'))
