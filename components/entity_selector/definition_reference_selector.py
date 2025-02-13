from django_components import component

from .entity_selector import EntitySelector
from compliances.models import Definition
from workflows.tenant import current_tenant_id
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from compliances.entity_types import EntityType, get_class_by_entity_type

@component.register("definition_reference_selector")
class DefinitionReferenceSelector(EntitySelector):
    entity_class = Definition
    value_attr = 'ref_object'
    search_placeholder = _('Profile')

    def get_entity_target(self, entity):
        return entity.ref_entity_type

    def get_value_class(self, entity):
        cls = get_class_by_entity_type(entity.ref_entity_type)
        return cls

    def get_search_placeholder(self, entity):
        cls = get_class_by_entity_type(entity.ref_entity_type)
        return cls._meta.verbose_name

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:definition-select-reference', kwargs={'tenant_id': tenant_id, 'entity_type': entity.ref_entity_type})

    def set_value(self, entity, value_id, value_name):
        cls = self.get_value_class(entity)
        obj = cls.objects.get(id=value_id)
        setattr(entity, self.value_attr, obj)
