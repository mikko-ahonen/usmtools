import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref")
class Xref(component.Component):
    template_name = "xref/xref.html"

    def get_context_data(self, **kwargs):

        xref = kwargs["xref"]
        selected_requirement = kwargs["selected_requirement"]
        selected_statement = kwargs["selected_statement"]
        selected_constraint = kwargs["selected_constraint"]

        return {
            "xref": xref,
            "selected_requirement": selected_requirement,
            "selected_statement": selected_statement,
            "selected_constraint": selected_constraint,
        }
