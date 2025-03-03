import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref_statement_card")
class XrefStatementCard(component.Component):
    template_name = "xref/xref_statement_card.html"

    def get_context_data(self, **kwargs):

        statement = kwargs["statement"]
        is_selected = kwargs["is_selected"]
        selected_statement = kwargs["selected_statement"]
        selected_constraint = kwargs["selected_constraint"]
        next_statement = kwargs["next_statement"]
        prev_statement = kwargs["prev_statement"]

        return {
            "statement": statement,
            "is_selected": is_selected,
            "selected_statement": selected_statement,
            "selected_constraint": selected_constraint,
            "next_statement": next_statement,
            "prev_statement": prev_statement,
        }
