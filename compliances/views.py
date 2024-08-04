
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from workflows.views import TenantMixin

from .models import Domain, Requirement

class DomainList(TenantMixin, ListView):
    model = Domain
    template_name = 'compliances/domain-list.html'
    context_object_name = 'domains'

class DomainDetail(TenantMixin, DetailView):
    model = Domain
    template_name = 'compliances/domain-detail.html'
    context_object_name = 'domain'
