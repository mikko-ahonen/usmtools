import re

from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import CrossReference
from compliances.models import Domain, Section, Requirement, Statement, Constraint

class CrossReferenceCreateOrUpdate(ModelForm):

    class Meta:
        model = CrossReference
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary-outline'))

class SectionCreateOrUpdate(ModelForm):

    class Meta:
        model = Section
        fields = ['docid', 'title', 'text', 'index']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary-outline'))


    def clean(self):
        cleaned_data = super().clean()
        docid = cleaned_data.get("docid", None)

        cleaned_data['index'] = -1

        if docid:
            if m := re.search(r'^(?:\d+\.)*(\d+)$', docid):
                cleaned_data['index'] = m.group(1)
                
        return cleaned_data

class RequirementCreateOrUpdate(ModelForm):

    class Meta:
        model = Requirement
        fields = ['docid', 'title', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary-outline'))

class StatementCreateOrUpdate(ModelForm):

    class Meta:
        model = Statement
        fields = ['title', 'text', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary-outline'))

class ConstraintCreateOrUpdate(ModelForm):

    class Meta:
        model = Constraint
        fields = ['key', 'title', 'text', 'description', 'story_points']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary-outline'))
