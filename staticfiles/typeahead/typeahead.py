import logging

from django_components import component

logger = logging.getLogger(__name__)

from taggit.models import Tag
from workflows.models import OrganizationUnit, Profile
from mir.models import Document, Risk
from django.utils.translation import gettext as _
from workflows.tenant import current_tenant_id
from workflows.tenant_models import tenant_check

from inflection import pluralize

@component.register("typeahead")
class Typeahead(component.Component):
    template_name = "typeahead/typeahead.html"

    def get_context_data(self, **kwargs):
        new_item = kwargs.get("new_item", None)

        target = kwargs.get('target', None)
        if target is None:
            raise ValueError("target required")
        if "x-model" not in kwargs:
            raise ValueError("x-model required")
        tenant_id = current_tenant_id()
        return {
            "placeholder": self.get_placeholder(target),
            "x_model": kwargs["x-model"],
            "target": target,
            "new_item": new_item,
            "tenant_id": tenant_id,
        }

    def get_placeholder(self, target):
        if target in ['t', 'tags']:
            placeholder = _('Search from tags')
        elif target in ["p", "profile"]:
            placeholder = _('Search from profiles')
        elif target in ["o", "organization_unit"]:
            placeholder = _('Search from organization units')
        elif target in ["d", "document"]:
            placeholder = _('Search from documents')
        elif target in ["task"]:
            placeholder = _('Search from tasks')
        elif target in ["risk"]:
            placeholder = _('Search from risks')
        else:
            raise ValueError(f"Invalid typeahead type: {target}")
        return placeholder + '...'

    def post(self, request, *args, **kwargs):

        logger.error("POSTing")

        tenant_id = current_tenant_id()
        tenant_check(request=request, tenant_id=tenant_id)

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
        if target in ["t", "tags"]:
            new_item, created = Tag.objects.get_or_create(name=new_item_value)
        elif target in ["p", "profile"]:
            new_item, created = Profile.objects.get_or_create(tenant_id=tenant_id, name=new_item_value)
        elif target in ["o", "organization_unit"]:
            new_item, created = OrganizationUnit.objects.get_or_create(tenant_id=tenant_id, name=new_item_value)
        elif target in ["risk"]:
            new_item = Risk.objects.filter(name=new_item_value).first()
        elif target in ["d", "document"]:
            new_item = Document.objects.filter(name=new_item_value).first()
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
