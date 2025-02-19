from django_components import component

from .entity_selector import EntitySelector
from workflows.models import Responsibility, Profile
from workflows.tenant import current_tenant_id
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

@component.register("responsibility_profile_selector")
class ResponsibilityProfileSelector(EntitySelector):
    entity_class = Responsibility
    entity_target = 'p'
    value_attr = 'profile'
    value_class = Profile
    search_placeholder = _('Profile')

    def get_entity_url(sef, entity):
        tenant_id = current_tenant_id()
        return reverse_lazy('components:responsibility-select-profile', kwargs={'tenant_id': tenant_id})
