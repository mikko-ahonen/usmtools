import logging

from django_components import component
from django.http import QueryDict
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from compliances.entity_types import get_class_by_entity_type

from workflows.tenant import current_tenant_id
from compliances.models import Domain, Constraint, Definition

logger = logging.getLogger(__name__)

@component.register("constraint_references")
class ConstraintReferences(component.Component):
    template_name = "constraint_references/constraint_references.html"

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

        definition = kwargs.get('definition', None)
        if not definition:
            raise ValueError("definition is required")

        ctx = {
            'tenant_id': tenant_id,
            'domain': domain,
            'constraint': constraint,
            'definition': definition,
        }
        return ctx


    def get_param(self, qd, name):
        v = qd.get(name)
        if v and v != '' and v != 'None':
            return v
        return None

    def get_constraint(self, qd):
        constraint_id = self.get_param(qd, 'constraint_id')
        if constraint_id:
            constraint = Constraint.objects.get(id=constraint_id)
            return constraint
        raise ValueError(f"Constraint not found with id {constraint_id}")

    def get_definition(self, qd):
        definition_id = self.get_param(qd, 'definition_id')
        if definition_id:
            definition = Definition.objects.get(id=definition_id)
            return definition
        raise ValueError(f"Definition not found with id {definition_id}")

    def delete(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()

        domain_id = kwargs.get('domain_id', None)
        if not domain_id:
            raise ValueError("domain_id is required")
        domain = Domain.objects.get(tenant_id=tenant_id, id=domain_id)

        qd = request.GET
        constraint = self.get_constraint(qd)
        definition_id = self.get_param(qd, 'definition_id')
        definition = constraint.definitions.filter(id=definition_id).first()

        if definition.ref_plural:
            raise ValueError("Plurals not yet supported")

        definition.ref_object = None
        definition.save()

        context = self.get_context_data(constraint=constraint, definition=definition, domain=domain)
        return self.render_to_response(context=context, slots={}, kwargs={'domain': domain, 'constraint': constraint, 'definition': definition})

    def post(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()

        domain_id = kwargs.get('domain_id', None)
        if not domain_id:
            raise ValueError("domain_id is required")
        domain = Domain.objects.get(tenant_id=tenant_id, id=domain_id)

        qd = QueryDict(request.body)
        constraint = self.get_constraint(qd)

        definition_id = self.get_param(qd, 'definition_id')
        definition_name = self.get_param(qd, 'definition_name')
        if definition_id:
            definition = self.get_definition(qd)

        if definition.ref_plural:
            raise ValueError("Plurals not yet supported")

        reference_id = self.get_param(qd, 'reference_id')
        if not reference_id:
            raise ValueError("reference_id is required")

        print(reference_id)
        cls = get_class_by_entity_type(definition.ref_entity_type)
        reference = cls.objects.filter(id=reference_id).first()
        definition.ref_object = reference
        definition.save()
        
        context = self.get_context_data(constraint=constraint, definition=definition, domain=domain)
        return self.render_to_response(context=context, slots={}, kwargs={'domain': domain, 'constraint': constraint, 'definition': definition})
