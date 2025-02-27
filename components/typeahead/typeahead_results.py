import re
import uuid
from django_components import component
from workflows.tenant import current_tenant_id
from workflows.tenant_models import tenant_check


from workflows.search import search_routines, search_profiles, search_organization_units
from mir.search import search_documents, search_risks

from django.db.models import Q
from taggit.models import Tag

def is_valid_uuid(s):
    try:
        uuid.UUID(str(s))
        return True
    except ValueError:
        return False

@component.register("typeahead_results")
class TypeaheadResults(component.Component):
    template_name = "typeahead/typeahead_results.html"

    def post(self, request, *args, **kwargs):
        tenant_id = current_tenant_id()
        tenant_check(request=request, tenant_id=tenant_id)

        q = request.POST.get('q') # query string
        t = request.POST.get('t') # type of search
        if q is None or q == "" or t is None or t == "":
            results = []
        else:
            if t in ["r", "routine"]:
                results = [{'id': r.id, 'name': str(r), 'type': 'r'} for r in search_routines(q)]
            elif t in ["d", "document"]:
                results = [{'id': r.id, 'name': str(r), 'type': 'd'} for r in search_documents(q)]
            elif t in ["risk"]:
                results = [{'id': r.id, 'name': str(r), 'type': 'd'} for r in search_risks(q)]
            elif t in ["o", "organization_unit"]:
                results = [{'id': r.id, 'name': str(r), 'type': 'o'} for r in search_organization_units(q)]
            elif t in ["p", "profile"]:
                results = [{'id': r.id, 'name': str(r), 'type': 'r'} for r in search_profiles(q)]
            elif t == "t":
                results = [{'id': r.id, 'name': r.name, 'type': 't'} for r in Tag.objects.filter(name__startswith=q)]
                print(results)
            else:
                raise ValueError(f"Invalid search type: {t}")

        context = {
            "type": t,
            "results": results,
        }
        return self.render_to_response(context=context, slots={}, kwargs={})

    class Media:
        css = "typeahead/typeahead_results.css"
