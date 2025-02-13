import logging

from django.urls import reverse_lazy
from django_components import component

from workflows.models import Routine
from workflows.tenant import current_tenant_id
from components.tags.tags import Tags

logger = logging.getLogger(__name__)

@component.register("routine_tags")
class RoutineTags(Tags):
    entity_class = Routine

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:routine-tags', kwargs={'tenant_id': tenant_id})

    #def get_extra_context_data(self, entity):
    #    return { 'timeline_id': entity.timeline_id }
