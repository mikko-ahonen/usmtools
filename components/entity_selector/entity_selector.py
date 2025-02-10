import logging

from django_components import component
from django.http import QueryDict
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from workflows.tenant import current_tenant_id

logger = logging.getLogger(__name__)

class EntitySelector(component.Component):
    template_name = "entity_selector/entity_selector.html"

    def get_context_data(self, **kwargs):
        if not self.entity_class:
            raise ValueError("instantiate through subclass")

        entity = kwargs['entity']
        url = self.get_entity_url(entity)
        value = self.get_value(entity)

        ctx = {
            'entity': entity,
            'initial_value': { 'id': value.id if value else None, 'name': value.name if value else None },
            'url': url,
            'target': self.entity_target,
            'search_placeholder': self.search_placeholder,
        }
        return ctx

    def get_param(self, qd, name):
        v = qd.get(name)
        if v and v != '' and v != 'None':
            return v
        return None

    def get_entity(self, qd):
        entity_id = self.get_param(qd, 'entity_id')
        if entity_id:
            entity = self.entity_class.objects.get(id=entity_id)
            return entity
        raise ValueError(f"Entity not found with id {entity_id} and class {self.entity_class}")

    def get_value(self, qd):
        value_id = self.get_param(qd, 'value_id')
        if value_id:
            value = self.value_class.objects.get(id=value_id)
            return value
        raise ValueError(f"Value not found with id {value_id} and class {self.value_class}")

    def delete(self, request, *args, **kwargs):
        qd = request.GET
        entity = self.get_entity(qd)
        removed_value_id = self.get_param(qd, 'removed_value_id')
        removed_value_name = self.get_param(qd, 'removed_value_name')
        self.delete_value(entity, removed_value_id, removed_value_name)
        entity.save()
        context = self.get_context_data(entity=entity)
        return self.render_to_response(context=context, slots={}, kwargs={'entity': entity})

    def post(self, request, *args, **kwargs):
        qd = QueryDict(request.body)
        entity = self.get_entity(qd)
        value_id = self.get_param(qd, 'value_id')
        value_name = self.get_param(qd, 'value_name')
        self.set_value(entity, value_id, value_name)
        entity.save()
        context = self.get_context_data(entity=entity)
        return self.render_to_response(context=context, slots={}, kwargs={'entity': entity})

    def get_value(self, entity):
        return getattr(entity,self.value_attr)

    def set_value(self, entity, value_id, vaölue_name):
        setattr(entity, self.value_attr + '_id', value_id)

    def delete_value(self, entity, value_id, value_name):
        setattr(entity, self.value_attr, None)
