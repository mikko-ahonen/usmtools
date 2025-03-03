import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref_requirement_card")
class XrefRequirementCard(component.Component):
    template_name = "xref/xref_requirement_card.html"

    def get_context_data(self, **kwargs):

        requirement = kwargs["requirement"]
        is_selected = kwargs["is_selected"]
        selected_requirement = kwargs["selected_requirement"]
        next_requirement = kwargs["next_requirement"]
        prev_requirement = kwargs["prev_requirement"]

        return {
            "requirement": requirement,
            "is_selected": is_selected,
            "selected_requirement": selected_requirement,
            "next_requirement": next_requirement,
            "prev_requirement": prev_requirement,
        }
