import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from projects.models import Project
from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase

class Domain(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    projects = models.ManyToManyField(Project, related_name="domains")

    order_field_name = 'index'

    def project(self):
        return self.projects.all().first()

    def is_project_created(self):
        return self.project() is not None

    def is_project_setup_complete(self):
        project = self.project()
        return len(project.targets.all()) > 0

    def is_project_roadmap_created(self):
        project = self.project()
        return False

    def is_project_backlog_created(self):
        return False

    def is_project_deployment_completed(self):
        return False

    def is_audit_completed(self):
        return False

    def __str__(self):
        return self.name or self.slug

    class Meta:
        ordering = ('index',)

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


class Category(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'

    def __str__(self):
        return self.name or self.slug

    class Meta:
        ordering = ('index',)


class Constraint(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, null=True, related_name='constraints')
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='constraints')

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
    sections = models.ManyToManyField(Section, through='TargetSection')

    def __str__(self):
        return self.name or self.slug


class TargetSection(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, null=True, related_name='target_sections')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, related_name='+')
