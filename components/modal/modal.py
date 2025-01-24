#import logging
from django_components import component
from django_components import types as t

#logger = logging.getLogger(__name__)

@component.register("modal")
class Modal(component.Component):
    """
    Create one or more triggers i.e. with hx-get passing the 
    hx-target="#dialog" attribute
    """
    template_name = "modal/modal.html"

    def get_context_data(self):
        return {
        }

    class Media:
        js = "modal/modal.js"
        css = "modal/modal.css"
