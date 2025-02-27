import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from workflows.tenant_models import Tenant, TenantAwareOrderedModelBase, TenantAwareModelBase, TenantAwareTreeModelBase

class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class Document(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    url = models.URLField(blank=True, null=True, verbose_name=_('URL'))

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    tags = TaggableManager(through=UUIDTaggedItem)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        default_related_name = 'documents'

class Training(TenantAwareModelBase):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    url = models.URLField(blank=True, null=True, verbose_name=_('URL'))

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    tags = TaggableManager(through=UUIDTaggedItem)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Training')
        verbose_name_plural = _('Trainings')
        default_related_name = 'trainings'


class Employee(TenantAwareModelBase):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    tags = TaggableManager(through=UUIDTaggedItem)


    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        default_related_name = 'employees'


class TrainingAttended(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL, related_name='attended')
    training = models.ForeignKey(Training, null=True, on_delete=models.SET_NULL, related_name='attendants')
    date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Training attended')
        verbose_name_plural = _('Trainings attended')
        default_related_name = 'trainings_attended'


class TrainingOrganized(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    training = models.ForeignKey(Training, null=True, on_delete=models.SET_NULL, related_name='organized')
    date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Training organized')
        verbose_name_plural = _('Trainings organized')
        default_related_name = 'trainings_organized'


class Risk(TenantAwareModelBase):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Impact Levels
    IMPACT_VERY_LOW = 'very-low'
    IMPACT_LOW = 'low'
    IMPACT_MEDIUM = 'medium'
    IMPACT_HIGH = 'high'
    IMPACT_CRITICAL = 'critical'

    IMPACT_LEVELS = [
        (IMPACT_VERY_LOW, _("Low")),
        (IMPACT_MEDIUM, _("Medium")),
        (IMPACT_HIGH, _("High")),
        (IMPACT_CRITICAL, _("Critical")),
    ]

    # Likelihood Levels
    LIKELIHOOD_RARE = 'rare'
    LIKELIHOOD_UNLIKELY = 'unlikely'
    LIKELIHOOD_POSSIBLE = 'possible'
    LIKELIHOOD_LIKELY = 'likely'
    LIKELIHOOD_ALMOST_CERTAIN = 'almost-certain'

    LIKELIHOOD_LEVELS = [
        (LIKELIHOOD_RARE, _("Rare")),
        (LIKELIHOOD_UNLIKELY, _("Unlikely")),
        (LIKELIHOOD_POSSIBLE, _("Possible")),
        (LIKELIHOOD_LIKELY, _("Likely")),
        (LIKELIHOOD_ALMOST_CERTAIN, _("Almost Certain")),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Enter a short and descriptive name for the risk.")
    )

    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Provide a detailed description of the risk.")
    )

    url = models.URLField(blank=True, null=True, verbose_name=_('URL'), help_text=_('URL for this risk'))

    CATEGORY_OPERATIONAL = 'operational'
    CATEGORY_FINANCIAL = 'financial'
    CATEGORY_COMPLIANCE = 'compliance'
    CATEGORY_STRATEGIC = 'strategic'
    CATEGORY_REPUTATIONAL = 'reputational'

    RISK_CATEGORIES = [
        (CATEGORY_OPERATIONAL, _("Operational")),
        (CATEGORY_FINANCIAL, _("Financial")),
        (CATEGORY_COMPLIANCE, _("Compliance")),
        (CATEGORY_STRATEGIC, _("Strategic")),
        (CATEGORY_REPUTATIONAL, _("Reputational")),
    ]

    category = models.CharField(
        max_length=50,
        choices=RISK_CATEGORIES,
        verbose_name=_("Category"),
        help_text=_("Select the category that best describes this risk.")
    )

    # Inherent Risk: Before any controls are applied
    inherent_impact = models.CharField(
        max_length=10,
        choices=IMPACT_LEVELS,
        verbose_name=_("Inherent Impact"),
        help_text=_("Assess the impact level of the risk before any mitigation actions.")
    )
    inherent_likelihood = models.CharField(
        max_length=15,
        choices=LIKELIHOOD_LEVELS,
        verbose_name=_("Inherent Likelihood"),
        help_text=_("Assess the likelihood of the risk occurring before any mitigation actions.")
    )

    # Mitigation plan
    mitigation_plan = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Mitigation Plan"),
        help_text=_("Describe the mitigation strategies or actions to reduce the risk.")
    )

    # Residual Risk: After applying controls
    residual_impact = models.CharField(
        max_length=10,
        choices=IMPACT_LEVELS,
        blank=True,
        null=True,
        verbose_name=_("Residual Impact"),
        help_text=_("Assess the impact level of the risk after mitigation actions.")
    )
    residual_likelihood = models.CharField(
        max_length=15,
        choices=LIKELIHOOD_LEVELS,
        blank=True,
        null=True,
        verbose_name=_("Residual Likelihood"),
        help_text=_("Assess the likelihood of the risk occurring after mitigation actions.")
    )

    responsible_party_name = models.CharField(
        max_length=255,
        verbose_name=_("Name of responsible party"),
        help_text=_("Specify the name of the individual or department responsible for managing this risk.")
    )

    # Status Choices
    STATUS_IDENTIFIED = 'identified'
    STATUS_ASSESSED = 'assessed'
    STATUS_MITIGATED = 'mitigated'
    STATUS_RESOLVED = 'resolved'
    STATUS_ACCEPTED = 'accepted'

    STATUS_CHOICES = [
        (STATUS_IDENTIFIED, _("Identified")),
        (STATUS_ASSESSED, _("Assessed")),
        (STATUS_MITIGATED, _("Mitigated")),
        (STATUS_RESOLVED, _("Resolved")),
        (STATUS_ACCEPTED, _("Accepted")),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_IDENTIFIED,
        verbose_name=_("Status"),
        help_text=_("Track the current status of the risk in its lifecycle.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    tags = TaggableManager(through=UUIDTaggedItem)

    def __str__(self):
        return self.name


class DataManagement(TenantAwareOrderedModelBase):
    """
    Meta class to define the data management policy and status for a model class
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True, default=0)
    allow_policy_change = models.BooleanField(default=True)

    POLICY_NOT_DEFINED = "not-defined"
    POLICY_MANUAL = "manual"
    POLICY_LINK = "linked"
    POLICY_REPLICATED = "replicated"
    POLICY_MANAGED = "managed"

    POLICIES = [
        (POLICY_NOT_DEFINED, _("Not defined")),
        (POLICY_MANUAL, _("Manual")),
        (POLICY_LINK, _("Link")),
        (POLICY_REPLICATED, _("Replicated")),
        (POLICY_MANAGED, _("Managed")),
    ]

    policy = models.CharField(max_length=32, choices=POLICIES, default=POLICY_NOT_DEFINED)

    STATUS_NOT_DEFINED = "not-defined"
    STATUS_PROTOTYPING = "prototyping"
    STATUS_DEVELOPMENT = "development"
    STATUS_TESTING = "testing"
    STATUS_PRODUCTION = "production"

    STATUSES = [
        (STATUS_NOT_DEFINED, _("Not defined")),
        (STATUS_PROTOTYPING, _("Prototyping")),
        (STATUS_DEVELOPMENT, _("Development")),
        (STATUS_TESTING, _("Testing")),
        (STATUS_PRODUCTION, _("Production")),
    ]

    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NOT_DEFINED)

    order_field_name = 'index'

    @classmethod
    def is_valid_policy(cls, policy):
        for p in cls.POLICIES:
            if policy == p[0]:
                return True
        return False

    @classmethod
    def is_valid_status(cls, status):
        for s in cls.STATUSES:
            if status == s[0]:
                return True
        return False

    def get_entity_name(self):
        if self.content_type:
            cls = self.content_type.model_class()
            if cls:
                return cls._meta.verbose_name
        return _("Unknown entity")

    def __str__(self):
        cls = self.content_type.model_class()
        return cls._meta.verbose_name + ': ' + self.get_policy_display()

    class Meta:
        ordering = ('index',)
