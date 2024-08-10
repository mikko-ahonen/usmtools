import logging

from django_components import component

logger = logging.getLogger(__name__)

@component.register("typeahead")
class Typeahead(component.Component):
    template_name = "typeahead/typeahead.html"

    def get_context_data(self, **kwargs):
        if "target" not in kwargs:
            raise ValueError("target required")
        if "x-model" not in kwargs:
            raise ValueError("x-model required")
        return {
            "placeholder": kwargs.get("placeholder", None),
            "x_model": kwargs["x-model"],
            "target": kwargs["target"],
            "component_id": self.component_id,
        }

    class Media:
        css = "typeahead/typeahead.css"

