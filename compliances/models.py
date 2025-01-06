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

    def is_project_configured(self):
        project = self.project()
        if project is not None:
            return project.start_date != None
        return False

    def is_project_setup_complete(self):
        if project := self.project():
            if targets := project.targets:
                return len(project.targets.all()) > 0
        return False

    def is_project_roadmap_created(self):
        if project := self.project():
            return project.roadmap is not None
        return False

    def is_project_backlog_created(self):
        if project := self.project():
            return project.backlog is not None
        return False

    def is_project_deployment_completed(self):
        return False

    def is_audit_completed(self):
        return False

    @property
    def root_sections(self):
        return self.section_set(manager='unscoped').filter(parent=None)

    @property
    def categories(self):
        return self.category_set(manager='unscoped')

    @property
    def constraints(self):
        return self.constraint_set(manager='unscoped')

    def __str__(self):
        return self.name or self.slug or str(self.id)

    class Meta:
        ordering = ('index',)

class Section(TenantAwareTreeModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey('Section', on_delete=models.CASCADE, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)
    docid = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    @property
    def subsections(self):
        return self.section_set(manager="unscoped")

    @property
    def requirements(self):
        return self.requirement_set(manager="unscoped")

    def __str__(self):
        return self.title or self.slug or str(self.id)

    class Meta:
        ordering = ('index',)
        unique_together = ('domain', 'parent', 'index',)

class Requirement(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    docid = models.CharField(max_length=255, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    text = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    @property
    def statement(self):
        return self.statement_set(manager="unscoped").first()

    @property
    def statements(self):
        return self.statement_set(manager="unscoped")

    order_field_name = 'index'
    order_with_respect_to = 'section'

    def __str__(self):
        return self.text or self.slug or str(self.id)

    class Meta:
        ordering = ('index',)
        unique_together = ('section', 'index',)


class Definition(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=255, blank=True, null=True)
    definition = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'

    class Meta:
        ordering = ('index',)


class Category(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, blank=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True, related_name='categories')

    order_field_name = 'index'

    @property
    def constraints(self):
        return self.constraint_set(manager='unscoped')

    @property
    def stories(self):
        return self.story_set(manager='unscoped')

    def __str__(self):
        return self.name or self.slug or str(self.id)

    class Meta:
        ordering = ('index',)

    @classmethod
    def get_category_by_name(self, tenant_id, domain_id, name):
        category, created = Category.unscoped.get_or_create(tenant_id=tenant_id, domain_id=domain_id, name=name)
        return category

class Statement(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, null=True)
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    @property
    def constraints(self):
        return [cs.constraint for cs in self.constraint_statements(manager='unscoped').all()]

    order_field_name = 'index'

    def __str__(self):
        return self.slug or self.text or str(self.id)

    class Meta:
        ordering = ('index',)


class Team(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, related_name='teams')

    order_field_name = 'index'

    def __str__(self):
        return self.name or self.slug or str(self.id)

    class Meta:
        ordering = ('index',)

class Constraint(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    statements = models.ManyToManyField(Statement, through="ConstraintStatement")
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)

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

    @property
    def statements(self):
        return [cs.statement for cs in self.constraint_statements(manager='unscoped').all()]

    def __str__(self):
        return self.text or self.slug

    class Meta:
        ordering = ('index',)

    def get_goal(self):
        return (self.category.slug + '_' + self.slug).replace("-", "_")


class ConstraintStatement(TenantAwareOrderedModelBase):
    constraint = models.ForeignKey(Constraint, on_delete=models.CASCADE, null=True, related_name='constraint_statements')
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, null=True, related_name='constraint_statements')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'
    order_with_respect_to = 'statement'

    class Meta:
        ordering = ('index',)


class Target(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, related_name='targets')
    sections = models.ManyToManyField(Section, through='TargetSection')

    def __str__(self):
        return self.name or self.slug or str(self.id)


class TargetSection(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target = models.ForeignKey(Target, on_delete=models.CASCADE, null=True, related_name='target_sections')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, related_name='+')
