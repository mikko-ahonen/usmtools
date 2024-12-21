from django import template
from django.utils.html import mark_safe
from django.urls import reverse
from django.utils.translation import gettext as _
from workflows.models import Service, Workflow

register = template.Library()

def mode(edit, tenant):
    edit_trans = _("Edit")
    view_trans = _("View")
    tenant_id = tenant if isinstance(tenant, str) else tenant.id
    if edit:
        view_url = reverse('workflows:user-service-list', kwargs={'tenant_id': tenant_id})
        return f'<a href="{view_url}">{view_trans}</a> | <strong>{edit_trans}</strong>'
    else:
        edit_url = reverse('workflows:service-list', kwargs={'tenant_id': tenant_id})
        return f'<strong>{view_trans}</strong> | <a href="{edit_url}">{edit_trans}</a>'

def header():
    return """
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
"""

def footer():
    return """
  </ol>
</nav>
"""

def breadcrumb_item(name, translate=False, active=False, url=None):
    if active:
        active_class = 'active'
        aria_current = 'aria-current="page"'
    else:
        active_class = ''
        aria_current = ''

    if translate:
        name_translated = _(name)
    else:
        name_translated = name

    if url and not active:
        name_with_url = f'<a href="{url}">{name_translated}</a>'
    else:
        name_with_url = name_translated

    return f'<li class="breadcrumb-item {active_class}" {aria_current}>{name_with_url}</a></li>'

@register.simple_tag
def breadcrumbs(tenant=None, edit=False, page=None, entity=None):
    #text = mode(edit, tenant)
    text = ''
    text += header()
    if tenant:
        text += breadcrumb_item(tenant.name, translate=False, active=False)
    if page == 'services':
        text += breadcrumb_item('Services', translate=True, active=entity is None, url=reverse('workflows:service-list', kwargs={'tenant_id': tenant.id}))
    elif page == 'organizations':
        text += breadcrumb_item('Organizations', translate=True, active=True, url=reverse('workflows:organization-unit-list', kwargs={'tenant_id': tenant.id}))
    elif page == 'profiles':
        text += breadcrumb_item('Profiles', translate=True, active=True, url=reverse('workflows:profile-list', kwargs={'tenant_id': tenant.id}))
    elif page == 'customers':
        text += breadcrumb_item('Customers', translate=True, active=True, url=reverse('workflows:customer-list', kwargs={'tenant_id': tenant.id}))
    else:
        text += breadcrumb_item('Others', translate=True, active=True, url=reverse('workflows:service-list', kwargs={'tenant_id': tenant.id}))

    if isinstance(entity, Service):
        text += breadcrumb_item(_("Service") + ": " + str(entity), active=True, url=reverse('workflows:service-detail', kwargs={'tenant_id': tenant.id, 'pk': entity.id}))
    if isinstance(entity, Workflow):
        if tenant and entity and entity.service:
            service_detail_url = reverse('workflows:service-detail', kwargs={'tenant_id': tenant.id, 'pk': entity.service.id})
            workflow_detail_url = reverse('workflows:workflow-detail', kwargs={'tenant_id': tenant.id, 'pk': entity.id})
        else:
            service_detail_url = None
            workflow_detail_url = None
        text += breadcrumb_item(_("Service") + ": " + str(entity.service), active=False, url=service_detail_url)
        text += breadcrumb_item(_("Workflow") + ": " + str(entity), active=True, url=workflow_detail_url)
    text += footer()
    return mark_safe(text)
