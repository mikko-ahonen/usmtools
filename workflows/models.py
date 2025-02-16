import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from accounts.validators import RestrictedUsernameValidator
from accounts.models import Invitation
from .tenant_models import Tenant, TenantAwareOrderedModelBase, TenantAwareModelBase, TenantAwareTreeModelBase

class Account(AbstractUser):
    username_validator = RestrictedUsernameValidator()

    LANGUAGE_FI = 'fi'
    LANGUAGE_EN = 'en'

    LANGUAGES = (
        (LANGUAGE_EN, _('English')),
        (LANGUAGE_FI, _('Finnish')),
    )

    lang = models.CharField(
        max_length=2,
        verbose_name=_('Language'),
        choices=LANGUAGES,
        default=LANGUAGE_FI,
        error_messages={
          'required': _("You must choose the language"),
          'invalid_choice': _("Wrong language choice")
        }
    ) 

    invitation = models.ForeignKey(Invitation, null=True, on_delete=models.SET_NULL, related_name='accounts')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='accounts_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='accounts_modified')

    def __str__(self):
        if self.last_name or self.first_name:
            return self.get_full_name()
        else:
            return self.username


class OrganizationUnit(TenantAwareTreeModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='organizations_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='organizations_modified')
    #index = models.PositiveSmallIntegerField(editable=False, db_index=True, default=None, null=True)

    def __str__(self):
        return self.name

    #order_field_name = 'index'
    #order_with_respect_to = 'tenant'

    class Meta:
        verbose_name = _('organization unit')
        verbose_name_plural = _('organization units')
        default_related_name = 'organization_units'
    #    ordering = ('index',)


class Service(TenantAwareTreeModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services')
    is_meta = models.BooleanField(default=False) # Meta service, used for example for templates
    is_global_template = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='services_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='services_modified')
    #index = models.PositiveSmallIntegerField(editable=False, db_index=True, default=None, null=True)

    def __str__(self):
        return self.name

    #order_field_name = 'index'
    #order_with_respect_to = 'tenant'

    #def get_absolute_url(self):
    #    return reverse('workflows:service-detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.name

    class Meta:
    #    ordering = ('index',)
        verbose_name = _('service')
        verbose_name_plural = _('services')
        default_related_name = 'services'
        permissions = [
            ("can_edit_global_template", "Can edit the service containing the global routine templates"),
        ]

class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class Customer(TenantAwareModelBase):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    CUSTOMER_TYPE_INTERNAL = "internal"
    CUSTOMER_TYPE_EXTERNAL = "external"
    CUSTOMER_TYPE_CHOICES = [
        (CUSTOMER_TYPE_INTERNAL, _("Internal")),
        (CUSTOMER_TYPE_EXTERNAL, _("External")),
    ]
    customer_type = models.CharField(max_length=10, choices=CUSTOMER_TYPE_CHOICES, default=CUSTOMER_TYPE_INTERNAL)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='customers_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='customers_modified')

    def __str__(self):
        name = self.name
        cust_type = self.get_customer_type_display()
        return f"{name} ({cust_type})"

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        default_related_name = 'customers'


class ServiceCustomer(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='service_customers_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='service_customers_modified')
    service = models.ForeignKey(Service, null=False, blank=False, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.service} <-> {self.customer}"

    class Meta:
        verbose_name = _('service to customer relationship')
        verbose_name_plural = _('service to customer relationships')
        default_related_name = 'service_customers'


class Routine(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_template = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    based_on = models.ForeignKey('Routine', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    PROCESS_AGREE = "agree"
    PROCESS_CHANGE = "change"
    PROCESS_RECOVER = "recover"
    PROCESS_OPERATION = "operation"
    PROCESS_RISK = "risk"
    PROCESSES = [
        (PROCESS_AGREE, _("Agree")),
        (PROCESS_CHANGE, _("Change")),
        (PROCESS_RECOVER, _("Recover")),
        (PROCESS_OPERATION, _("Operation")),
        (PROCESS_RISK, _("Risk")),
    ]
    process = models.CharField(max_length=32, choices=PROCESSES, default=PROCESS_RECOVER)
    tags = TaggableManager(through=UUIDTaggedItem)

    order_field_name = 'index'
    order_with_respect_to = 'service'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('workflows:routine-detail', kwargs={'pk': self.id})

    def can_draw_diagram(self):
        count = 0
        for step in self.steps.all():
            for activity in step.activities.all():
                for action in activity.actions.all():
                    count += 1
                    if count > 1:
                        return True
        return False

    class Meta:
        verbose_name = _('routine')
        verbose_name_plural = _('routines')
        ordering = ('index',)
        default_related_name = 'routines'


class Share(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    SCOPE_ROUTINE = "routine"
    SCOPE_CHOICES = [
        (SCOPE_ROUTINE, _("Routine")),
    ]
    scope = models.CharField(max_length=10, choices=SCOPE_CHOICES, default=SCOPE_ROUTINE)

    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='shares', null=True)
    token1 = models.UUIDField(default=uuid.uuid4, editable=False)
    token2 = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    last_access = models.DateTimeField(editable=False, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('workflows:shared-routine-detail', kwargs={'pk': self.id, 'token1': self.token1, 'token2': self.token2})

    class Meta:
        verbose_name = _('share')
        verbose_name_plural = _('shares')
        default_related_name = 'shares'


class Profile(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    order_field_name = 'index'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('index',)
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        default_related_name = 'profiles'


class Step(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    fork = models.ForeignKey(Routine, null=True, on_delete=models.SET_NULL, help_text=_('Only used in template routine to specify forks to sub-routine. In actualized routines, all the forks have been expanded into one single routine.'), related_name='forks')
    process_depth  = models.PositiveSmallIntegerField(null=True, blank=True, help_text=_('Used in actualized routines, to signal how many levels of sub-processes there are'))
    skipped = models.BooleanField(default=False, help_text=_('This step is skipped'))

    PROCESS_AGREE = "agree"
    PROCESS_CHANGE = "change"
    PROCESS_RECOVER = "recover"
    PROCESS_OPERATE = "operate"
    PROCESS_IMPROVE = "improve"
    PROCESS_CHOICES = [
        (PROCESS_AGREE, _("Agree")),
        (PROCESS_CHANGE, _("Change")),
        (PROCESS_RECOVER, _("Recover")),
        (PROCESS_OPERATE, _("Operate")),
        (PROCESS_IMPROVE, _("Improve")),
    ]
    process = models.CharField(max_length=10, choices=PROCESS_CHOICES, default=PROCESS_AGREE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    
    order_field_name = 'index'
    order_with_respect_to = 'routine'

    class Meta:
        unique_together = ('routine', 'index')
        default_related_name = 'steps'
        ordering = ('index',)
        verbose_name_plural = _('steps')


    def __str__(self):
        return f"{self.routine.name}/{self.name}"


class Activity(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    name = models.CharField(max_length=255)
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='activities')
    description = models.TextField(blank=True, null=True)
    skipped = models.BooleanField(default=False, help_text=_('This activity is skipped'))

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    order_field_name = 'index'
    order_with_respect_to = 'step'

    def __str__(self):
        return f"{self.step.routine.name}/{self.step.name}/{self.name}"

    class Meta:
        verbose_name_plural = _('activities')
        ordering = ('index',)
        default_related_name = 'activities'


class Action(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    RASCI_RESPONSIBLE = "R"
    RASCI_ACCOUNTABLE = "A"
    RASCI_SUPPORTING = "S"
    RASCI_CONSULTED = "C"
    RASCI_INFORMED = "I"
    RASCI_CHOICES = [
        (RASCI_RESPONSIBLE, _("Responsible")),
        (RASCI_ACCOUNTABLE, _("Accountable")),
        (RASCI_SUPPORTING, _("Supporting")),
        (RASCI_CONSULTED, _("Consulted")),
        (RASCI_INFORMED, _("Informed")),
    ]
    types = models.CharField(max_length=4, blank=True, default='')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    organization_unit = models.ForeignKey(OrganizationUnit, on_delete=models.CASCADE, null=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='actions')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'
    order_with_respect_to = 'activity'

    def get_types_display(self):
        retval = []
        for (k, v) in Action.RASCI_CHOICES:
            if k in self.types:
                retval.append(str(v))
        if len(retval) == 0:
            return _('No actions')
        return ", ".join(retval)

    def __str__(self):
        if self.profile and self.organization_unit:
            name = self.profile.name + ' / ' + self.organization_unit.name
        elif self.profile:
            name = self.profile.name
        elif self.organization_unit:
            name = self.organization_unit.name
        else:
            name = "no name"
        return self.get_types_display() + ': ' + name 

    class Meta:
        verbose_name = _('responsible')
        verbose_name_plural = _('responsibles')
        ordering = ['modified_at',]
        default_related_name = 'responsibles'

class WorkInstruction(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    responsible = models.ForeignKey(Action, on_delete=models.CASCADE)

    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        verbose_name = _('work instruction')
        verbose_name_plural = _('work instructions')
        ordering = ['modified_at',]
        default_related_name = 'work_instructions'

    def __str__(self):
        profile = self.responsible.profile
        ou = self.responsible.organization_unit
        if profile and ou:
            name = profile.name + ' / ' + ou.name
        elif profile:
            name = profile.name
        elif ou:
            name = ou.name
        else:
            name = "no name"

        return f"{self.responsible.activity.step.routine.name}/{self.responsible.activity.step.name}/{self.responsible.activity.name}/{name}"


class Task(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    actions = models.ManyToManyField(Action, related_name="actions")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    tags = TaggableManager(through=UUIDTaggedItem)

    order_field_name = 'index'
    order_with_respect_to = 'profile'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('workflows:task-detail', kwargs={'pk': self.id})

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        ordering = ('index',)
        default_related_name = 'tasks'


