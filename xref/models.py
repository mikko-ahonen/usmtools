import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from compliances.models import Domain
from ordered_model.models import OrderedModelBase, OrderedModelManager

class CrossReference(OrderedModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='standards_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='standards_modified')
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)
    order_field_name = 'index'
    domain = models.OneToOneField(Domain, on_delete=models.CASCADE, related_name='cross_reference', null=True, blank=True)

    class Meta:
        ordering = ('index',)

    def __str__(self):
        return self.name
