from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.forms import Form, ModelForm, ModelChoiceField, Select, BooleanField, CharField, ValidationError, formset_factory, ChoiceField, ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import Textarea, RadioSelect, CheckboxSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Column, Row, HTML, Div
import pprint

from tree_queries.forms import TreeNodeChoiceField

#from dal import autocomplete
#from dal_select2_taggit.widgets import TaggitSelect2

from .models import Routine, Activity, Responsibility, Profile, Service, WorkInstruction, Customer, OrganizationUnit, Share, Tenant, ServiceCustomer, Task, Action


class UUIDModelChoiceField(ModelChoiceField):

    def to_python(self, value):
        return super().to_python(value)


class TenantCreateOrUpdate(ModelForm):

    class Meta:
        model = Tenant
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class TaskCreateOrUpdate(ModelForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class ServiceCreateOrUpdate(ModelForm):

    parent = TreeNodeChoiceField(queryset=None, required=False, help_text=_('Select the parent service, if any. Maximum service tree depth is 10.'))

    class Meta:
        model = Service
        fields = ['name', 'description', 'parent']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }

    # TODO: Maximum tree level
    #def clean_parent(self):
    #    parent = self.cleaned_data['parent']
    #    if parent and parent.level == 9:
    #        raise ValidationError("Maximum service tree depth is 10.")
    #    return parent

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Service.objects.filter(is_meta=False).with_tree_fields()
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class ProfileCreateOrUpdate(ModelForm):

    class Meta:
        model = Profile
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class ServiceCustomerAdd(ModelForm):

    use_existing_customer = BooleanField(widget=RadioSelect(choices=[(True, 'True'), (False, 'False')]), required=False) # initial value as radio checked on the template
    new_customer_name = CharField(required=False, label=_('Name'))
    new_customer_type = ChoiceField(required=False, label=_('Customer type'), choices=Customer.CUSTOMER_TYPE_CHOICES, initial=Customer.CUSTOMER_TYPE_INTERNAL)
    customer = ModelChoiceField(
                queryset=None,
                required=False, 
                label='')

    class Meta:
        model = ServiceCustomer
        fields = ['use_existing_customer', 'new_customer_name', 'new_customer_type', 'customer']

    def clean(self):
        use_existing_customer = 'use_existing_customer' in self.cleaned_data and self.cleaned_data['use_existing_customer']
        if use_existing_customer:
            customer = self.cleaned_data['customer']
            if 'new_customer_name' in self.cleaned_data and self.cleaned_data['new_customer_name'] != '':
                raise ValidationError(_('If you choose to select existing customer, you must clean new customer name'), code="existing_customer_requires_clean_new_profile_name",)
            if not customer:
                raise ValidationError(_('If you choose to select existing customer, you must select one'), code="existing_customer_requires_customer",)
        else:
            name = self.cleaned_data['new_customer_name']
            if not name:
                raise ValidationError(_('If you choose to creata a new customer, you must provide the name'), code="new_customer_requires_name",)
            customer_type = self.cleaned_data['new_customer_type']
            customer = self.cleaned_data['customer']
            if customer:
                raise ValidationError(_('If you choose to creata a new customer, please first deselect existing customer'), code="new_customer_deselect_customer",)
            customer = Customer(name=name, tenant_id=self.tenant_id, customer_type=customer_type)
            customer.save()
            self.cleaned_data['customer'] = customer
    
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        exclude_customer_ids = kwargs.pop('exclude_customer_ids')
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.exclude(pk__in=exclude_customer_ids)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.tenant_id = tenant_id


class OrganizationUnitCreateOrUpdate(ModelForm):

    parent = TreeNodeChoiceField(queryset=None, required=False, help_text=_('Select the parent organizational unit, if any. Maximum organization tree depth is 10.'))

    class Meta:
        model = OrganizationUnit
        fields = ['name', 'parent', 'description']

    # TODO: Maximum level
    #def clean_parent(self):
    #    parent = self.cleaned_data['parent']
    #    if parent and parent.level == 9:
    #        raise ValidationError("Maximum organization tree depth is 10.")
    #    return parent

    def __init__(self, *args, **kwargs):
        # if parent is set and None, it means create a root entity. If parent is not set, 
        # allow choosing the parent.
        parent_set = False
        user = kwargs.pop('user', None)
        if 'parent' in kwargs:
            parent_set = True
            parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)

        if parent_set:
            field = self.fields['parent']
            field.widget = field.hidden_widget()
            # if parent is None, we create a new root entity.
            if parent:
                field.queryset = OrganizationUnit.objects.filter(id=parent.id)
            self.initial['parent'] = parent
        else:
            self.fields['parent'].queryset = OrganizationUnit.objects.all().with_tree_fields()

        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class ActionCreateOrUpdate(ModelForm):

    class Meta:
        model = Action
        fields = ['title', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class CustomerCreateOrUpdate(ModelForm):

    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'description']

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class ActivityCreateOrUpdate(ModelForm):

    class Meta:
        model = Activity
        fields = ['name', 'description']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class WorkInstructionCreateOrUpdate(ModelForm):

    class Meta:
        model = WorkInstruction
        fields = ['description']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))



class RoutineUpdate(ModelForm):

    class Meta:
        model = Routine
        fields = ['name', 'description']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        #self.__class__.Meta.widgets['tags'] = autocomplete.TaggitSelect2(reverse('workflows:tag-autocomplete', kwargs={"tenant_id": tenant_id}))
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class RoutineCreate(ModelForm):

    template = UUIDModelChoiceField(queryset=Routine.unscoped.filter(is_template=True))

    class Meta:
        model = Routine
        fields = ['name', 'description', 'template']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

class ServiceShare(ModelForm):
    workflow = ModelChoiceField(
        queryset=None,
        required=False, 
        label='')

    class Meta:
        model = Share
        fields = ['name', 'scope', 'workflow']
        labels = {
            'name': '',
            'scope': '',
            'workflow': '',
        }

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

        if service:
            self.fields['workflow'].queryset = Routine.objects.filter(service=service, is_template=False)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(HTML(_('Name')), css_class='col-md-3 mb-1'),
                Column(HTML(_('Scope')), css_class='col-md-3 mb-1'),
                Column(HTML(_('Routine')), css_class='col-md-5 mb-1'),
                Column(Div(), css_class='col-md-1 mb-1'),
            ),
            Row(
                Column('name', css_class='form-group col-md-3'),
                Column('scope', css_class='form-group col-md-3'),
                Column('workflow', css_class='form-group col-md-5'),
                Column(Submit('submit', _('Share'), css_class='btn btn-primary'), css_class='form-group col-md-1 mb-0'),
                css_class='form-row align-items-start'
            ),
        )
        ##self.helper.form_class = 'form-horizontal'
        #self.helper.field_template = 'bootstrap5/layout/inline_field.html'
        self.helper.form_class = 'form-inline'
        #self.helper.template = 'bootstrap/table_inline_formset.html'
        #self.helper.add_input(Submit('submit', _('Share'), css_class='btn btn-primary'))
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-2'


class ServiceShareFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_tag = False
        self.render_required_fields = True


