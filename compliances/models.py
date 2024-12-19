import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase

class Domain(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'

    def __str__(self):
        return self.name or self.slug

    class Meta:
        ordering = ('index',)

class Project(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    prefix = models.CharField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, related_name='projects')

class Release(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

class Epic(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, null=True, related_name='epics')

class Section(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, related_name='sections')
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'
    order_with_respect_to = 'domain'

    def __str__(self):
        return self.title or self.slug

    class Meta:
        ordering = ('index',)
        unique_together = ('domain', 'index',)

class Requirement(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='requirements')
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'
    order_with_respect_to = 'section'

    def __str__(self):
        return self.text or self.slug

    class Meta:
        ordering = ('index',)
        unique_together = ('section', 'index',)

class Term(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    definition = models.CharField(max_length=255, blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'

    class Meta:
        ordering = ('index',)

class Category(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name or self.slug

class ConstraintCategory(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    constraint = models.ForeignKey('Constraint', on_delete=models.CASCADE, null=True, related_name='constraints')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='categories')

    def __str__(self):
        return self.constraint + " / " + self.category

class Constraint(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, null=True, related_name='constraints')
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    categories = models.ManyToManyField(Category, through=ConstraintCategory)

    STATUS_NEW = "new"
    STATUS_ONGOING = "ongoing"
    STATUS_IMPLEMENTED = "implemented"
    STATUS_FAILED = "failed"
    STATUS_NON_COMPLIANT = "non-compliant"
    STATUS_COMPLIANT = "compliant"
    STATUS_AUDITED = "audited"
    STATUSES = [
        (STATUS_NEW, _("New")),
        (STATUS_ONGOING, _("Ongoing")),
        (STATUS_IMPLEMENTED, _("Implemented")),
        (STATUS_FAILED, _("Failed")),
        (STATUS_NON_COMPLIANT, _("Non-compliant")),
        (STATUS_COMPLIANT, _("Compliant")),
        (STATUS_AUDITED, _("Audited")),
    ]
    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NEW)

    order_field_name = 'index'
    order_with_respect_to = 'requirement'

    def __str__(self):
        return self.text or self.slug

    class Meta:
        ordering = ('index',)
        unique_together = ('requirement', 'index',)

    def get_goal(self):
        return (self.requirement.section.domain.slug + '_' + self.requirement.section.slug + '_' + self.requirement.slug + '_' + self.slug).replace("-", "_")

class Target(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, related_name='targets')

    def __str__(self):
        return self.name or self.slug

class TargetSection(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, null=True, related_name='target_sections')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, related_name='+')
