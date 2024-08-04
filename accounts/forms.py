from django.forms import Form, ModelForm, CharField, HiddenInput, CheckboxInput, BooleanField, ChoiceField, TextInput, Field, HiddenInput
from django.forms.widgets import Textarea
#from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext as _
from django.urls import reverse_lazy
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field as CrispyField, ButtonHolder, HTML

from registration.forms import RegistrationForm as BaseRegistrationForm
#from registration.forms import RegistrationFormTermsOfService as BaseRegistrationForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as OrigPasswordChangeForm, PasswordResetForm as OrigPasswordResetForm, SetPasswordForm as OrigSetPasswordForm

from workflows.models import Account
from .models import WaitingListEntry

class MultiEmailField(Field):
    def to_python(self, value):
        """Normalize string with comma-separated values into list of strings"""
        # Return an empty list if no input was given.
        if not value:
            return []
        return [ x.strip() for x in value.split(',') ]

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.
        super().validate(value)
        for email in value:
            validate_email(email)

class Row(Div):
    css_class = "form-row"

class JoinWaitingListForm(ModelForm):
    # these two are honey traps for spam bots, we check that they are unmodified
    email2 = CharField(initial='your@email.com', max_length=254, widget=TextInput(attrs={'class': "d-none"}), label="", help_text="") 
    website = CharField(initial='http://www.google.com', widget=HiddenInput())

    def clean_email(self):
        e = self.cleaned_data['email'].strip()

        if Account.objects.filter(email=e).exists():
            raise ValidationError(_("An account already exists with this email."))
        if WaitingListEntry.objects.filter(email=e).exists():
            raise ValidationError(_("This email address is already in the waiting list."))

        return e

    def clean_email2(self):
        if self.cleaned_data['email2'] != 'your@email.com':
            raise ValidationError('Spam bot detected')
        return ''

    def clean_website(self):
        if self.cleaned_data['website'] != 'http://www.google.com':
            raise ValidationError('Spam bot detected')
        return ''

    invite_emails = MultiEmailField(label=_('Email addresses to invite, separated by comma'), required=False)

    class Meta:
        model = WaitingListEntry
        fields = ['email', 'email2', 'website', 'why', 'source', 'interested_groups', 'invite_emails']
        widgets = {
            'why': Textarea(attrs={'rows': 4}),
            'source': Textarea(attrs={'rows': 4}),
            'interested_groups': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Join waiting list'), css_class='btn btn-primary btn-rounded'))

class RegistrationForm(BaseRegistrationForm):

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ('lang',)

    tos = BooleanField(widget=CheckboxInput,
                       label=_('I have read and agree to the Terms of Service'),
                       error_messages={'required': _("You must agree to the Terms of Service to register")})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.lang.label = _("Your preferred language")
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', _('Register'), css_class='btn btn-primary btn-rounded'))

class PasswordResetForm(OrigPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Div(
                    HTML('<label for="id_email" class=" requiredField"> ' + _('Email') + '<span class="asteriskField">*</span></label>'),
                    css_class='col-md-9'
                ),
            ),
            Row(
                CrispyField('email', wrapper_class='col-md-9'),
                Div(
                    Submit('submit', _('Reset password'), css_class='btn button white btn-rounded'),
                    css_class='col-md-2'
                ),
            )
        )

class PasswordResetConfirmForm(OrigSetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Reset password'), css_class='btn btn-primary btn-rounded'))

class PasswordChangeForm(OrigPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Change password'), css_class='btn btn-primary btn-rounded'))

class LoginForm(AuthenticationForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(
                CrispyField('username', wrapper_class='col-md-5'),
                CrispyField('password', wrapper_class='col-md-5'),
                Div(
                    Submit('submit', _('Login'), css_class='btn btn-rounded button white my-auto'),
                    css_class='col-md-2 mb-3'
                ),
                css_class='row-fluid'
            )
        )

