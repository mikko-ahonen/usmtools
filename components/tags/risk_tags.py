import logging

from django.urls import reverse_lazy
from django_components import component

from mir.models import Risk
from workflows.tenant import current_tenant_id
from components.tags.tags import Tags

logger = logging.getLogger(__name__)

@component.register("risk_tags")
class RiskTags(Tags):
    entity_class = Risk

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:risk-tags', kwargs={'tenant_id': tenant_id})
