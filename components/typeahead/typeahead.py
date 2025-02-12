import logging

from django_components import component

logger = logging.getLogger(__name__)

from taggit.models import Tag
from workflows.tenant import current_tenant_id
from workflows.models import OrganizationUnit, Profile

@component.register("typeahead")
class Typeahead(component.Component):
    template_name = "typeahead/typeahead.html"

    def get_context_data(self, **kwargs):
        new_item = kwargs.get("new_item", None)

        if "target" not in kwargs:
            raise ValueError("target required")
        if "x-model" not in kwargs:
            raise ValueError("x-model required")
        tenant_id = current_tenant_id()
        return {
            "placeholder": kwargs.get("placeholder", None),
            "x_model": kwargs["x-model"],
            "target": kwargs["target"],
            "new_item": new_item,
            "tenant_id": tenant_id,
        }

    def post(self, request, *args, **kwargs):

        logger.error("POSTing")
        placeholder = request.POST.get('placeholder')

        x_model = request.POST.get('x_model')
        if not x_model:
            raise ValueError(f"x_model required")

        new_item_value = request.POST.get('new_item_value')
        logger.error(f"new_item_value {new_item_value}")
        if not new_item_value:
            raise ValueError(f"new_item_value required")

        target = request.POST.get('t')
        logger.error(f"target {target}")
        if target == "t":
            new_item, created = Tag.objects.get_or_create(name=new_item_value)
        elif target == "p":
            new_item, created = Profile.objects.get_or_create(name=new_item_value)
        elif target == "o":
            new_item, created = OrganizationUnit.objects.get_or_create(name=new_item_value)
        else:
            raise ValueError(f"Invalid typeahead type: {target}")

        context = self.get_context_data(**{
            "placeholder": placeholder,
            "x-model": x_model,
            "target": target,
            "new_item": new_item,
        })

        return self.render_to_response(context, {}, kwargs={'target': target, 'x-model': x_model, 'placeholder': placeholder, 'new_item': new_item})

    class Media:
        css = "typeahead/typeahead.css"
