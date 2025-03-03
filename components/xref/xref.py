import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref")
class Xref(component.Component):
    template_name = "xref/xref.html"

    def get_context_data(self, **kwargs):

        xref = kwargs["xref"]
        highlighted_requirement = kwargs["highlighted_requirement"]
        highlighted_statement = kwargs["highlighted_statement"]
        highlighted_constraint = kwargs["highlighted_constraint"]

        return {
            "xref": xref,
            "highlighted_requirement": highlighted_requirement,
            "highlighted_statement": highlighted_statement,
            "highlighted_constraint": highlighted_constraint,
        }
