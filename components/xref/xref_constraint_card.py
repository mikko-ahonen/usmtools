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

        return {
            "constraint": constraint,
            "statement": statement,
            "next_constraint": next_constraint,
            "prev_constraint": prev_constraint,
        }   
