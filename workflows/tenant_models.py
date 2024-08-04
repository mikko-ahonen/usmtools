import uuid

from django.conf import settings
from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModelBase, OrderedModelManager
from tree_queries.models import TreeNode, TreeQuerySet

from .tenant_aware import TenantAwareManager, TenantAwareOrderedManager, TenantAwareTreeManager, TenantAwareTreeQuerySet

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tenants', null=True, default=None)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='tenants_created')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='tenants_modified')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('tenant')
        verbose_name_plural = _('tenants')

class TenantAwareOrderedModelBase(OrderedModelBase):
    """
    An abstract base class model that provides a foreign key to a Tenant, plus ordering
    """

    tenant = models.ForeignKey(Tenant, models.CASCADE, null=True)

    objects = TenantAwareOrderedManager()
    unscoped = OrderedModelManager()

    class Meta:
        abstract = True

class OrderedModel(TenantAwareOrderedModelBase):
    """
    An abstract base class for ordered models.
    """
    index = models.PositiveSmallIntegerField(editable=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        abstract = True
        ordering = ('index',)

    order_field_name = 'index'

class TenantAwareModelBase(models.Model):
    """
    An abstract base class model that provides a foreign key to a Tenant
    """

    tenant = models.ForeignKey(Tenant, models.CASCADE, null=True)

    objects = TenantAwareManager()
    unscoped = models.Manager()

    class Meta:
        abstract = True


class Model(TenantAwareModelBase):
    """
    An abstract base class for models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    class Meta:
        abstract = True


class TenantAwareTreeModelBase(TreeNode):

    """
    An abstract base class model that provides a foreign key to a Tenant, plus tree structure
    """

    tenant = models.ForeignKey(Tenant, models.CASCADE, null=True)

    objects = TenantAwareTreeQuerySet.as_manager()
    unscoped = TreeQuerySet.as_manager()

    class Meta:
        default_manager_name = 'objects'
        abstract = True

class TreeModel(TenantAwareTreeModelBase):
    """
    An abstract base class for tree models.
    """

    class Meta:
        abstract = True

