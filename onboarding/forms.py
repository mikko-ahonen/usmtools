from django.forms import ModelForm, BooleanField, ChoiceField, ValidationError
from onboarding.models import Contact
from django.utils.translation import gettext_lazy as _

from .models import Contact

class ContactCreateForm(ModelForm):

    mailing_list = BooleanField(label=_('Keep me updated on your upcoming workshops, product releases etc. relevant news'), required=False)
    sales_contact = BooleanField(label=_('We need to fix our service management ASAP! Let''s get in touch!'), required=False)

    class Meta:
        model = Contact
        fields = ['industry', 'mailing_list', 'sales_contact', 'email',]

    def clean(self):
        cleaned_data = super(ContactCreateForm, self).clean()
        mailing_list = cleaned_data.get("mailing_list")
        sales_contact = cleaned_data.get("sales_contact")
        email = cleaned_data.get("email")

        if (mailing_list or sales_contact) and not email:
            raise ValidationError(_("Email address is required if you want us to contact you."))

        return cleaned_data
