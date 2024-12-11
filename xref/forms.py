from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Standard, Control, Requirement, Statement, Task

class StandardCreateOrUpdate(ModelForm):

    class Meta:
        model = Standard
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))

class ControlCreateOrUpdate(ModelForm):

    class Meta:
        model = Control
        fields = ['status', 'name', 'domain', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))

class RequirementCreateOrUpdate(ModelForm):

    class Meta:
        model = Requirement
        fields = ['status', 'name', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))

class StatementCreateOrUpdate(ModelForm):

    class Meta:
        model = Statement
        fields = ['status', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))

class TaskCreateOrUpdate(ModelForm):

    class Meta:
        model = Task
        fields = ['subject', 'predicate', 'object']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))
