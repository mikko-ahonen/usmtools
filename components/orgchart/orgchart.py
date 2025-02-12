import logging

from django_components import component
from compliances.models import Section

@component.register("orgchart")
class OrgChart(component.Component):
    template_name = "orgchart/orgchart.html"
    js_file = "orgchart.js"
    css_file = "orgchart.css"

    def get_context_data(self, **kwargs):

        if "tenant_id" not in kwargs:
            raise ValueError("tenant_id required")

        tenant_id = kwargs["tenant_id"]

        org_unit = kwargs["org_unit"]

        return {
            "org_unit": org_unit,
            "orgchart_data": self.org_unit_as_orgchart_data(org_unit),
            "tenant_id": tenant_id,
        }

    def org_unit_as_orgchart_data(self, org_unit):
        return {
            'name': org_unit.name,
            'className': 'test',
            'children': [self.org_unit_as_orgchart_data(x) for x in org_unit.children.all()],
        }
