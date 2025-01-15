import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from colorfield.fields import ColorField

from projects.models import Project, Story, Team
from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase

class Domain(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    projects = models.ManyToManyField(Project, related_name="domains")

    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
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

    def is_project_scope_setup_complete(self):
        retval = False
        for category in self.categories.all():
            if not category.team:
                return False
            retval = True
        return retval

    def is_project_teams_setup_complete(self):
        if project := self.project():
            if targets := project.targets:
                if len(project.targets.all()) > 0:
                    return True
                return False
        return False

    def is_project_data_management_setup_complete(self):
        if project := self.project():
            domain = project.domains.first()
            for dm in domain.data_managements.all():
                if not dm.team:
                    return False
                if dm.policy == DataManagement.POLICY_NOT_DEFINED:
                    return False
            return True
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

    def sections_with_status(self):
        sections = list(Section
                        .unscoped
                        .filter(tenant_id=self.tenant.id, domain_id=self.id)
                        .with_tree_fields())
        for section in sections:
            section._status = Constraint.most_urgent_status([r.get_status() for r in section.requirements.all()])
            if not section._status:
                section._status = Constraint.STATUS_NEW
            if section.parent:
                section.parent._status = Constraint.most_urgent_status([section._status, section.parent._status])
        return sections

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
    _status = None

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
    title = models.CharField(max_length=255, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    text = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    _status = None

    def get_status(self):
        if not self._status:
            self._status = Constraint.most_urgent_status([constraint.status for constraint in self.statement.constraints])
        return self._status

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
    team = models.ForeignKey('projects.Team', on_delete=models.SET_NULL, null=True, related_name='categories')
    name = models.CharField(max_length=255, blank=True, null=True)
    color = ColorField(default='#000000')

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


class Constraint(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    statements = models.ManyToManyField(Statement, through="ConstraintStatement")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)
    story_points = models.FloatField(null=True, blank=True)

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

    STATUS_URGENCY = {v: i for i, v in enumerate([
        STATUS_AUDITED,
        STATUS_COMPLIANT,
        STATUS_IMPLEMENTED,
        STATUS_ONGOING,
        STATUS_NEW,
        STATUS_NON_COMPLIANT, 
        STATUS_FAILED, 
    ])}

    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NEW)

    @classmethod
    def cmp_status_urgency(cls, a, b):
        if not a:
            if b:
                return 1
            return 0
        if not b:
            if a:
                return -1
            assert False
        return cls.STATUS_URGENCY[a] - cls.STATUS_URGENCY[b]

    @classmethod
    def most_urgent_status(cls, statuses):
        status = None
        for s in statuses:
            if cls.cmp_status_urgency(status, s) > 0:
                status = s

        return status

    order_field_name = 'index'

    @property
    def stories(self):
        return self.story_set(manager='unscoped')

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

class DataManagement(TenantAwareOrderedModelBase):
    """
    Meta class to define the data management policy for a model class
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, related_name='data_managements')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='data_managements')
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

    order_field_name = 'index'

    @classmethod
    def is_valid_policy(cls, policy):
        for p in cls.POLICIES:
            if policy == p[0]:
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
