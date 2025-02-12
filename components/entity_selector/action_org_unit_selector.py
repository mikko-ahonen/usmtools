from django_components import component

from .entity_selector import EntitySelector
from workflows.models import Action, OrganizationUnit
from workflows.tenant import current_tenant_id
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

@component.register("action_org_unit_selector")
class ActionOrgUnitSelector(EntitySelector):
    entity_class = Action
    entity_target = 'o'
    value_attr = 'organization_unit'
    value_class = OrganizationUnit
    search_placeholder = _('Organization')

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:action-select-org-unit', kwargs={'tenant_id': tenant_id})
