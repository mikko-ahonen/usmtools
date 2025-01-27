from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm, ModelChoiceField, Select, BooleanField, CharField, ValidationError, formset_factory, ChoiceField
from django.forms.widgets import Textarea, RadioSelect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Column, Row, HTML, Div
import pprint

from tree_queries.forms import TreeNodeChoiceField

#from dal import autocomplete
#from dal_select2_taggit.widgets import TaggitSelect2

from .models import Routine, Activity, Action, Profile, Service, WorkInstruction, Customer, OrganizationUnit, Share, Tenant, ServiceCustomer


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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = OrganizationUnit.objects.all().with_tree_fields()
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class CustomerCreateOrUpdate(ModelForm):

    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))


class ActionCreateOrUpdate(ModelForm):
    profile_choices = [('none', _('none')), ('use', _('use')), ('create', _('create'))]
    use_existing_profile = ChoiceField(widget=RadioSelect(choices=profile_choices), choices=profile_choices, required=False) # initial value as radio checked on the template
    profile = ModelChoiceField(
                queryset=None,
                required=False, 
                label='')

    new_profile_name = CharField(required=False, label=_('Name'))

    org_choices = [('none', 'none'), ('use', 'use'), ('create', 'create')]
    use_existing_organization_unit = ChoiceField(widget=RadioSelect(choices=org_choices), choices=org_choices, required=False) # initial value as radio checked on the template
    organization_unit = TreeNodeChoiceField(queryset=None, required=False, label='')
    new_organization_unit_name = CharField(required=False, label=_('Name'))
    new_organization_unit_parent = TreeNodeChoiceField(queryset=None, required=False, label=_('Parent'), help_text=_('Select the parent organizational unit, if any. Maximum organization tree depth is 10.'))

    class Meta:
        model = Action
        fields = ['title', 'description', 'use_existing_organization_unit', 'organization_unit', 'new_organization_unit_name', 'new_organization_unit_parent', 'use_existing_profile', 'new_profile_name', 'profile']

    def clean(self):
        use_existing_organization_unit = self.cleaned_data['use_existing_organization_unit'] if 'use_existing_organization_unit' in self.cleaned_data else None
        if use_existing_organization_unit == 'use':
            ou = self.cleaned_data['organization_unit']
            if 'new_organization_unit_name' in self.cleaned_data and self.cleaned_data['new_organization_unit_name'] != '':
                raise ValidationError(_('If you choose to select an existing organization unit, you must clean new organization unit name'), code="existing_org_unit_requires_clean_new_org_unit_name",)
            if not ou:
                raise ValidationError(_('If you choose to select an existing organization unit, you must select one'), code="existing_org_unit_requires_org_unit",)
        elif use_existing_organization_unit == 'create':
            ou = self.cleaned_data['organization_unit']
            name = self.cleaned_data['new_organization_unit_name']
            parent = self.cleaned_data['new_organization_unit_parent']
            if ou:
                raise ValidationError(_('If you choose to creata a new organization unit, please first deselect existing organization unit'), code="new_org_unit_deselect_org_unit",)
            if not name:
                raise ValidationError(_('If you choose to creata a new organization unit, you must provide the name'), code="new_org_unit_requires_name",)
            ou = OrganizationUnit(name=name, parent=parent, tenant_id=self.tenant_id)
            ou.save()
            self.cleaned_data['organization_unit_id'] = ou.id
            self.cleaned_data['organization_unit'] = ou
        else: # none i.e. link only to org unit
            if 'new_organization_unit_name' in self.cleaned_data and self.cleaned_data['new_organization_unit_name'] != '':
                raise ValidationError(_('If you choose not to link to an organization unit, you must clean new organization unit name'), code="no_org_unit_requires_clean_new_org_unit_name",)
            ou = self.cleaned_data['organization_unit']
            if ou:
                raise ValidationError(_('If you choose not to link to an organization unit, please first deselect existing organization unit'), code="no_org_unit_deselect_org_unit",)

        use_existing_profile = self.cleaned_data['use_existing_profile'] if 'use_existing_profile' in self.cleaned_data else None
        if use_existing_profile == 'use':
            profile = self.cleaned_data['profile']
            if 'new_profile_name' in self.cleaned_data and self.cleaned_data['new_profile_name'] != '':
                raise ValidationError(_('If you choose to select an existing profile, you must clean new profile name'), code="existing_profile_requires_clean_new_profile_name",)
            if not profile:
                raise ValidationError(_('If you choose to select an existing profile, you must select one'), code="existing_profile_requires_profile",)
        elif use_existing_profile == 'create':
            name = self.cleaned_data['new_profile_name']
            if not name:
                raise ValidationError(_('If you choose to creata a new profile, you must provide the name'), code="new_profile_requires_name",)
            profile = self.cleaned_data['profile']
            if profile:
                raise ValidationError(_('If you choose to creata a new profile, please first deselect existing profile'), code="new_profile_deselect_profile",)
            profile = Profile(name=name, tenant_id=self.tenant_id)
            profile.save()
    
            self.cleaned_data['profile_id'] = profile.id
            self.cleaned_data['profile'] = profile
        else: # none i.e. link only to 
            if 'new_profile_name' in self.cleaned_data and self.cleaned_data['new_profile_name'] != '':
                raise ValidationError(_('If you choose not to link to profile, you must clean new profile name'), code="no_profile_requires_clean_new_profile_name",)
            if 'profile' in self.cleaned_data and self.cleaned_data['profile']:
                raise ValidationError(_('If you choose not to link to profile, you must first deselect existing profile'), code="no_profile_requires_deselect_profile",)
            
        if use_existing_profile == 'none' and use_existing_organization_unit == 'none':
            raise ValidationError(_('You must either choose or create a profile or an organization unit'), code="either_profile_or_org_unit_required",)
            

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        exclude_profile_ids = kwargs.pop('exclude_profile_ids')
        super().__init__(*args, **kwargs)
        self.fields['new_organization_unit_parent'].queryset = OrganizationUnit.objects.with_tree_fields()
        self.fields['organization_unit'].queryset = OrganizationUnit.objects.with_tree_fields()
        self.fields['profile'].queryset = Profile.objects.exclude(pk__in=exclude_profile_ids)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.tenant_id = tenant_id


class ActivityCreateOrUpdate(ModelForm):

    class Meta:
        model = Activity
        fields = ['name', 'description']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
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
        fields = ['name', 'description', 'tags']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            #'tags': TaggitSelect2("/foobar"),
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
        fields = ['name', 'description', 'tags']
        widgets = {
            'description': Textarea(attrs={'rows': 4}),
            #'tags': TaggitSelect2("/foobar"),
        }

    def __init__(self, *args, **kwargs):
        tenant_id = kwargs.pop('tenant_id')
        #self.__class__.Meta.widgets['tags'] = autocomplete.TaggitSelect2(reverse('workflows:tag-autocomplete', kwargs={"tenant_id": tenant_id}))
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        #self.helper.add_input(Submit('submit', _('Save'), css_class='btn btn-outline-primary'))

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

