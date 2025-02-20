import logging

from django.urls import reverse_lazy
from django_components import component

from workflows.models import Action
from workflows.tenant import current_tenant_id
from components.tags.tags import Tags

logger = logging.getLogger(__name__)

@component.register("action_tags")
class ActionTags(Tags):
    entity_class = Action

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:action-tags', kwargs={'tenant_id': tenant_id})
