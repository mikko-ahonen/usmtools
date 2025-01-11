import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from workflows.tenant_models import TenantAwareModelBase

class Dataset(TenantAwareModelBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    object_id = models.UUIDField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    @property
    def datapoints(self, object):
        return self.datapoint_set(manager='unscoped').filter(tenant_id=self.tenant_id).order_by('date')

    @classmethod
    def by_object(cls, tenant_id, object):
        content_type = ContentType.objects.get_for_model(object)
        return cls.unscoped.get(tenant_id=tenant_id, object_id=object.id, content_type=content_type)

class Datapoint(TenantAwareModelBase):
    date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
