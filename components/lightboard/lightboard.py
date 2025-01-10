import logging

from django_components import component
from compliances.models import Section

@component.register("lightboard")
class Lightboard(component.Component):
    template_name = "lightboard/lightboard.html"

    def get_context_data(self, **kwargs):

        if "tenant_id" not in kwargs:
            raise ValueError("tenant_id required")

        tenant_id = kwargs["tenant_id"]

        if "domain" not in kwargs:
            raise ValueError("domain required")

        domain = kwargs["domain"]

        sections = Section.unscoped.filter(tenant_id=tenant_id, domain_id=domain.id).with_tree_fields()

        return {
            "domain": domain,
            "sections": sections,
            "tenant_id": tenant_id,
        }

    class Media:
        pass
        #css = "board/board.css"
        #js = "board/board.js"
