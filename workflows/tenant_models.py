import uuid

from django.conf import settings
from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _

from ordered_model.models import OrderedModelBase, OrderedModelManager
from tree_queries.models import TreeNode, TreeQuerySet
from sequences import get_next_value

from .tenant_aware import TenantAwareManager, TenantAwareOrderedManager, TenantAwareTreeManager, TenantAwareTreeQuerySet

class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tenants', null=True, default=None)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
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

    @classmethod
    def get_unscoped_manager_name(cls):
        manager_cls = cls.unscoped
        module = manager_cls.__module__
        return module + '.' + manager_cls.__class__.__name__

    class Meta:
        abstract = True


def get_next_index():
    return get_next_value('index')

class OrderedModel(TenantAwareOrderedModelBase):
    """
    An abstract base class for ordered models.
    """
    index = models.PositiveSmallIntegerField(editable=False, db_index=True, default=get_next_index)

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


def tenant_check(request=None, tenant=None, tenant_id=None):
    if not request:
        raise ValueError("Must have request")
    if tenant_id and not tenant:
        tenant = Tenant.objects.get(id=tenant_id)
    user = request.user
    if user.is_authenticated:
        if user.is_superuser:
            return
        if tenant and tenant.owner_id == user.pk:
            return
    raise PermissionDenied("Not logged in or not tenant owner")
