import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref_constraint_card")
class XrefConstraintCard(component.Component):
    template_name = "xref/xref_constraint_card.html"

    def get_context_data(self, **kwargs):

        statement = kwargs["statement"]
        constraint = kwargs["constraint"]
        next_constraint = kwargs["next_constraint"]
        prev_constraint = kwargs["prev_constraint"]

        statuses = Statement.XREF_STATUSES

        return {
            "statuses": statuses,
            "constraint": constraint,
            "statement": statement,
            "next_constraint": next_constraint,
            "prev_constraint": prev_constraint,
        }   

    def get_statement(self, obj_id):
        try:
            return Statement.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    def get_constraint(self, obj_id):
        try:
            return Constraint.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    def get_status(self, target_status):
        for k, v in Constraint.XREF_STATUSES:
            if target_status == k:
                return target_status
        raise ValueError(f"Invalid target status {target_status} for instance of constraint")

    def post(self, request, statement_id, obj_id, target_status):
        statement = self.get_statement(statement_id)
        obj = self.get_constraint(obj_id)
        next_constraint_id = request.POST.get('next_constraint_id', None)
        next_constraint = None
        if next_constraint_id:
            next_constraint = self.get_constraint(next_constraint_id)
        prev_constraint_id = request.POST.get('prev_constraint_id', None)
        prev_constraint = None
        if prev_constraint_id:
            prev_constraint = self.get_constraint(prev_constraint_id)
        status = self.get_status(target_status)
        obj.xref_status = status
        obj.save()
        kwargs = {
            "statement": statement,
            "constraint": obj,
            "next_constraint": next_constraint,
            "prev_constraint": prev_constraint,
        }
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context=context, slots={}, kwargs=kwargs)

