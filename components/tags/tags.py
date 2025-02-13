import logging

from django_components import component
from django.http import QueryDict
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)

@component.register("tags")
class Tags(component.Component):
    template_name = "tags/tags.html"

    def get_context_data(self, **kwargs):
        if not self.entity_class:
            raise ValueError("instantiate through subclass")
        if not 'entity' in kwargs:
            raise ValueError("entity is required")

        entity = kwargs['entity']
        tags = self.get_entity_tags(entity)
        url = self.get_entity_url(entity)

        ctx = {
            'entity': entity,
            'tags': tags,
            'url': url,
            'target': 't',
        }
        ctx.update(self.get_extra_context_data(entity))
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
        raise ValueError(f"Entity not found with id {entity_id}")

    def delete(self, request, *args, **kwargs):
        qd = request.GET
        entity = self.get_entity(qd)
        removed_tag_id = self.get_param(qd, 'removed_tag_id')
        removed_tag_name = self.get_param(qd, 'removed_tag_name')
        self.remove_tag(entity, removed_tag_id, removed_tag_name)
        context = self.get_context_data(entity=entity)
        return self.render_to_response(context=context, slots={}, kwargs={'entity': entity})

    def post(self, request, *args, **kwargs):
        qd = QueryDict(request.body)
        entity = self.get_entity(qd)
        added_tag_id = self.get_param(qd, 'added_tag_id')
        added_tag_name = self.get_param(qd, 'added_tag_name')
        self.add_tag(entity, added_tag_id, added_tag_name)
        context = self.get_context_data(entity=entity)
        return self.render_to_response(context=context, slots={}, kwargs={'entity': entity})

    def get_extra_context_data(self, entity):
        return { }
        
    def get_entity_tags(self, entity):
        return entity.tags.all()

    def add_tag(self, entity, tag_id, tag_name):
        entity.tags.add(tag_name)

    def remove_tag(self, entity, tag_id, tag_name):
        entity.tags.remove(tag_name)
