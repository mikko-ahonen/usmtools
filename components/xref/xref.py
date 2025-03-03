import logging

from django_components import component
from compliances.models import Statement, Constraint, Requirement

@component.register("xref")
class Xref(component.Component):
    template_name = "xref/xref.html"

    def get_context_data(self, **kwargs):

        xref = kwargs["xref"]

        return {
            "xref": xref,
            "selected_type": 'Requirement',
            "selected_id": self.get_first_requirement(xref.domain.root_sections),
        }

    def get_first_requirement(self, sections):
        for section in sections:
            for requirement in section.requirements.all():
                return requirement.id
            req = self.get_first_requirement(section.children.all())
            if req:
                return req
        return None
