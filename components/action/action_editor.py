import logging

from django.http import QueryDict
from django.core.exceptions import SuspiciousOperation

from django_components import component

from workflows.tenant import current_tenant_id
from workflows.models import Action, Responsibility

@component.register("action_editor")
class ActionEditor(component.Component):
    template_name = "action/action_editor.html"

    def get_context_data(self, **kwargs):

        tenant_id = current_tenant_id()

        action = kwargs.get("action", None)
        if not action:
            raise ValueError("action is required")

        return {
            "action": action,
            "tenant_id": tenant_id,
        }


    def get_param(self, qd, name):
        v = qd.get(name)
        if v and v != '' and v != 'None':
            return v
        return None

    def delete(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()
        responsibility_id = kwargs.get('responsibility_id', None)
        responsibility = Responsibility.objects.get(tenant_id=tenant_id, id=responsibility_id)
        action = responsibility.action
        if tenant_id != str(responsibility.tenant_id):
            raise SuspiciousOperation(f"Parameter tenant_id {tenant_id} while responsibility tenant_id {responsibility.tenant_id}")
        if tenant_id != str(action.tenant_id):
            raise SuspiciousOperation(f"Parameter tenant_id {tenant_id} while action tenant_id {action.tenant_id}")
        responsibility.delete()
        context = self.get_context_data(tenant_id=tenant_id, action=action)
        return self.render_to_response(context=context, slots={}, kwargs={'tenant_id': tenant_id, 'action': action})

    def post(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()
        action_id = kwargs.get('action_id', None)
        action = Action.objects.get(tenant_id=tenant_id, id=action_id)
        if tenant_id != str(action.tenant_id):
            raise SuspiciousOperation(f"Parameter tenant_id {tenant_id} while action tenant_id {action.tenant_id}")
        responsibility = Responsibility.objects.create(action=action, tenant_id=tenant_id, created_by=request.user, modified_by=request.user)

        context = self.get_context_data(tenant_id=tenant_id, action=action)
        return self.render_to_response(context=context, slots={}, kwargs={'tenant_id': tenant_id, 'action': action})

