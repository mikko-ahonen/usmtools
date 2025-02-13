import logging

from django.urls import reverse_lazy
from django_components import component

from mir.models import Document
from workflows.tenant import current_tenant_id
from components.tags.tags import Tags

logger = logging.getLogger(__name__)

@component.register("document_tags")
class DocumentTags(Tags):
    entity_class = Document

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:document-tags', kwargs={'tenant_id': tenant_id})
