import logging

from workflows.tenant import current_tenant_id

from django_components import component
from workflows.models import Action

@component.register("action")
class Action(component.Component):
    template_name = "action/action.html"

    def get_context_data(self, **kwargs):

        tenant_id = current_tenant_id()

        action = kwargs.get("action", None)
        if not action:
            raise ValueError("action is required")

        return {
            "action": action,
            "tenant_id": tenant_id,
        }
