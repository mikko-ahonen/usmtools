from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, ModelChoiceField
from django.forms.widgets import Textarea
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout

from .models import Training, Employee, Document


class UUIDModelChoiceField(ModelChoiceField):

    def to_python(self, value):
        return super().to_python(value)


class TrainingCreateOrUpdate(ModelForm):

    class Meta:
        model = Training
        fields = ['name', 'description', 'tags']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            #'tags': TaggitSelect2("/foobar"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.fields.keys())
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))


class EmployeeCreateOrUpdate(ModelForm):

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'title', 'description', 'email']
        widgets = {
            'description': Textarea(attrs={'rows': 4}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))

class DocumentCreateOrUpdate(ModelForm):

    class Meta:
        model = Document
        fields = ['name', 'description', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-primary'))
