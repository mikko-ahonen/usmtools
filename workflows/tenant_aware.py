from ordered_model.models import OrderedModelBase, OrderedModelQuerySet, OrderedModelManager
from tree_queries.query import TreeQuerySet

from django.db.models import Manager, QuerySet
from .tenant import current_tenant_id

class TenantAwareManager(Manager):
    def get_queryset(self):
        tenant_id = current_tenant_id()

        # If the manager was built from a queryset using
        # SomeQuerySet.as_manager() or SomeManager.from_queryset(),
        # we want to use that queryset instead of TenantAwareQuerySet.
        if self._queryset_class != TenantAwareQuerySet:
            return super().get_queryset().filter(tenant_id=tenant_id)

        return TenantAwareQuerySet(self.model, using=self._db).filter(
            tenant_id=tenant_id
        )

class TenantAwareTreeManager(Manager):
    def get_queryset(self):
        tenant_id = current_tenant_id()

        # If the manager was built from a queryset using
        # SomeQuerySet.as_manager() or SomeManager.from_queryset(),
        # we want to use that queryset instead of TenantAwareQuerySet.
        if self._queryset_class != TenantAwareTreeQuerySet:
            return super().get_queryset().filter(tenant_id=tenant_id)

        return TenantAwareTreeQuerySet(self.model, using=self._db).filter(
            tenant_id=tenant_id
        )

class TenantAwareOrderedManager(OrderedModelManager):
    def get_queryset(self):
        tenant_id = current_tenant_id()

        # If the manager was built from a queryset using
        # SomeQuerySet.as_manager() or SomeManager.from_queryset(),
        # we want to use that queryset instead of TenantAwareQuerySet.
        if self._queryset_class != TenantAwareOrderedQuerySet:
            return super().get_queryset().filter(tenant_id=tenant_id)

        return TenantAwareOrderedQuerySet(self.model, using=self._db).filter(
            tenant_id=tenant_id
        )

class TenantAwareQuerySet(QuerySet):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        objs = list(objs)
        for o in objs:
            o.tenant = current_tenant()

        super().bulk_create(objs, batch_size, ignore_conflicts)

    def as_manager(cls):
        manager = TenantAwareManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True

    as_manager = classmethod(as_manager)

class TenantAwareTreeQuerySet(TreeQuerySet):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        objs = list(objs)
        for o in objs:
            o.tenant = current_tenant()

        super().bulk_create(objs, batch_size, ignore_conflicts)

    def as_manager(cls):
        manager = TenantAwareTreeManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True

    as_manager = classmethod(as_manager)

class TenantAwareOrderedQuerySet(OrderedModelQuerySet):
    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        objs = list(objs)
        for o in objs:
            o.tenant = current_tenant()

        super().bulk_create(objs, batch_size, ignore_conflicts)

    def as_manager(cls):
        manager = TenantAwareOrderedManager.from_queryset(cls)()
        manager._built_with_as_manager = True
        return manager

    as_manager.queryset_only = True

    as_manager = classmethod(as_manager)
