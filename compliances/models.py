import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from taggit.models import Tag
from colorfield.fields import ColorField

from projects.models import Project, Story, Team
from workflows.tenant_models import TenantAwareOrderedModelBase, TenantAwareTreeModelBase, TenantAwareModelBase
from .entity_types import EntityType, get_class_by_entity_type
from mir.models import DataManagement

class Domain(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    projects = models.ManyToManyField(Project, related_name="domains")

    XREF_STATUS_DRAFT = "draft"
    XREF_STATUS_READY = "ready"
    XREF_STATUS_VERIFIED = "verified"

    XREF_STATUSES = [
        (XREF_STATUS_DRAFT, _("Draft")),
        (XREF_STATUS_READY, _("Ready")),
        (XREF_STATUS_VERIFIED, _("Verified")),
    ]

    xref_status = models.CharField(max_length=32, choices=XREF_STATUSES, default=XREF_STATUS_DRAFT)

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

    def is_project_teams_setup_complete(self):
        retval = False
        for category in self.categories.all():
            if not category.team:
                return False
            retval = True
        return retval

    def is_project_scope_setup_complete(self):
        if project := self.project():
            if targets := project.targets:
                if len(project.targets.all()) > 0:
                    return True
        return False

    def is_project_data_management_setup_complete(self):
        if project := self.project():
            domain = project.domains.first()
            for dm in domain.data_management_plans.all():
                if not dm.team:
                    return False
                if dm.plan == DataManagementPlan.PLAN_NOT_DEFINED:
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

    #@property
    #def constraints(self):
    #    return self.constraint_set(manager='unscoped')

    def recursive_status(self, section):
        child_statuses = [self.recursive_status(section) for section in section.children.all()]
        section._status = Constraint.most_urgent_status([r.get_status() for r in section.requirements.all()])
        if section._status:
            child_statuses.append(section._status)
        section._status = Constraint.most_urgent_status(child_statuses)
        return section._status or Constraint.STATUS_NEW

    def sections_with_status(self):
        sections = list(Section
                        .objects
                        .filter(domain_id=self.id)
                        .with_tree_fields())

        for section in sections:
            section._status = self.recursive_status(section)

        return sections

    def __str__(self):
        return self.name or self.slug or str(self.id)

    class Meta:
        ordering = ('index',)

class Section(TenantAwareTreeModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doc = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey('Section', on_delete=models.CASCADE, null=True, related_name='children')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)
    docid = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(db_index=True)
    _status = None

    XREF_STATUS_DRAFT = "draft"
    XREF_STATUS_READY = "ready"
    XREF_STATUS_VERIFIED = "verified"

    XREF_STATUSES = [
        (XREF_STATUS_DRAFT, _("Draft")),
        (XREF_STATUS_READY, _("Ready")),
        (XREF_STATUS_VERIFIED, _("Verified")),
    ]

    xref_status = models.CharField(max_length=32, choices=XREF_STATUSES, default=XREF_STATUS_DRAFT)

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

    XREF_STATUS_DRAFT = "draft"
    XREF_STATUS_READY = "ready"
    XREF_STATUS_VERIFIED = "verified"

    XREF_STATUSES = [
        (XREF_STATUS_DRAFT, _("Draft")),
        (XREF_STATUS_READY, _("Ready")),
        (XREF_STATUS_VERIFIED, _("Verified")),
    ]

    xref_status = models.CharField(max_length=32, choices=XREF_STATUSES, default=XREF_STATUS_DRAFT)

    _status = None

    def get_status(self):
        if not self.statement:
            return Constraint.STATUS_FAILED
        if not self._status:
            self._status = Constraint.most_urgent_status([constraint.status for constraint in self.statement.constraints.all()])
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
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, blank=True)
    term = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Term (singular)'))
    term_plural = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Term (plural)'))
    definition = models.TextField(blank=True, null=True, verbose_name=_('Definition for the term'))

    ref_plural = models.BooleanField(default=False, verbose_name=_('If checked, this is a plural definition'))
    ref_plural_tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=models.PROTECT, verbose_name=_('The label used by plural definitions'))
    ref_entity_type = models.CharField(max_length=32, choices=EntityType.CHOICES, default=EntityType.NOT_DEFINED, verbose_name=_('Entity type used by definition'))
    ref_content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    ref_object_id = models.UUIDField(null=True, blank=True)
    ref_object = GenericForeignKey("ref_content_type", "ref_object_id")

    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'

    def get_matches(self):
        if not self.ref_plural:
            raise ValueError("Only plural definitions support getting matchs")

        cls = get_class_by_entity_type(self.ref_entity_type)

        if not hasattr(cls, 'tags'):
            raise ValueError(f"Class {cls} does not have tags attribute, but there is still a reference")

        return cls.objects.filter(tags__id=self.ref_plural_tag_id)

    def __str__(self):
        return self.term_plural if self.ref_plural and self.term_plural else self.term

    class Meta:
        ordering = ('index',)


class Category(TenantAwareTreeModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, blank=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    team = models.ForeignKey('projects.Team', on_delete=models.SET_NULL, null=True, related_name='categories')
    name = models.CharField(max_length=255, blank=True, null=True)
    color = ColorField(default='#000000')
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def subcategories(self):
        return self.cateogry_set(manager="unscoped")

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
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    XREF_STATUS_DRAFT = "draft"
    XREF_STATUS_READY = "ready"
    XREF_STATUS_VERIFIED = "verified"

    XREF_STATUSES = [
        (XREF_STATUS_DRAFT, _("Draft")),
        (XREF_STATUS_READY, _("Ready")),
        (XREF_STATUS_VERIFIED, _("Verified")),
    ]

    xref_status = models.CharField(max_length=32, choices=XREF_STATUSES, default=XREF_STATUS_DRAFT)

    @property
    def constraints(self):
        return [cs.constraint for cs in self.constraint_statements(manager='unscoped').all()]

    order_field_name = 'index'

    def __str__(self):
        return self.slug or self.text or str(self.id)

    class Meta:
        ordering = ('index',)


class ConstraintDependency(TenantAwareOrderedModelBase):
    source = models.ForeignKey('Constraint', on_delete=models.CASCADE, null=True, related_name='+')
    target = models.ForeignKey('Constraint', on_delete=models.CASCADE, null=True, related_name='+')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'
    order_with_respect_to = 'target'

    class Meta:
        ordering = ('index',)


class Constraint(TenantAwareOrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    statements = models.ManyToManyField(Statement, through="ConstraintStatement", related_name='constraints')
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)
    story_points = models.FloatField(null=True, blank=True)
    is_generic = models.BooleanField(default=True, help_text="If True statement, only this needs to be done only once. If False, needs to be implemented seperately for each target in scope.")
    key = models.CharField(max_length=255, blank=True, null=True)
    dependencies = models.ManyToManyField('Constraint', through="ConstraintDependency")
    definitions = models.ManyToManyField('Definition', through="ConstraintDefinition")

    XREF_STATUS_DRAFT = "draft"
    XREF_STATUS_READY = "ready"
    XREF_STATUS_VERIFIED = "verified"

    XREF_STATUSES = [
        (XREF_STATUS_DRAFT, _("Draft")),
        (XREF_STATUS_READY, _("Ready")),
        (XREF_STATUS_VERIFIED, _("Verified")),
    ]

    xref_status = models.CharField(max_length=32, choices=XREF_STATUSES, default=XREF_STATUS_DRAFT)

    @property
    def unscoped_definitions(self):
        return self.definitions(manager="unscoped")

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

    STATUS_TRANSITIONS = {
        STATUS_NEW: [STATUS_ONGOING, STATUS_IMPLEMENTED, STATUS_FAILED, STATUS_NON_COMPLIANT, STATUS_COMPLIANT],
        STATUS_ONGOING: [STATUS_IMPLEMENTED, STATUS_FAILED, STATUS_NON_COMPLIANT, STATUS_COMPLIANT],
        STATUS_FAILED: [STATUS_ONGOING, STATUS_IMPLEMENTED, STATUS_FAILED, STATUS_NON_COMPLIANT, STATUS_COMPLIANT],
        STATUS_NON_COMPLIANT: [STATUS_FAILED, STATUS_ONGOING, STATUS_IMPLEMENTED, STATUS_FAILED, STATUS_COMPLIANT],
        STATUS_IMPLEMENTED: [STATUS_FAILED, STATUS_ONGOING, STATUS_COMPLIANT, STATUS_FAILED, STATUS_NON_COMPLIANT, STATUS_AUDITED],
        STATUS_COMPLIANT: [STATUS_FAILED, STATUS_ONGOING, STATUS_IMPLEMENTED, STATUS_FAILED, STATUS_NON_COMPLIANT, STATUS_AUDITED],
        STATUS_AUDITED: [STATUS_FAILED, STATUS_ONGOING, STATUS_IMPLEMENTED, STATUS_FAILED, STATUS_NON_COMPLIANT],
    }

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
    def status_text(cls, status):
        for status_text in cls.STATUSES:
            if status == status_text[0]:
                return status_text[1]
        return "None"

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
        return cls.STATUS_URGENCY[b] - cls.STATUS_URGENCY[a]

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

    #@property
    #def statements(self):
    #    return [cs.statement for cs in self.constraint_statements(manager='unscoped').all()]

    def target_statuses(self):
        return self.STATUS_TRANSITIONS[self.status]

    def __str__(self):
        return self.text or self.slug

    class Meta:
        ordering = ('index',)

    def get_goal(self):
        return (self.category.slug + '_' + self.slug).replace("-", "_")


class ConstraintDefinition(TenantAwareOrderedModelBase):
    constraint = models.ForeignKey(Constraint, on_delete=models.CASCADE, null=True)
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE, null=True)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    order_field_name = 'index'
    order_with_respect_to = 'constraint'

    class Meta:
        ordering = ('index',)


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


class DataManagementPlan(TenantAwareOrderedModelBase):
    """
    The planned approach for managing data
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, related_name='data_management_plans')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='data_managements', verbose_name='Team responsible for this data type')
    data_management = models.ForeignKey(DataManagement, null=True, on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField(editable=False, db_index=True, default=0)

    PLAN_NOT_DEFINED = "not-defined"
    PLAN_KEEP = "keep"
    PLAN_IMPLEMENT = "implement"
    PLAN_ANOTHER_PROJECT = "another-project"
    PLAN_POSTPONE = "postpone"

    PLANS = [
        (PLAN_NOT_DEFINED, _("Not defined")),
        (PLAN_KEEP, _("Keep the existing status")),
        (PLAN_IMPLEMENT, _("Implement in this project")),
        (PLAN_ANOTHER_PROJECT, _("Implemented in another project")),
        (PLAN_POSTPONE, _("Postpone integration")),
    ]

    plan = models.CharField(max_length=32, choices=PLANS, default=PLAN_NOT_DEFINED)

    @classmethod
    def is_valid_plan(cls, status):
        for p in cls.PLANS:
            if status == p[0]:
                return True
        return False

    order_field_name = 'index'

    def __str__(self):
        cls = self.content_type.model_class()
        return cls._meta.verbose_name + ': ' + self.get_policy_display()

    class Meta:
        ordering = ('index',)
