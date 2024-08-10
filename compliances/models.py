import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from workflows.tenant_models import Model, OrderedModel, TreeModel

class Domain(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or self.slug

class Section(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True, related_name='sections')
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order_with_respect_to = 'domain'

    def __str__(self):
        return self.title or self.slug

    class Meta:
        ordering = ('index',)
        unique_together = ('domain', 'index',)

class Requirement(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='requirements')
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order_with_respect_to = 'section'

    def __str__(self):
        return self.text or self.slug

    class Meta:
        ordering = ('index',)
        unique_together = ('section', 'index',)

class Term(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    definition = models.CharField(max_length=255, blank=True, null=True)

class Constraint(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, null=True, related_name='constraints')
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    STATUS_NEW = "new"
    STATUS_IMPLEMENTED = "implemented"
    STATUS_FAILED = "failed"
    STATUS_NON_COMPLIANT = "non-compliant"
    STATUS_COMPLIANT = "compliant"
    STATUS_AUDITED = "audited"
    STATUSES = [
        (STATUS_NEW, _("New")),
        (STATUS_IMPLEMENTED, _("Implemented")),
        (STATUS_FAILED, _("Failed")),
        (STATUS_NON_COMPLIANT, _("Non-compliant")),
        (STATUS_COMPLIANT, _("Compliant")),
        (STATUS_AUDITED, _("Audited")),
    ]
    status = models.CharField(max_length=32, choices=STATUSES, default=STATUS_NEW)

    order_with_respect_to = 'requirement'

    def __str__(self):
        return self.text or self.slug

    class Meta:
        ordering = ('index',)
        unique_together = ('requirement', 'index',)

    def get_goal(self):
        return (self.requirement.section.domain.slug + '_' + self.requirement.section.slug + '_' + self.requirement.slug + '_' + self.slug).replace("-", "_")
