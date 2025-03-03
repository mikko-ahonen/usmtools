import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref_document")
class XrefDocument(component.Component):
    template_name = "xref/xref_document.html"

    def get_context_data(self, **kwargs):

        xref = kwargs["xref"]
        highlighted_requirement = kwargs["highlighted_requirement"]
        highlighted_statement = kwargs["highlighted_statement"]

        return {
            "xref": xref,
            "highlighted_requirement": highlighted_requirement,
            "highlighted_statement": highlighted_statement,
        }
