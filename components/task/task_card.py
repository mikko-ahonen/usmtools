import logging

from django.http import QueryDict
from django.core.exceptions import SuspiciousOperation

from django_components import component

from workflows.tenant import current_tenant_id
from workflows.models import Action, Responsibility

@component.register("task_card")
class TaskCard(component.Component):
    template_name = "task/task_card.html"

    def get_context_data(self, **kwargs):

        tenant_id = current_tenant_id()

        task = kwargs.get("task", None)
        if not task:
            raise ValueError("task is required")

        return {
            "task": task,
            "tenant_id": tenant_id,
        }
