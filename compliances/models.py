import uuid

from django.db import models
from django.conf import settings

from workflows.tenant_models import Model, OrderedModel, TreeModel

class Domain(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

class Section(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order_with_respect_to = 'domain'

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('index',)
        unique_together = ('domain', 'index',)

class Requirement(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order_with_respect_to = 'section'

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('index',)
        unique_together = ('section', 'index',)

class Constraint(OrderedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    order_with_respect_to = 'requirement'

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('index',)
        unique_together = ('requirement', 'index',)

    def get_goal(self):
        return self.requirement.section.domain.slug + '_' + self.requirement.section.slug + '_' + self.requirement.slug + '_' + self.slug
