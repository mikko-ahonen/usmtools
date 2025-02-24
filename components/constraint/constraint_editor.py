import logging

from django_components import component
from django.http import QueryDict
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from compliances.entity_types import get_class_by_entity_type

from workflows.tenant import current_tenant_id
from workflows.tenant_models import tenant_check


from compliances.models import Domain, Constraint, Definition


logger = logging.getLogger(__name__)

@component.register("constraint_editor")
class ConstraintEditor(component.Component):
    template_name = "constraint/constraint_editor.html"

    def get_context_data(self, **kwargs):

        tenant_id = current_tenant_id()
        if not tenant_id:
            raise ValueError("tenant_id is required")

        domain = kwargs.get('domain', None)
        if not domain:
            raise ValueError("domain is required")

        constraint = kwargs.get('constraint', None)
        if not constraint:
            raise ValueError("constraint is required")

        ctx = {
            'tenant_id': tenant_id,
            'domain': domain,
            'constraint': constraint,
        }

        return ctx


    def get_param(self, qd, name):
        v = qd.get(name)
        if v and v != '' and v != 'None':
            return v
        return None


    def get_constraint(self, constraint_id):
        if constraint_id:
            constraint = Constraint.objects.get(id=constraint_id)
            return constraint
        raise ValueError(f"Constraint not found with id {constraint_id}")


    def post(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()

        tenant_check(request=request, tenant_id=tenant_id)

        domain_id = kwargs.get('domain_id', None)
        if not domain_id:
            raise ValueError("domain_id is required")

        domain = Domain.objects.get(tenant_id=tenant_id, id=domain_id)

        constraint_id = kwargs.get('constraint_id', None)
        if not constraint_id:
            raise ValueError("constraint_id is required")

        constraint = self.get_constraint(constraint_id)

        qd = QueryDict(request.body)
        target_status = self.get_param(qd, "target_status")
        if target_status not in Constraint.STATUS_TRANSITIONS[constraint.status]:
            raise ValueError(f"Invalid status transition {constraint.status} => {target_status}")

        constraint.status = target_status
        constraint.save()
        
        context = self.get_context_data(constraint=constraint, domain=domain)
        return self.render_to_response(context=context, slots={}, kwargs={'domain': domain, 'constraint': constraint})
