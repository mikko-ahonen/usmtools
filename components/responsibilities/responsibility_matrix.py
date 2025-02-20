import logging

from django.http import QueryDict
from django.core.exceptions import SuspiciousOperation

from django_components import component

from workflows.tenant import current_tenant_id
from workflows.models import Action, Responsibility

@component.register("responsibility_matrix")
class ResponsibilityMatrix(component.Component):
    template_name = "responsibilities/responsibility_matrix.html"

    def get_context_data(self, **kwargs):

        tenant_id = current_tenant_id()

        routine = kwargs.get("routine", None)
        if not routine:
            raise ValueError("routine is required")

        return {
            "routine": routine,
            "tenant_id": tenant_id,
        }
