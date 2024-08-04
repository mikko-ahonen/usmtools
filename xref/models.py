import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModelBase, OrderedModelManager

class Standard(OrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='standards_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='standards_modified')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'

    class Meta:
        ordering = ('index',)

    def __str__(self):
        return self.name


class Control(OrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='controls')
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='controls_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='controls_modified')

    CONTROL_STATUS_DRAFT = "draft"
    CONTROL_STATUS_READY = "ready"
    CONTROL_STATUS_APPROVED = "approved"
    CONTROL_STATUS_CHOICES = [
        (CONTROL_STATUS_DRAFT, _("Draft")),
        (CONTROL_STATUS_READY, _("Ready")),
        (CONTROL_STATUS_APPROVED, _("Approved")),
    ]
    status = models.CharField(max_length=10, choices=CONTROL_STATUS_CHOICES, default=CONTROL_STATUS_DRAFT)

    order_with_respect_to = 'standard'
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'

    class Meta:
        ordering = ('index',)


    def __str__(self):
        return self.name


class Requirement(OrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='requirements')
    name = models.CharField(max_length=255)
    text = models.TextField()
    start_pos = models.IntegerField(help_text='Starting position of text in control text field')
    end_pos = models.IntegerField(help_text='Ending position of text in control text field')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='requirements_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='requirements_modified')

    REQUIREMENT_STATUS_DRAFT = "draft"
    REQUIREMENT_STATUS_READY = "ready"
    REQUIREMENT_STATUS_APPROVED = "approved"
    REQUIREMENT_STATUS_CHOICES = [
        (REQUIREMENT_STATUS_DRAFT, _("Draft")),
        (REQUIREMENT_STATUS_READY, _("Ready")),
        (REQUIREMENT_STATUS_APPROVED, _("Approved")),
    ]
    status = models.CharField(max_length=10, choices=REQUIREMENT_STATUS_CHOICES, default=REQUIREMENT_STATUS_DRAFT)

    order_with_respect_to = 'control'
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'

    class Meta:
        ordering = ('index',)


    def __str__(self):
        return self.name


class Statement(OrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='statements')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='statements_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='statements_modified')

    STATEMENT_STATUS_DRAFT = "draft"
    STATEMENT_STATUS_READY = "ready"
    STATEMENT_STATUS_APPROVED = "approved"
    STATEMENT_STATUS_CHOICES = [
        (STATEMENT_STATUS_DRAFT, _("Draft")),
        (STATEMENT_STATUS_READY, _("Ready")),
        (STATEMENT_STATUS_APPROVED, _("Approved")),
    ]
    status = models.CharField(max_length=10, choices=STATEMENT_STATUS_CHOICES, default=STATEMENT_STATUS_DRAFT)

    order_with_respect_to = 'requirement'
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'

    class Meta:
        ordering = ('index',)


    def __str__(self):
        return self.text


class StatementToSubstatement(OrderedModelBase):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)
    substatement = models.ForeignKey('Substatement', on_delete=models.CASCADE)

    order_with_respect_to = 'statement'
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'

    class Meta:
        ordering = ('index',)


    class Meta:
        ordering = ('substatement',)
        unique_together = (('statement', 'substatement'),)


class Substatement(OrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    statements = models.ManyToManyField(Statement, related_name='substatements', through='StatementToSubstatement')
    subject = models.CharField(max_length=255)
    predicate = models.CharField(max_length=255)
    object = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='substatements_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='substatements_modified')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'

    class Meta:
        ordering = ('index',)


    def __str__(self):
        return self.subject + ' ' + self.predicate + ' ' + self.object
