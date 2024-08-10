from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils.translation import gettext_lazy as _

from workflows.views import TenantMixin

from .models import Domain, Requirement, Constraint

class DomainList(TenantMixin, ListView):
    model = Domain
    template_name = 'compliances/domain-list.html'
    context_object_name = 'domains'

class DomainDetail(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-detail.html'
    context_object_name = 'domain'

class DomainBoard(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-board.html'
    context_object_name = 'domain'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain_id = self.kwargs['pk']
        context['columns'] = [
            {
                'name': _("New"),
                'status': 'new',
            },
            {
                'name': _("Implemented"),
                'status': 'implemented',
            },
            {
                'name': _("Non-compliant"),
                'status': 'non-compliant',
            },
            {
                'name': _("Failed"),
                'status': 'failed',
            },
            {
                'name': _("Compliant"),
                'status': 'compliant',
            },
            {
                'name': _("Audited"),
                'status': 'audited',
            },
        ]
        context['constraints'] = Constraint.objects.filter(requirement__section__domain_id=domain_id).select_related('requirement', 'requirement__section', 'requirement__section__domain')
        return context
